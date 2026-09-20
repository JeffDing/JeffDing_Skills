#!/usr/bin/env python3
"""
台风快速增强(RI)诊断分析

功能：
    - RI 事件识别
    - SHIPS 因子分析
    - RI 有利条件综合判据
    - RI vs 非 RI 对比
    - RI 概率预报评估
    - 环境因子时间序列图

依赖：pandas, numpy, matplotlib, sklearn

用法：
    python ri_diagnosis.py --track track.csv --name HATO --output ri.png
    python ri_diagnosis.py --ships ships_data.csv --output ships.png
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss


def identify_ri(intensity_series, threshold=30, window=24, dt=6):
    """
    识别 RI 事件

    参数：
        intensity_series: 最大风速序列 (kt)
        threshold: RI 阈值 (kt)
        window: 时间窗口 (小时)
        dt: 时间间隔 (小时)

    返回：RI 事件列表
    """
    steps = window // dt
    ri_events = []
    values = intensity_series.values
    times = intensity_series.index

    for i in range(len(values) - steps):
        change = values[i + steps] - values[i]
        if change >= threshold:
            ri_events.append({
                'start_time': times[i],
                'end_time': times[i + steps],
                'intensity_change': change,
                'start_intensity': values[i],
                'end_intensity': values[i + steps],
            })
    return ri_events


def ri_favorable_check(sst, shear, rh_mid, d200, pot, land_dist, speed):
    """
    RI 有利条件综合判据

    返回各条件满足情况和总体评分
    """
    conditions = {
        'warm_sst (SST > 28.5°C)': sst > 28.5,
        'weak_shear (< 8 m/s)': shear < 8,
        'moist_mid (RH > 60%)': rh_mid > 60,
        'upper_div (D200 > 2e-6 s⁻¹)': d200 > 2e-6,
        'high_pot (Pot > 20 kt)': pot > 20,
        'far_land (> 200 km)': land_dist > 200,
        'slow_move (< 5 m/s)': speed < 5,
    }
    n_met = sum(conditions.values())
    return conditions, n_met


def plot_ri_periods(df, ri_events, storm_name='', output_path='ri_periods.png'):
    """
    在强度演变图上标注 RI 时期
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df['time'], df['vmax'], 'b-', linewidth=2.5, label='Vmax')

    for event in ri_events:
        mask = (df['time'] >= event['start_time']) & (df['time'] <= event['end_time'])
        ax.axvspan(event['start_time'], event['end_time'],
                   alpha=0.2, color='red')
        ax.annotate(f"+{event['intensity_change']:.0f}kt",
                    xy=(event['end_time'], event['end_intensity']),
                    fontsize=9, color='red', fontweight='bold')

    ax.axhline(y=34, color='green', linestyle='--', alpha=0.3)
    ax.axhline(y=64, color='orange', linestyle='--', alpha=0.3)
    ax.axhline(y=96, color='red', linestyle='--', alpha=0.3)

    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Maximum Wind Speed (kt)', fontsize=12)
    ax.set_title(f'Typhoon {storm_name} - RI Periods (≥30 kt/24h)',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"RI 时期标注图已保存: {output_path}")


def plot_ships_factors(ships_df, output_path='ships_factors.png'):
    """
    绘制 SHIPS 因子时间序列（多面板）

    参数：
        ships_df: 含 SST, shear, rh_mid, d200, pot 等列的 DataFrame
    """
    factors = {
        'SST': ('SST (°C)', 'RdYlBu_r'),
        'shear': ('Deep Shear (m/s)', 'YlOrRd'),
        'rh_mid': ('Mid-level RH (%)', 'YlGnBu'),
        'd200': ('200hPa Div (1e-6 s⁻¹)', 'RdBu_r'),
        'pot': ('Potential Intensity (kt)', 'YlOrRd'),
    }

    available = [f for f in factors if f in ships_df.columns]
    n = len(available)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3*n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, factor in zip(axes, available):
        label, cmap = factors[factor]
        ax.plot(ships_df.index, ships_df[factor], 'b-', linewidth=2)
        ax.fill_between(ships_df.index, ships_df[factor].min(),
                        ships_df[factor], alpha=0.1)
        ax.set_ylabel(label, fontsize=10)
        ax.grid(True, alpha=0.3)

        # 标注 RI 阈值
        thresholds = {
            'SST': 28.5, 'shear': 8, 'rh_mid': 60,
            'd200': 2e-6, 'pot': 20
        }
        if factor in thresholds:
            ax.axhline(y=thresholds[factor], color='r', linestyle='--',
                       alpha=0.5, label=f'RI threshold: {thresholds[factor]}')
            ax.legend(fontsize=8)

    axes[-1].set_xlabel('Time', fontsize=12)
    plt.suptitle('SHIPS Environmental Factors Time Series',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"SHIPS 因子图已保存: {output_path}")


def ri_logistic_model(factors_df, ri_labels):
    """
    构建 RI 逻辑回归概率预报模型

    参数：
        factors_df: 预报因子 DataFrame
        ri_labels: RI 发生(1)/不发生(0) 标签

    返回：模型和预报概率
    """
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(factors_df, ri_labels)
    ri_prob = model.predict_proba(factors_df)[:, 1]
    return model, ri_prob


def evaluate_ri_forecast(probabilities, observations, threshold=0.4):
    """
    评估 RI 概率预报

    参数：
        probabilities: RI 概率预报
        observations: 实际是否 RI (0/1)
        threshold: 二值化阈值

    返回：检验指标字典
    """
    binary_fcst = (probabilities >= threshold).astype(int)

    tp = np.sum((binary_fcst == 1) & (observations == 1))
    fp = np.sum((binary_fcst == 1) & (observations == 0))
    fn = np.sum((binary_fcst == 0) & (observations == 1))
    tn = np.sum((binary_fcst == 0) & (observations == 0))

    pod = tp / (tp + fn) if (tp + fn) > 0 else 0
    far = fp / (fp + tp) if (fp + tp) > 0 else 0
    brier = brier_score_loss(observations, probabilities)
    auc = roc_auc_score(observations, probabilities) if observations.sum() > 0 else np.nan

    return {
        'POD': pod, 'FAR': far, 'Brier': brier, 'AUC': auc,
        'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
        'threat_score': tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0,
    }


def compare_ri_nonri(ri_factors, nonri_factors, factor_names):
    """
    RI vs 非 RI 环境因子对比

    参数：
        ri_factors: RI 事件环境因子 DataFrame
        nonri_factors: 非 RI 事件环境因子 DataFrame
        factor_names: 因子名称列表

    返回：对比统计表
    """
    from scipy.stats import ttest_ind

    results = []
    for factor in factor_names:
        if factor not in ri_factors.columns or factor not in nonri_factors.columns:
            continue
        ri_vals = ri_factors[factor].dropna()
        nonri_vals = nonri_factors[factor].dropna()

        if len(ri_vals) < 2 or len(nonri_vals) < 2:
            continue

        t_stat, p_val = ttest_ind(ri_vals, nonri_vals)
        results.append({
            'factor': factor,
            'ri_mean': ri_vals.mean(),
            'ri_std': ri_vals.std(),
            'nonri_mean': nonri_vals.mean(),
            'nonri_std': nonri_vals.std(),
            'difference': ri_vals.mean() - nonri_vals.mean(),
            't_stat': t_stat,
            'p_value': p_val,
            'significant': p_val < 0.05,
        })

    return pd.DataFrame(results)


def plot_ri_comparison(comparison_df, output_path='ri_comparison.png'):
    """
    绘制 RI vs 非 RI 对比图
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(comparison_df))
    width = 0.35

    ax.bar(x - width/2, comparison_df['ri_mean'], width,
           yerr=comparison_df['ri_std'], label='RI', color='red', alpha=0.7,
           capsize=3)
    ax.bar(x + width/2, comparison_df['nonri_mean'], width,
           yerr=comparison_df['nonri_std'], label='Non-RI', color='blue', alpha=0.7,
           capsize=3)

    # 标注显著性
    for i, row in comparison_df.iterrows():
        if row['significant']:
            ax.text(i, max(row['ri_mean'], row['nonri_mean']) + row[['ri_std','nonri_std']].max(),
                    '*', fontsize=14, ha='center', color='red', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(comparison_df['factor'], rotation=45, ha='right')
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('RI vs Non-RI Environmental Factors Comparison\n(* = p < 0.05)',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"RI 对比图已保存: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风快速增强诊断')
    parser.add_argument('--track', help='路径数据 CSV (含 time, vmax)')
    parser.add_argument('--ships', help='SHIPS 因子数据 CSV')
    parser.add_argument('--name', default='', help='台风名称')
    parser.add_argument('--output', default='ri.png', help='输出路径')
    parser.add_argument('--threshold', type=float, default=30,
                        help='RI 阈值 (kt/24h)')
    args = parser.parse_args()

    if args.track:
        df = pd.read_csv(args.track)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time').reset_index(drop=True)

        ri_events = identify_ri(df.set_index('time')['vmax'],
                                threshold=args.threshold)
        print(f"\n识别到 {len(ri_events)} 个 RI 事件:")
        for event in ri_events:
            print(f"  {event['start_time']} → {event['end_time']}: "
                  f"+{event['intensity_change']:.0f} kt "
                  f"({event['start_intensity']:.0f} → {event['end_intensity']:.0f})")

        plot_ri_periods(df, ri_events, args.name, args.output)

    if args.ships:
        ships = pd.read_csv(args.ships, index_col=0)
        plot_ships_factors(ships, args.output.replace('.png', '_ships.png'))
