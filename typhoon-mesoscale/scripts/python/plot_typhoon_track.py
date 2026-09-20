#!/usr/bin/env python3
"""
绘制台风路径图

功能：
    - 单个台风路径图（按强度/时间着色）
    - 多路径叠加
    - 路径密度图

依赖：cartopy, matplotlib, numpy, pandas, xarray

用法：
    python plot_typhoon_track.py --ibtracs ./data/IBTrACS.WP.nc --name HATO --output track.png
    python plot_typhoon_track.py --csv track_data.csv --output track.png
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr


def plot_single_track(df, storm_name='', output_path='track.png',
                      intensity_col='vmax', extent=None):
    """
    绘制单个台风路径图（按强度着色）

    参数：
        df: 路径数据，含 lat, lon, vmax（或指定 intensity_col）列
        storm_name: 台风名称（用于标题）
        output_path: 输出图片路径
        intensity_col: 强度列名
        extent: 地图范围 [lon_min, lon_max, lat_min, lat_max]
    """
    fig, ax = plt.subplots(figsize=(12, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()})

    ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=1)
    ax.add_feature(cfeature.OCEAN, facecolor='#f0f8ff', zorder=0)
    ax.coastlines(resolution='50m', linewidth=0.8, zorder=2)

    if extent:
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    else:
        margin = 10
        ax.set_extent([
            df['lon'].min() - margin, df['lon'].max() + margin,
            df['lat'].min() - margin, df['lat'].max() + margin
        ], crs=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    gl.top_labels = gl.right_labels = False

    intensity = df[intensity_col].values
    scatter = ax.scatter(df['lon'], df['lat'], c=intensity,
                         cmap='YlOrRd', s=50, edgecolors='black',
                         linewidth=0.5, transform=ccrs.PlateCarree(),
                         zorder=5)

    ax.plot(df['lon'], df['lat'], 'k-', linewidth=1.2,
            transform=ccrs.PlateCarree(), zorder=4)

    start = df.iloc[0]
    end = df.iloc[-1]
    ax.plot(start['lon'], start['lat'], 'go', markersize=10,
            transform=ccrs.PlateCarree(), label='Genesis', zorder=6)
    ax.plot(end['lon'], end['lat'], 'rs', markersize=10,
            transform=ccrs.PlateCarree(), label='Dissipation', zorder=6)

    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical',
                        shrink=0.8, pad=0.05)
    cbar.set_label('Maximum Wind Speed (kt)')

    ax.set_title(f'Typhoon {storm_name} Track', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"路径图已保存: {output_path}")


def plot_multi_tracks(df_list, labels, output_path='multi_track.png',
                      extent=None, basin='WP'):
    """
    绘制多路径叠加图

    参数：
        df_list: DataFrame 列表，每个含 lat, lon 列
        labels: 对应的名称列表
        output_path: 输出路径
        extent: 地图范围
    """
    fig, ax = plt.subplots(figsize=(14, 10),
                           subplot_kw={'projection': ccrs.PlateCarree()})
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.coastlines(resolution='50m')

    if extent:
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = gl.right_labels = False

    colors = plt.cm.tab10(np.linspace(0, 1, len(df_list)))
    for df, label, color in zip(df_list, labels, colors):
        ax.plot(df['lon'], df['lat'], '-', color=color, linewidth=1.5,
                label=label, transform=ccrs.PlateCarree())
        ax.plot(df['lon'].iloc[0], df['lat'].iloc[0], 'o',
                color=color, markersize=6, transform=ccrs.PlateCarree())

    ax.legend(loc='upper left', fontsize=8)
    ax.set_title('Typhoon Tracks Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"多路径图已保存: {output_path}")


def plot_track_density(df, output_path='density.png',
                       resolution=1, extent=None):
    """
    绘制路径密度图

    参数：
        df: 路径数据，含 lat, lon 列（多个台风）
        resolution: 网格分辨率（度）
        extent: 地图范围 [lon_min, lon_max, lat_min, lat_max]
    """
    from scipy.stats import binned_statistic_2d

    if extent:
        lon_min, lon_max, lat_min, lat_max = extent
    else:
        lon_min = max(df['lon'].min() - 5, 0)
        lon_max = min(df['lon'].max() + 5, 360)
        lat_min = max(df['lat'].min() - 5, -30)
        lat_max = min(df['lat'].max() + 5, 60)

    lat_bins = np.arange(lat_min, lat_max + resolution, resolution)
    lon_bins = np.arange(lon_min, lon_max + resolution, resolution)

    density, _, _, _ = binned_statistic_2d(
        df['lat'], df['lon'], df['lat'],
        statistic='count', bins=[lat_bins, lon_bins]
    )

    n_years = df['time'].dt.year.nunique() if 'time' in df.columns else 1
    density_per_year = density / n_years

    fig, ax = plt.subplots(figsize=(14, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines(resolution='50m')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')

    if extent:
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    lon_centers = (lon_bins[:-1] + lon_bins[1:]) / 2
    lat_centers = (lat_bins[:-1] + lat_bins[1:]) / 2

    cf = ax.contourf(lon_centers, lat_centers, density_per_year,
                     levels=np.linspace(0, density_per_year.max(), 15),
                     cmap='YlOrRd', transform=ccrs.PlateCarree())
    ax.contour(lon_centers, lat_centers, density_per_year,
               levels=[1, 3, 5, 10], colors='k', linewidths=0.5,
               transform=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = gl.right_labels = False

    plt.colorbar(cf, ax=ax, label='Track density per year per grid cell',
                 shrink=0.8)
    ax.set_title('Typhoon Track Density', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"路径密度图已保存: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='绘制台风路径图')
    parser.add_argument('--ibtracs', help='IBTrACS NetCDF 文件路径')
    parser.add_argument('--csv', help='路径数据 CSV 文件路径')
    parser.add_argument('--name', help='台风名称')
    parser.add_argument('--output', default='track.png', help='输出图片路径')
    parser.add_argument('--extent', nargs=4, type=float,
                        help='地图范围 lon_min lon_max lat_min lat_max')
    parser.add_argument('--density', action='store_true',
                        help='绘制路径密度图而非单路径')
    args = parser.parse_args()

    if args.ibtracs:
        ds = xr.open_dataset(args.ibtracs)
        if args.name:
            from download_track_data import load_ibtracs_storm
            df = load_ibtracs_storm(args.ibtracs, storm_name=args.name)
            plot_single_track(df, args.name, args.output,
                              extent=args.extent)
        elif args.density:
            lat = ds['lat'].values.ravel()
            lon = ds['lon'].values.ravel()
            time = ds['time'].values.ravel()
            mask = ~np.isnan(lat) & ~np.isnan(lon)
            df = pd.DataFrame({'lat': lat[mask], 'lon': lon[mask],
                               'time': pd.to_datetime(time[mask])})
            plot_track_density(df, args.output, extent=args.extent)
    elif args.csv:
        df = pd.read_csv(args.csv)
        if args.density:
            plot_track_density(df, args.output, extent=args.extent)
        else:
            name = args.name or ''
            plot_single_track(df, name, args.output, extent=args.extent)
