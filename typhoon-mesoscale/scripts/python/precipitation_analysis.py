#!/usr/bin/env python3
"""
台风降水分析

功能：
    - GPM IMERG 降水数据读取与裁剪
    - 降水空间分布图
    - 极坐标降水分布
    - 半径-时间 Hovmöller 图
    - 方位角-时间 Hovmöller 图
    - 降水非对称性傅里叶分解
    - 累积降水时间序列

依赖：xarray, numpy, matplotlib, cartopy, scipy

用法：
    python precipitation_analysis.py --imerg imerg_data.nc --track track.csv --output precip.png
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr


def load_imerg(filepath):
    """
    读取 GPM IMERG 数据
    """
    ds = xr.open_dataset(filepath)
    precip = ds['precipitationCal'] if 'precipitationCal' in ds else ds['precipitation']
    return precip, ds['lat'].values, ds['lon'].values, ds['time'].values


def haversine(lat1, lon1, lat2, lon2):
    """
    计算两点间大圆距离 (km)
    """
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def calc_bearing(lat1, lon1, lat2, lon2):
    """
    计算从点1到点2的方位角 (0=北, 顺时针)
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1)*np.sin(lat2) - np.sin(lat1)*np.cos(lat2)*np.cos(dlon)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def to_polar(precip_2d, lats, lons, center_lat, center_lon,
             r_max=500, dr=10, daz=5):
    """
    将经纬度降水场转换为极坐标（以台风中心为原点）

    参数：
        precip_2d: (n_lat, n_lon) 降水场
        lats, lons: 经纬度数组
        center_lat, center_lon: 台风中心
        r_max: 最大半径 (km)
        dr: 半径间隔 (km)
        daz: 方位角间隔 (度)

    返回：(r_bins, az_bins, polar_field)
    """
    r_bins = np.arange(0, r_max + dr, dr)
    az_bins = np.arange(0, 360, daz)
    polar_field = np.full((len(r_bins), len(az_bins)), np.nan)

    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            dist = haversine(center_lat, center_lon, lat, lon)
            if dist > r_max:
                continue
            bearing = calc_bearing(center_lat, center_lon, lat, lon)
            ri = np.digitize(dist, r_bins) - 1
            ai = np.digitize(bearing, az_bins) - 1
            ri = np.clip(ri, 0, len(r_bins)-1)
            ai = np.clip(ai, 0, len(az_bins)-1)
            if np.isnan(polar_field[ri, ai]):
                polar_field[ri, ai] = precip_2d[i, j]
            else:
                polar_field[ri, ai] = np.nanmean([polar_field[ri, ai], precip_2d[i, j]])

    polar_field = np.where(np.isnan(polar_field), 0, polar_field)
    return r_bins, az_bins, polar_field


def plot_precip_spatial(precip_2d, lats, lons, storm_lat, storm_lon,
                         storm_name='', output_path='precip_spatial.png',
                         accumulation_label='mm'):
    """
    绘制降水空间分布图
    """
    fig, ax = plt.subplots(figsize=(12, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines(resolution='50m')
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.gridlines(draw_labels=True)

    levels = [0.1, 1, 5, 10, 25, 50, 100, 200, 300, 500]
    colors = ['#ffffff', '#a6f2a6', '#00b300', '#01ffff', '#0000ff',
              '#ffff00', '#ff0000', '#9c009c', '#000000']
    cf = ax.contourf(lons, lats, precip_2d, levels=levels, colors=colors,
                     extend='max', transform=ccrs.PlateCarree())
    plt.colorbar(cf, label=f'Precipitation ({accumulation_label})',
                 shrink=0.8, pad=0.05)

    ax.plot(storm_lon, storm_lat, 'k*', markersize=15,
            transform=ccrs.PlateCarree(), label='TC Center')
    ax.legend(loc='upper left')

    ax.set_title(f'Typhoon {storm_name} Precipitation Distribution',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"降水空间分布图已保存: {output_path}")


def plot_hovmoller_radius(polar_series_list, r_bins, times,
                           output_path='hovmoller_r.png'):
    """
    绘制半径-时间 Hovmöller 图

    参数：
        polar_series_list: 各时刻极坐标降水场列表
        r_bins: 半径数组
        times: 时间数组
    """
    az_means = [np.nanmean(p, axis=1) for p in polar_series_list]
    hov = np.array(az_means).T  # (n_r, n_t)

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.pcolormesh(times, r_bins, hov, cmap='jet', vmin=0,
                       vmax=np.nanpercentile(hov, 95))
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Radius (km)', fontsize=12)
    ax.set_title('Radius-Time Hovmöller (Azimuthal Mean Precipitation)',
                 fontsize=14, fontweight='bold')
    plt.colorbar(im, label='Precipitation (mm/hr)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"半径-时间 Hovmöller 图已保存: {output_path}")


def plot_hovmoller_azimuth(polar_series_list, az_bins, r_bins, times,
                            r_range=(50, 200),
                            output_path='hovmoller_az.png'):
    """
    绘制方位角-时间 Hovmöller 图
    """
    r_mask = (r_bins >= r_range[0]) & (r_bins <= r_range[1])
    r_means = [np.nanmean(p[r_mask, :], axis=0) for p in polar_series_list]
    hov = np.array(r_means).T  # (n_az, n_t)

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.pcolormesh(times, az_bins, hov, cmap='jet', vmin=0,
                       vmax=np.nanpercentile(hov, 95))
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Azimuth (°)', fontsize=12)
    ax.set_title(f'Azimuth-Time Hovmöller ({r_range[0]}-{r_range[1]} km)',
                 fontsize=14, fontweight='bold')
    plt.colorbar(im, label='Precipitation (mm/hr)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"方位角-时间 Hovmöller 图已保存: {output_path}")


def analyze_asymmetry(polar_field, r_bins, az_bins, r_range=(50, 200)):
    """
    降水非对称性傅里叶分解

    返回各波数分量的振幅和方向
    """
    r_mask = (r_bins >= r_range[0]) & (r_bins <= r_range[1])
    az_profile = np.nanmean(polar_field[r_mask, :], axis=0)

    from numpy.fft import fft
    coeffs = fft(az_profile)
    n = len(az_profile)

    return {
        'symmetric': np.real(coeffs[0]) / n,
        'wave1_amp': np.abs(coeffs[1]) / n * 2,
        'wave1_dir': (np.degrees(np.angle(coeffs[1])) % 360),
        'wave2_amp': np.abs(coeffs[2]) / n * 2,
        'wave2_dir': (np.degrees(np.angle(coeffs[2])) % 360),
        'asym_ratio': np.abs(coeffs[1]) / (np.abs(coeffs[0]) + 1e-10),
        'az_profile': az_profile,
    }


def plot_asymmetry(asym_result, az_bins, output_path='asymmetry.png'):
    """
    绘制非对称性分析图
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：方位角分布
    ax1 = axes[0]
    ax1.plot(az_bins, asym_result['az_profile'], 'b-', linewidth=2)
    ax1.axhline(y=asym_result['symmetric'], color='r', linestyle='--',
                label=f"Symmetric = {asym_result['symmetric']:.1f}")
    ax1.set_xlabel('Azimuth (°)', fontsize=12)
    ax1.set_ylabel('Precipitation (mm/hr)', fontsize=12)
    ax1.set_title('Azimuthal Distribution', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 右图：波数分量
    ax2 = axes[1]
    waves = ['Sym\n(k=0)', 'Waven1\n(k=1)', 'Waven2\n(k=2)']
    amps = [asym_result['symmetric'], asym_result['wave1_amp'],
            asym_result['wave2_amp']]
    ax2.bar(waves, amps, color=['green', 'orange', 'red'], alpha=0.7)
    ax2.set_ylabel('Amplitude (mm/hr)', fontsize=12)
    ax2.set_title('Fourier Components', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Precipitation Asymmetry Analysis',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"非对称性分析图已保存: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风降水分析')
    parser.add_argument('--imerg', help='IMERG NetCDF 文件路径')
    parser.add_argument('--track', help='路径数据 CSV 文件')
    parser.add_argument('--name', default='', help='台风名称')
    parser.add_argument('--output', default='precip.png', help='输出路径')
    parser.add_argument('--hovmoller', action='store_true',
                        help='绘制 Hovmöller 图')
    parser.add_argument('--asymmetry', action='store_true',
                        help='降水非对称性分析')
    args = parser.parse_args()

    if args.imerg and args.track:
        precip, lats, lons, times = load_imerg(args.imerg)
        track = pd.read_csv(args.track)
        track['time'] = pd.to_datetime(track['time'])

        # 取最近时刻的台风中心
        t0 = pd.to_datetime(times[0])
        nearest = track.iloc[(track['time'] - t0).abs().argsort()[0]]
        clat, clon = nearest['lat'], nearest['lon']

        # 空间分布图
        precip_2d = precip.isel(time=0).values
        plot_precip_spatial(precip_2d, lats, lons, clat, clon,
                            args.name, args.output)

        if args.hovmoller or args.asymmetry:
            r_bins, az_bins, polar = to_polar(precip_2d, lats, lons,
                                               clat, clon)
            if args.hovmoller:
                plot_hovmoller_radius([polar], r_bins, [t0],
                                      args.output.replace('.png', '_hov_r.png'))
                plot_hovmoller_azimuth([polar], az_bins, r_bins, [t0],
                                        output_path=args.output.replace('.png', '_hov_az.png'))
            if args.asymmetry:
                result = analyze_asymmetry(polar, r_bins, az_bins)
                print(f"波数0(轴对称): {result['symmetric']:.1f} mm/hr")
                print(f"波数1振幅: {result['wave1_amp']:.1f}, 方向: {result['wave1_dir']:.0f}°")
                print(f"波数2振幅: {result['wave2_amp']:.1f}")
                print(f"非对称比: {result['asym_ratio']:.2f}")
                plot_asymmetry(result, az_bins,
                               args.output.replace('.png', '_asym.png'))
