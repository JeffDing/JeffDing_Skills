#!/usr/bin/env python3
"""
台风气候统计与趋势分析

功能：
    - 年频数统计与可视化
    - 季节分布分析
    - 强度气候态统计
    - Mann-Kendall 趋势检验
    - 线性回归趋势
    - ENSO 遥相关分析
    - 生成潜势指数(GPI)计算

依赖：pandas, numpy, matplotlib, scipy, statsmodels

用法：
    python climate_statistics.py --ibtracs ./data/IBTrACS.WP.nc --output climate/
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, kendalltau, linregress
import xarray as xr


def load_best_track(ibtracs_path, basin=None, min_intensity=34):
    """
    加载最佳路径数据并提取年频数
    """
    ds = xr.open_dataset(ibtracs_path)
    if basin:
        ds = ds.where(ds['basin'] == basin, drop=True)

    all_times = ds['time'].values
    all_storms = ds['sid'].values
    all_winds = ds['wmo_wind'].values

    records = []
    for i in range(len(all_storms)):
        winds = all_winds[i]
        mask = ~np.isnan(winds)
        if mask.sum() == 0:
            continue
        vmax = np.nanmax(winds)
        if vmax < min_intensity:
            continue
        times = all_times[i][mask]
        genesis = pd.Timestamp(times[0])
        records.append({
            'sid': str(all_storms[i]),
            'year': genesis.year,
            'month': genesis.month,
            'vmax': vmax,
            'genesis_time': genesis,
        })
    return pd.DataFrame(records)


def annual_frequency(df, output_path='annual_freq.png'):
    """
    年频数统计与可视化
    """
    annual = df.groupby('year').size()

    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(annual.index, annual.values, color='steelblue', alpha=0.7)
    ax.axhline(y=annual.mean(), color='red', linestyle='--',
               label=f'Mean = {annual.mean():.1f}')
    ax.fill_between(annual.index,
                    annual.mean() - annual.std(),
                    annual.mean() + annual.std(),
                    alpha=0.15, color='red')

    # 5年滑动平均
    if len(annual) > 5:
        rolling = annual.rolling(window=5, center=True).mean()
        ax.plot(rolling.index, rolling.values, 'r-', linewidth=2,
                label='5-yr Running Mean')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of TCs', fontsize=12)
    ax.set_title('Annual Tropical Cyclone Frequency', fontsize=14,
                 fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"年频数图已保存: {output_path}")
    return annual


def seasonal_distribution(df, output_path='seasonal.png'):
    """
    季节分布分析
    """
    monthly = df.groupby('month').size()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(monthly.index, monthly.values, color='steelblue', alpha=0.7)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun',
                         'Jul','Aug','Sep','Oct','Nov','Dec'])
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Genesis', fontsize=12)
    ax.set_title('Seasonal Distribution of TC Genesis', fontsize=14,
                 fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"季节分布图已保存: {output_path}")


def intensity_climatology(df, output_path='intensity_clim.png'):
    """
    强度气候态统计
    """
    bins = [0, 34, 64, 83, 96, 113, 137, 200]
    labels = ['TD', 'TS', 'Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5']
    df['category'] = pd.cut(df['vmax'], bins=bins, labels=labels)

    annual_cat = df.groupby(['year', 'category']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))
    annual_cat.plot(kind='bar', stacked=True, ax=ax, width=0.8,
                    colormap='YlOrRd')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of TCs', fontsize=12)
    ax.set_title('Annual TC Frequency by Intensity Category',
                 fontsize=14, fontweight='bold')
    ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"强度气候态图已保存: {output_path}")


def mann_kendall(series):
    """
    Mann-Kendall 趋势检验

    返回：Z, p_value, sen_slope
    """
    n = len(series)
    S = 0
    for i in range(n-1):
        for j in range(i+1, n):
            S += np.sign(series[j] - series[i])

    var_S = n * (n - 1) * (2 * n + 5) / 18

    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0

    p_value = 2 * (1 - norm.cdf(abs(Z)))

    slopes = []
    for i in range(n-1):
        for j in range(i+1, n):
            slopes.append((series[j] - series[i]) / (j - i))
    sen_slope = np.median(slopes)

    return Z, p_value, sen_slope


def trend_analysis(series, years, output_path='trend.png'):
    """
    趋势分析（Mann-Kendall + 线性回归）
    """
    Z, p, sen = mann_kendall(series.values)
    slope, intercept, r, p_lin, se = linregress(years, series.values)

    trend_desc = 'increasing' if Z > 0 else 'decreasing'
    sig_desc = 'significant' if p < 0.05 else 'not significant'

    print(f"\n趋势分析结果:")
    print(f"  Mann-Kendall Z = {Z:.3f}, p = {p:.4f}")
    print(f"  Sen 斜率 = {sen:.3f}/year ({sen*10:.2f}/decade)")
    print(f"  趋势方向: {trend_desc} ({sig_desc})")
    print(f"  线性回归: slope={slope:.3f}/yr, R²={r**2:.3f}, p={p_lin:.4f}")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(years, series.values, color='steelblue', alpha=0.5)
    ax.plot(years, slope * years + intercept, 'r-', linewidth=2,
            label=f'Linear trend ({slope*10:.2f}/decade, p={p_lin:.3f})')
    ax.plot(years, sen * (years - years[0]) + series.values[0],
            'g--', linewidth=2, label=f'Sen slope ({sen*10:.2f}/decade)')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Trend Analysis ({trend_desc}, {sig_desc})',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"趋势分析图已保存: {output_path}")

    return {'mk_z': Z, 'mk_p': p, 'sen_slope': sen,
            'lin_slope': slope, 'lin_p': p_lin, 'lin_r2': r**2}


def enso_correlation(tc_df, nino34_series, output_path='enso.png'):
    """
    ENSO 遥相关分析

    参数：
        tc_df: 台风数据
        nino34_series: Niño3.4 指数 Series
    """
    annual = tc_df.groupby('year').size()

    # 对齐年份
    common_years = annual.index.intersection(nino34_series.index)
    tc_vals = annual.loc[common_years].values
    nino_vals = nino34_series.loc[common_years].values

    corr = np.corrcoef(tc_vals, nino_vals)[0, 1]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    ax1 = axes[0]
    ax1.bar(common_years, tc_vals, color='steelblue', alpha=0.7,
            label='TC Frequency')
    ax1b = ax1.twinx()
    ax1b.plot(common_years, nino_vals, 'r-', linewidth=2, label='Niño3.4')
    ax1b.axhline(y=0.5, color='r', linestyle='--', alpha=0.3)
    ax1b.axhline(y=-0.5, color='b', linestyle='--', alpha=0.3)
    ax1.set_ylabel('TC Frequency', fontsize=12)
    ax1b.set_ylabel('Niño3.4 (°C)', fontsize=12, color='r')
    ax1.set_title(f'TC Frequency vs ENSO (r = {corr:.2f})',
                  fontsize=14, fontweight='bold')

    ax2 = axes[1]
    colors = np.where(nino_vals > 0.5, 'red',
              np.where(nino_vals < -0.5, 'blue', 'gray'))
    ax2.scatter(nino_vals, tc_vals, c=colors, s=50, alpha=0.7)
    z = np.polyfit(nino_vals, tc_vals, 1)
    ax2.plot(nino_vals, np.polyval(z, nino_vals), 'k-', linewidth=1.5)
    ax2.set_xlabel('Niño3.4 (°C)', fontsize=12)
    ax2.set_ylabel('TC Frequency', fontsize=12)
    ax2.set_title('Scatter: TC Frequency vs ENSO', fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"ENSO 相关分析图已保存: {output_path}")
    print(f"  相关系数: r = {corr:.3f}")
    return corr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风气候统计与趋势分析')
    parser.add_argument('--ibtracs', required=True, help='IBTrACS NetCDF')
    parser.add_argument('--basin', default=None, help='海域代码')
    parser.add_argument('--output', default='./climate_output/', help='输出目录')
    parser.add_argument('--nino34', help='Niño3.4 指数 CSV 文件')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    df = load_best_track(args.ibtracs, args.basin)

    annual = annual_frequency(df, os.path.join(args.output, 'annual_freq.png'))
    seasonal_distribution(df, os.path.join(args.output, 'seasonal.png'))
    intensity_climatology(df, os.path.join(args.output, 'intensity_clim.png'))
    trend_analysis(annual, annual.index,
                   os.path.join(args.output, 'trend.png'))

    if args.nino34:
        nino = pd.read_csv(args.nino34, index_col=0)
        nino.index = pd.to_datetime(nino.index).year
        enso_correlation(df, nino.iloc[:, 0],
                        os.path.join(args.output, 'enso.png'))
