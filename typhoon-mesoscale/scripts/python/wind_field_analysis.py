#!/usr/bin/env python3
"""
台风风场结构与非对称性分析

功能：
    - Holland (1980) 梯度风模型重建风场
    - 风场极坐标转换
    - 轴对称与非对称分量分解（傅里叶）
    - 最大风速半径(RMW)计算
    - 风圈四象限半径图

依赖：numpy, matplotlib, scipy, xarray(可选)

用法：
    python wind_field_analysis.py --pmin 935 --vmax 130 --rmax 25 --lat 22 --reconstruct wind.png
    python wind_field_analysis.py --field wind_data.nc --decompose decompose.png
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


def holland_gradient_wind(pmin, pn, vmax, rmax, lat, r_array):
    """
    Holland (1980) 梯度风模型

    参数：
        pmin: 中心最低气压 (hPa)
        pn: 环境气压 (hPa)，通常 1010-1013
        vmax: 最大风速 (m/s)
        rmax: 最大风速半径 (km)
        lat: 纬度（用于科氏参数）
        r_array: 半径数组 (km)

    返回：各半径处的梯度风速 (m/s)
    """
    rho = 1.15  # 空气密度 (kg/m^3)
    omega = 7.292e-5  # 地球自转角速度
    f = 2 * omega * np.abs(np.sin(np.radians(lat)))  # 科氏参数

    # Holland B 参数估计 (Willoughby & Rahn 2004)
    B = (vmax**2 * rho * np.e) / (100 * (pn - pmin))
    B = np.clip(B, 1.0, 2.5)

    # 转换为 SI 单位
    r_m = r_array * 1000  # m
    rmax_m = rmax * 1000  # m
    dp_pa = (pn - pmin) * 100  # Pa

    # Holland 梯度风方程
    term1 = (B / rho) * (rmax_m / r_m)**B * dp_pa * np.exp(-(rmax_m / r_m)**B)
    term2 = (r_m * f / 2)**2
    vg = np.sqrt(term1 + term2) - r_m * f / 2

    return vg, B


def reconstruct_wind_field(pmin, pn, vmax, rmax, lat0, lon0,
                           vmax_ts_speed=0, vmax_ts_dir=0,
                           r_max=500, dr=5, daz=5):
    """
    重建台风完整风场（Holland + 移动效应）

    参数：
        pmin, pn, vmax, rmax, lat0, lon0: 台风参数
        vmax_ts_speed: 台风移速 (m/s)
        vmax_ts_dir: 台风移向 (度，0=北)
        r_max: 最大半径 (km)
        dr: 半径间隔 (km)
        daz: 方位角间隔 (度)

    返回：(r_bins, az_bins, wind_field) 极坐标风场
    """
    r_bins = np.arange(dr, r_max + dr, dr)
    az_bins = np.arange(0, 360, daz)
    R, AZ = np.meshgrid(r_bins, az_bins, indexing='ij')

    # Holland 梯度风
    vg, B = holland_gradient_wind(pmin, pn, vmax, rmax, lat0, r_bins)
    vg_2d = np.tile(vg[:, np.newaxis], (1, len(az_bins)))

    # 移动效应修正：北半球移动方向右侧风增强
    if vmax_ts_speed > 0:
        az_rad = np.radians(az_bins)
        # 移动方向方位角
        move_az = np.radians(vmax_ts_dir)
        # 移动方向右侧 = move_az + 90 (北半球)
        cos_diff = np.cos(az_rad - move_az)
        # 移动速度的切向投影
        ts_component = vmax_ts_speed * np.cos(az_rad - move_az)
        wind_field = vg_2d + ts_component[np.newaxis, :]
    else:
        wind_field = vg_2d

    return r_bins, az_bins, wind_field, B


def plot_reconstructed_field(r_bins, az_bins, wind_field, storm_name='',
                              output_path='wind_field.png'):
    """
    绘制极坐标风场图
    """
    R, AZ = np.meshgrid(r_bins, az_bins, indexing='ij')
    THETA = np.radians(AZ)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7),
                              subplot_kw={'projection': 'polar'})

    # 左图：极坐标
    ax = axes[0]
    cf = ax.pcolormesh(THETA, R, wind_field, cmap='jet', shading='auto')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title('Wind Field (Polar)', fontsize=12)
    plt.colorbar(cf, ax=ax, label='Wind Speed (m/s)')

    # 右图：方位角平均廓线
    ax2 = axes[1]
    az_mean = np.mean(wind_field, axis=1)
    ax2.plot(r_bins, az_mean, 'b-', linewidth=2)
    rmax_idx = np.argmax(az_mean)
    ax2.axvline(x=r_bins[rmax_idx], color='r', linestyle='--',
                label=f'RMW = {r_bins[rmax_idx]:.0f} km')
    ax2.set_xlabel('Radius (km)', fontsize=12)
    ax2.set_ylabel('Wind Speed (m/s)', fontsize=12)
    ax2.set_title('Azimuthal Mean Wind Profile', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.suptitle(f'Typhoon {storm_name} Wind Field Reconstruction',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"风场图已保存: {output_path}")


def azimuthal_decompose(field_2d, az_bins):
    """
    方位角傅里叶分解

    参数：
        field_2d: (n_r, n_az) 极坐标场
        az_bins: 方位角数组 (度)

    返回：dict 含各波数分量
    """
    az_rad = np.radians(az_bins)
    n_az = len(az_bins)

    from numpy.fft import fft
    fft_coeffs = fft(field_2d, axis=1)

    result = {
        'symmetric': np.real(fft_coeffs[:, 0]) / n_az,
        'wave1_amp': np.abs(fft_coeffs[:, 1]) / n_az * 2,
        'wave1_phase': np.angle(fft_coeffs[:, 1]),
        'wave2_amp': np.abs(fft_coeffs[:, 2]) / n_az * 2,
        'wave2_phase': np.angle(fft_coeffs[:, 2]),
        'total_asym': field_2d - np.real(fft_coeffs[:, 0:1]) / n_az,
    }

    result['wave1_direction'] = np.degrees(result['wave1_phase']) % 360
    return result


def plot_wind_radii(radii_dict, output_path='wind_radii.png'):
    """
    绘制风圈四象限半径图

    参数：
        radii_dict: {'34kt': {'NE':r,'SE':r,'SW':r,'NW':r}, '50kt':..., '64kt':...}
    """
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    quadrants = ['NE', 'SE', 'SW', 'NW']
    angles = [45, 135, 225, 315]

    for (level, radii), color in zip(radii_dict.items(), colors):
        r_vals = [radii[q] for q in quadrants]
        theta = np.radians(angles)
        theta_closed = np.append(theta, theta[0])
        r_closed = np.append(r_vals, r_vals[0])
        ax.plot(theta_closed, r_closed, 'o-', color=color, linewidth=2,
                markersize=6, label=f'{level} kt')

    ax.set_xticks(np.radians(angles))
    ax.set_xticklabels(quadrants)
    ax.set_xlabel('Radius (km)')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.set_title('Wind Radii by Quadrant', fontsize=14, pad=20)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"风圈图已保存: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风风场分析')
    parser.add_argument('--pmin', type=float, help='中心气压 (hPa)')
    parser.add_argument('--vmax', type=float, help='最大风速 (m/s)')
    parser.add_argument('--rmax', type=float, help='最大风速半径 (km)')
    parser.add_argument('--pn', type=float, default=1010, help='环境气压 (hPa)')
    parser.add_argument('--lat', type=float, default=20, help='台风纬度')
    parser.add_argument('--lon', type=float, default=130, help='台风经度')
    parser.add_argument('--ts-speed', type=float, default=0, help='移速 (m/s)')
    parser.add_argument('--ts-dir', type=float, default=0, help='移向 (度)')
    parser.add_argument('--name', default='', help='台风名称')
    parser.add_argument('--output', default='wind_field.png', help='输出路径')
    parser.add_argument('--reconstruct', action='store_true',
                        help='重建风场')
    args = parser.parse_args()

    if args.reconstruct and args.pmin and args.vmax and args.rmax:
        r_bins, az_bins, wind, B = reconstruct_wind_field(
            args.pmin, args.pn, args.vmax, args.rmax,
            args.lat, args.lon,
            args.ts_speed, args.ts_dir
        )
        print(f"Holland B 参数: {B:.2f}")
        print(f"最大风速半径(RMW): {r_bins[np.argmax(np.mean(wind, axis=1))]:.0f} km")
        plot_reconstructed_field(r_bins, az_bins, wind, args.name, args.output)
