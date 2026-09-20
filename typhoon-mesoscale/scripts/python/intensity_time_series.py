#!/usr/bin/env python3
"""
台风强度时间序列分析

功能：
    - 绘制强度演变图（Vmax + Pmin 双轴）
    - 强度变化率分析
    - 多台风强度对比
    - 强度等级标注

依赖：matplotlib, pandas, numpy

用法：
    python intensity_time_series.py --csv track_data.csv --name HATO --output intensity.png
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_intensity_series(df, storm_name='', output_path='intensity.png'):
    """
    绘制强度时间序列图（Vmax + Pmin 双轴）

    参数：
        df: 含 time, vmax, pres 列的 DataFrame
        storm_name: 台风名称
        output_path: 输出路径
    """
    df = df.sort_values('time').reset_index(drop=True)

    fig, ax1 = plt.subplots(figsize=(14, 6))

    color_wind = '#e74c3c'
    ax1.plot(df['time'], df['vmax'], color=color_wind, linewidth=2.5,
             marker='o', markersize=4, label='Vmax')
    ax1.fill_between(df['time'], 0, df['vmax'], alpha=0.1, color=color_wind)
    ax1.set_ylabel('Maximum Wind Speed (kt)', color=color_wind, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_wind)
    ax1.set_ylim(bottom=0)

    ax1.axhline(y=34, color='green', linestyle='--', alpha=0.4, linewidth=1)
    ax1.axhline(y=64, color='orange', linestyle='--', alpha=0.4, linewidth=1)
    ax1.axhline(y=96, color='red', linestyle='--', alpha=0.4, linewidth=1)
    ax1.axhline(y=137, color='darkred', linestyle='--', alpha=0.4, linewidth=1)

    ax1.text(df['time'].iloc[0], 36, 'TS', fontsize=8, color='green', alpha=0.6)
    ax1.text(df['time'].iloc[0], 66, 'Cat1', fontsize=8, color='orange', alpha=0.6)
    ax1.text(df['time'].iloc[0], 98, 'Cat3', fontsize=8, color='red', alpha=0.6)
    ax1.text(df['time'].iloc[0], 139, 'Cat5', fontsize=8, color='darkred', alpha=0.6)

    ax2 = ax1.twinx()
    color_pres = '#3498db'
    ax2.plot(df['time'], df['pres'], color=color_pres, linewidth=2.5,
             marker='s', markersize=3, label='Pmin')
    ax2.set_ylabel('Minimum Sea Level Pressure (hPa)', color=color_pres, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_pres)
    ax2.invert_yaxis()

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    fig.autofmt_xdate()

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    ax1.set_title(f'Typhoon {storm_name} Intensity Evolution',
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"强度时间序列图已保存: {output_path}")


def plot_intensity_rate(df, storm_name='', output_path='intensity_rate.png'):
    """
    绘制强度变化率图，标注 RI 事件

    参数：
        df: 含 time, vmax 列的 DataFrame
        storm_name: 台风名称
        output_path: 输出路径
    """
    df = df.sort_values('time').reset_index(drop=True)
    dt_hours = df['time'].diff().dt.total_seconds() / 3600
    df['dvmax_dt'] = df['vmax'].diff() / dt_hours * 24  # kt/24h

    fig, ax = plt.subplots(figsize=(14, 5))

    colors = np.where(df['dvmax_dt'] >= 30, 'red',
              np.where(df['dvmax_dt'] >= 15, 'orange',
              np.where(df['dvmax_dt'] <= -15, 'blue',
              np.where(df['dvmax_dt'] <= -30, 'darkblue', 'gray'))))

    ax.bar(df['time'], df['dvmax_dt'], width=0.15, color=colors, alpha=0.7)
    ax.axhline(y=30, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.axhline(y=-30, color='blue', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.axhline(y=0, color='black', linewidth=0.5)

    ax.text(df['time'].iloc[-1], 32, 'RI threshold (30 kt/24h)',
            fontsize=8, color='red', ha='right')

    ax.set_ylabel('Intensity Change Rate (kt/24h)', fontsize=12)
    ax.set_title(f'Typhoon {storm_name} Intensity Change Rate',
                 fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"强度变化率图已保存: {output_path}")


def compare_intensities(df_list, names, output_path='compare_intensity.png'):
    """
    多台风强度对比图

    参数：
        df_list: DataFrame 列表
        names: 名称列表
        output_path: 输出路径
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Set1(np.linspace(0, 1, len(df_list)))

    for df, name, color in zip(df_list, names, colors):
        df = df.sort_values('time').reset_index(drop=True)
        hours_from_genesis = (df['time'] - df['time'].iloc[0]).dt.total_seconds() / 3600
        ax.plot(hours_from_genesis, df['vmax'], linewidth=2, label=name, color=color)

    ax.axhline(y=34, color='gray', linestyle='--', alpha=0.3)
    ax.axhline(y=64, color='gray', linestyle='--', alpha=0.3)
    ax.axhline(y=96, color='gray', linestyle='--', alpha=0.3)
    ax.axhline(y=137, color='gray', linestyle='--', alpha=0.3)

    ax.set_xlabel('Hours from Genesis', fontsize=12)
    ax.set_ylabel('Maximum Wind Speed (kt)', fontsize=12)
    ax.set_title('Intensity Evolution Comparison', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"强度对比图已保存: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风强度时间序列分析')
    parser.add_argument('--csv', required=True, help='路径数据 CSV 文件')
    parser.add_argument('--name', default='', help='台风名称')
    parser.add_argument('--output', default='intensity.png', help='输出路径')
    parser.add_argument('--rate', action='store_true', help='绘制强度变化率')
    parser.add_argument('--compare', nargs='+', help='对比多个 CSV 文件')
    args = parser.parse_args()

    if args.compare:
        dfs = [pd.read_csv(f) for f in [args.csv] + args.compare]
        names = [args.name] + [f.split('/')[-1].replace('.csv', '') for f in args.compare]
        compare_intensities(dfs, names, args.output)
    else:
        df = pd.read_csv(args.csv)
        df['time'] = pd.to_datetime(df['time'])
        plot_intensity_series(df, args.name, args.output)
        if args.rate:
            rate_output = args.output.replace('.png', '_rate.png')
            plot_intensity_rate(df, args.name, rate_output)
