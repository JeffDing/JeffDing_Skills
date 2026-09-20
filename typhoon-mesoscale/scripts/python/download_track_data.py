#!/usr/bin/env python3
"""
下载台风最佳路径数据

支持 IBTrACS（全球）、CMA、JMA、JTWC 数据下载。
使用前请确保已安装 requests, pandas 库。

用法：
    python download_track_data.py --source ibtracs --output ./data/
    python download_track_data.py --source ibtracs --basin WP --output ./data/
    python download_track_data.py --source cmabst --output ./data/
"""

import argparse
import os
import requests
import pandas as pd
import xarray as xr


IBTRACS_URLS = {
    'all_nc': 'https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/code/IBTrACS.ALL.v04r00.nc',
    'all_csv': 'https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/code/ibtracs.ALL.list.v04r00.csv',
    'active_nc': 'https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/current/IBTrACS.active.v04r00.nc',
}

CMA_URL = 'http://www.typhoon.org.cn/data/best/%dBST.txt'


def download_ibtracs(output_dir, format='nc', basin=None):
    """
    下载 IBTrACS 最佳路径数据

    参数：
        output_dir: 输出目录
        format: 'nc' (NetCDF) 或 'csv'
        basin: 可选海域筛选，如 'WP'（西北太平洋）、'NA'（北大西洋）
               None 表示全球
    """
    os.makedirs(output_dir, exist_ok=True)

    if format == 'nc':
        url = IBTRACS_URLS['all_nc']
        filepath = os.path.join(output_dir, 'IBTrACS.ALL.v04r00.nc')
    else:
        url = IBTRACS_URLS['all_csv']
        filepath = os.path.join(output_dir, 'ibtracs.ALL.list.v04r00.csv')

    print(f"正在下载 IBTrACS 数据...")
    print(f"URL: {url}")
    print(f"保存到: {filepath}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"下载完成: {filepath}")

    if basin and format == 'nc':
        filter_by_basin(filepath, basin, output_dir)

    return filepath


def filter_by_basin(nc_path, basin, output_dir):
    """
    按海域筛选 IBTrACS 数据并保存

    参数：
        nc_path: NetCDF 文件路径
        basin: 海域代码 (WP, NA, EP, NI, SI, SP, SA)
        output_dir: 输出目录
    """
    print(f"筛选海域: {basin}")
    ds = xr.open_dataset(nc_path)

    basin_map = {
        'WP': 'WP - Western North Pacific',
        'NA': 'NA - North Atlantic',
        'EP': 'EP - Eastern Pacific',
        'NI': 'NI - North Indian',
        'SI': 'SI - South Indian',
        'SP': 'SP - South Pacific',
        'SA': 'SA - South Atlantic',
    }

    ds_basin = ds.where(ds['basin'] == basin, drop=True)
    out_path = os.path.join(output_dir, f'IBTrACS.{basin}.nc')
    ds_basin.to_netcdf(out_path)
    print(f"筛选后数据保存到: {out_path}")
    print(f"该海域台风数: {ds_basin.dims['storm']}")
    return out_path


def download_cma_bst(year_start, year_end, output_dir):
    """
    下载 CMA-STI 最佳路径数据（逐年）

    参数：
        year_start: 起始年
        year_end: 结束年
        output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    all_data = []

    for year in range(year_start, year_end + 1):
        url = CMA_URL % year
        print(f"下载 CMA {year} 年数据...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                filepath = os.path.join(output_dir, f'CMA_BST_{year}.txt')
                with open(filepath, 'w') as f:
                    f.write(response.text)
                all_data.append(filepath)
            else:
                print(f"  {year} 年数据不可用 (HTTP {response.status_code})")
        except Exception as e:
            print(f"  {year} 年下载失败: {e}")

    if all_data:
        combined_path = os.path.join(output_dir, 'CMA_BST_combined.txt')
        with open(combined_path, 'w') as outfile:
            for fpath in all_data:
                with open(fpath) as infile:
                    outfile.write(infile.read())
        print(f"合并数据保存到: {combined_path}")
        return combined_path
    return None


def load_ibtracs_storm(nc_path, storm_name=None, storm_sid=None):
    """
    从 IBTrACS NetCDF 中提取单个台风数据

    参数：
        nc_path: NetCDF 文件路径
        storm_name: 台风名称（如 'HATO'）
        storm_sid: IBTrACS 风暴 ID

    返回：pandas DataFrame
    """
    ds = xr.open_dataset(nc_path)

    if storm_sid:
        storm = ds.sel(storm=storm_sid)
    elif storm_name:
        mask = ds['name'].values == storm_name.upper().ljust(8)
        if mask.sum() == 0:
            raise ValueError(f"未找到台风: {storm_name}")
        storm = ds.isel(storm=np.where(mask)[0][0])
    else:
        raise ValueError("请提供 storm_name 或 storm_sid")

    df = pd.DataFrame({
        'time': pd.to_datetime(storm['time'].values),
        'lat': storm['lat'].values,
        'lon': storm['lon'].values,
        'vmax': storm['wmo_wind'].values,
        'pres': storm['wmo_pres'].values,
        'name': storm['name'].values,
        'sid': storm['sid'].values,
    })
    df = df.dropna(subset=['lat', 'lon'])
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='下载台风最佳路径数据')
    parser.add_argument('--source', choices=['ibtracs', 'cmabst'],
                        default='ibtracs', help='数据源')
    parser.add_argument('--format', choices=['nc', 'csv'], default='nc',
                        help='IBTrACS 格式')
    parser.add_argument('--basin', default=None,
                        help='海域筛选 (WP/NA/EP/NI/SI/SP/SA)')
    parser.add_argument('--year-start', type=int, default=1949,
                        help='CMA 起始年')
    parser.add_argument('--year-end', type=int, default=2023,
                        help='CMA 结束年')
    parser.add_argument('--output', default='./data/', help='输出目录')
    args = parser.parse_args()

    if args.source == 'ibtracs':
        download_ibtracs(args.output, args.format, args.basin)
    elif args.source == 'cmabst':
        download_cma_bst(args.year_start, args.year_end, args.output)
