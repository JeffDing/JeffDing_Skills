#!/usr/bin/env python3
"""
台风环境场诊断

功能：
    - ERA5 数据读取
    - SST 空间分布与冷尾迹分析
    - 垂直风切变计算 (200-850 hPa)
    - 引导气流计算
    - 中层湿度诊断
    - 高空辐散分析
    - 环境场综合诊断图

依赖：xarray, numpy, matplotlib, cartopy, metpy

用法：
    python environment_diagnosis.py --era5 era5_data.nc --track track.csv --output env.png
"""

import argparse
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def area_mean_around_center(field_2d, lats, lons, center_lat, center_lon,
                            radius_deg=5):
    """
    在台风中心周围做面积平均（去除涡旋本身影响）
    """
    mask = ((lats >= center_lat - radius_deg) & (lats <= center_lat + radius_deg) &
            (lons >= center_lon - radius_deg) & (lons <= center_lon + radius_deg))
    if field_2d.ndim == 2:
        return np.nanmean(field_2d[mask])
    elif field_2d.ndim == 3:
        result = np.array([np.nanmean(field_2d[k][mask]) for k in range(field_2d.shape[0])])
        return result


def calc_vertical_shear(u200, v200, u850, v850, lats, lons,
                        center_lat, center_lon, radius_deg=5):
    """
    计算 200-850 hPa 深层风切变

    参数：
        u200, v200: 200hPa U/V 风场
        u850, v850: 850hPa U/V 风场
        center_lat, center_lon: 台风中心
        radius_deg: 环境平均半径

    返回：(切变大小 m/s, 切变方向 度)
    """
    u200_env = area_mean_around_center(u200, lats, lons,
                                        center_lat, center_lon, radius_deg)
    v200_env = area_mean_around_center(v200, lats, lons,
                                        center_lat, center_lon, radius_deg)
    u850_env = area_mean_around_center(u850, lats, lons,
                                        center_lat, center_lon, radius_deg)
    v850_env = area_mean_around_center(v850, lats, lons,
                                        center_lat, center_lon, radius_deg)

    du = u200_env - u850_env
    dv = v200_env - v850_env
    shear_mag = np.sqrt(du**2 + dv**2)
    shear_dir = (np.degrees(np.arctan2(-du, -dv)) + 360) % 360

    return shear_mag, shear_dir


def calc_steering_flow(u_levels, v_levels, levels, storm_intensity='TS'):
    """
    计算深层平均引导气流

    参数：
        u_levels, v_levels: 各层风场 (多层)
        levels: 气压层数组 (hPa)
        storm_intensity: 台风强度等级 ('TD'|'TS'|'TY'|'ST')

    返回：(u_steer, v_steer, speed, direction)
    """
    layer_ranges = {
        'TD': (850, 700),
        'TS': (850, 500),
        'TY': (850, 300),
        'ST': (700, 200),
    }
    p_low, p_high = layer_ranges.get(storm_intensity, (850, 500))

    mask = (levels >= p_high) & (levels <= p_low)
    if mask.sum() == 0:
        return None, None, None, None

    weights = np.array(levels)[mask] / np.sum(np.array(levels)[mask])
    u_steer = np.average(np.array(u_levels)[mask], weights=weights)
    v_steer = np.average(np.array(v_levels)[mask], weights=weights)

    speed = np.sqrt(u_steer**2 + v_steer**2)
    direction = (np.degrees(np.arctan2(-u_steer, -v_steer)) + 360) % 360

    return u_steer, v_steer, speed, direction


def plot_sst(sst_field, lats, lons, storm_lat, storm_lon,
             storm_name='', output_path='sst.png'):
    """
    绘制 SST 空间分布图
    """
    fig, ax = plt.subplots(figsize=(12, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines(resolution='50m')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.gridlines(draw_labels=True)

    cf = ax.contourf(lons, lats, sst_field, levels=20,
                     cmap='RdYlBu_r', transform=ccrs.PlateCarree())
    ax.contour(lons, lats, sst_field, levels=[26.5, 28, 29],
               colors='k', linewidths=1.5, transform=ccrs.PlateCarree())
    ax.plot(storm_lon, storm_lat, 'k*', markersize=15,
            transform=ccrs.PlateCarree())

    plt.colorbar(cf, label='SST (°C)', shrink=0.8)
    ax.set_title(f'Typhoon {storm_name} - SST Environment',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"SST 图已保存: {output_path}")


def plot_shear_field(u200, v200, u850, v850, lats, lons,
                      storm_lat, storm_lon, storm_name='',
                      output_path='shear.png'):
    """
    绘制环境风切变场
    """
    shear_u = u200 - u850
    shear_v = v200 - v850

    fig, ax = plt.subplots(figsize=(12, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines(resolution='50m')
    ax.gridlines(draw_labels=True)

    mag = np.sqrt(shear_u**2 + shear_v**2)
    cf = ax.contourf(lons, lats, mag, levels=np.linspace(0, 30, 16),
                     cmap='YlOrRd', transform=ccrs.PlateCarree())

    # 风矢量
    skip = (slice(None, None, 5), slice(None, None, 5))
    ax.quiver(lons[skip[1]], lats[skip[0]],
              shear_u[skip], shear_v[skip],
              transform=ccrs.PlateCarree(), scale=500, width=0.003)

    ax.plot(storm_lon, storm_lat, 'k*', markersize=15,
            transform=ccrs.PlateCarree())

    plt.colorbar(cf, label='Deep Layer Shear (m/s)', shrink=0.8)
    ax.set_title(f'Typhoon {storm_name} - 200-850 hPa Wind Shear',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"切变场图已保存: {output_path}")


def comprehensive_diagnosis(era5_path, track_row, output_path='env_diag.png',
                             storm_name=''):
    """
    环境场综合诊断图（4面板）

    参数：
        era5_path: ERA5 NetCDF 文件路径
        track_row: 含 lat, lon, vmax, time 的 Series
    """
    ds = xr.open_dataset(era5_path)
    lats = ds['latitude'].values if 'latitude' in ds else ds['lat'].values
    lons = ds['longitude'].values if 'longitude' in ds else ds['lon'].values
    clat, clon = track_row['lat'], track_row['lon']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12),
                              subplot_kw={'projection': ccrs.PlateCarree()})

    for ax in axes.flat:
        ax.coastlines(resolution='50m')
        ax.gridlines(draw_labels=True)

    extent = [clon-15, clon+15, clat-15, clat+15]
    for ax in axes.flat:
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    # 面板1: SST
    if 'sst' in ds:
        sst = ds['sst'].isel(time=0).values
        ax = axes[0, 0]
        ax.contourf(lons, lats, sst, levels=20, cmap='RdYlBu_r',
                    transform=ccrs.PlateCarree())
        ax.set_title('SST')

    # 面板2: 850hPa 风场+涡度
    if 'u' in ds and 'v' in ds:
        u850 = ds['u'].sel(isobaricInhPa=850).isel(time=0).values
        v850 = ds['v'].sel(isobaricInhPa=850).isel(time=0).values
        ax = axes[0, 1]
        skip = 3
        ax.quiver(lons[::skip], lats[::skip],
                  u850[::skip, ::skip], v850[::skip, ::skip],
                  transform=ccrs.PlateCarree(), scale=300)
        ax.set_title('850 hPa Wind')

    # 面板3: 200hPa 风场（高空辐散）
    if 'u' in ds and 'v' in ds:
        u200 = ds['u'].sel(isobaricInhPa=200).isel(time=0).values
        v200 = ds['v'].sel(isobaricInhPa=200).isel(time=0).values
        ax = axes[1, 0]
        skip = 3
        ax.quiver(lons[::skip], lats[::skip],
                  u200[::skip, ::skip], v200[::skip, ::skip],
                  transform=ccrs.PlateCarree(), scale=300)
        ax.set_title('200 hPa Wind')

    # 面板4: 中层湿度
    if 'r' in ds:
        rh700 = ds['r'].sel(isobaricInhPa=700).isel(time=0).values
        ax = axes[1, 1]
        ax.contourf(lons, lats, rh700, levels=20, cmap='YlGnBu',
                    transform=ccrs.PlateCarree())
        ax.set_title('700 hPa Relative Humidity')

    for ax in axes.flat:
        ax.plot(clon, clat, 'k*', markersize=15,
                transform=ccrs.PlateCarree())

    plt.suptitle(f'Typhoon {storm_name} Environment Diagnosis',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"环境场综合诊断图已保存: {output_path}")


def ri_favorable_check(sst, shear, rh_mid, pot, land_dist, speed):
    """
    RI 有利条件综合判据

    返回各条件满足情况和总体评分
    """
    conditions = {
        'warm_sst (SST > 28.5°C)': sst > 28.5,
        'weak_shear (< 8 m/s)': shear < 8,
        'moist_mid (RH > 60%)': rh_mid > 60,
        'high_pot (Pot > 20 kt)': pot > 20,
        'far_land (> 200 km)': land_dist > 200,
        'slow_move (< 5 m/s)': speed < 5,
    }
    n_met = sum(conditions.values())
    return conditions, n_met


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风环境场诊断')
    parser.add_argument('--era5', required=True, help='ERA5 NetCDF 文件')
    parser.add_argument('--track', required=True, help='路径数据 CSV')
    parser.add_argument('--name', default='', help='台风名称')
    parser.add_argument('--output', default='env.png', help='输出路径')
    parser.add_argument('--comprehensive', action='store_true',
                        help='综合诊断图')
    args = parser.parse_args()

    track = pd.read_csv(args.track)
    track['time'] = pd.to_datetime(track['time'])

    ds = xr.open_dataset(args.era5)
    lats = ds['latitude'].values if 'latitude' in ds else ds['lat'].values
    lons = ds['longitude'].values if 'longitude' in ds else ds['lon'].values

    t0 = ds['time'].values[0] if 'time' in ds else track['time'].iloc[0]
    nearest = track.iloc[(track['time'] - pd.Timestamp(t0)).abs().argsort()[0]]
    clat, clon = nearest['lat'], nearest['lon']

    if 'sst' in ds:
        sst = ds['sst'].isel(time=0).values
        plot_sst(sst, lats, lons, clat, clon, args.name,
                 args.output.replace('.png', '_sst.png'))

    if 'u' in ds and 'v' in ds:
        u200 = ds['u'].sel(isobaricInhPa=200).isel(time=0).values
        v200 = ds['v'].sel(isobaricInhPa=200).isel(time=0).values
        u850 = ds['u'].sel(isobaricInhPa=850).isel(time=0).values
        v850 = ds['v'].sel(isobaricInhPa=850).isel(time=0).values

        shear_mag, shear_dir = calc_vertical_shear(
            u200, v200, u850, v850, lats, lons, clat, clon)
        print(f"深层切变: {shear_mag:.1f} m/s, 方向: {shear_dir:.0f}°")

        if shear_mag < 8:
            print("  → 弱切变，有利于台风增强")
        elif shear_mag < 15:
            print("  → 中等切变，增强减缓")
        else:
            print("  → 强切变，台风结构可能受损")

        plot_shear_field(u200, v200, u850, v850, lats, lons,
                         clat, clon, args.name,
                         args.output.replace('.png', '_shear.png'))

    if args.comprehensive:
        comprehensive_diagnosis(args.era5, nearest, args.output,
                                args.name)
