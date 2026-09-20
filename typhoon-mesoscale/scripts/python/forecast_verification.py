#!/usr/bin/env python3
"""
台风预报检验

功能：
    - 路径预报误差计算（各预报时效）
    - 强度预报误差计算
    - 技巧评分（相对 CLIPER/SHIFOR）
    - 预报偏差分析
    - 多模式对比表
    - 误差分布图

依赖：pandas, numpy, matplotlib

用法：
    python forecast_verification.py --fcst forecast.csv --best best_track.csv --output verify.png
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def great_circle_distance(lat1, lon1, lat2, lon2):
    """
    大圆距离 (km)
    """
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def verify_track(fcst_df, best_df, lead_times=[24, 48, 72, 96, 120]):
    """
    路径预报检验

    参数：
        fcst_df: 预报数据，含 init_time, lead_time, lat, lon
        best_df: 最佳路径数据，含 time, lat, lon
        lead_times: 预报时效列表 (小时)

    返回：各时效的平均误差 (km)
    """
    results = {}
    for lt in lead_times:
        fcst_lt = fcst_df[fcst_df['lead_time'] == lt].copy()
        errors = []
        for _, row in fcst_lt.iterrows():
            valid_time = row['init_time'] + pd.Timedelta(hours=lt)
            best_match = best_df[best_df['time'] == valid_time]
            if len(best_match) > 0:
                err = great_circle_distance(
                    row['lat'], row['lon'],
                    best_match.iloc[0]['lat'], best_match.iloc[0]['lon']
                )
                errors.append(err)
        results[lt] = np.mean(errors) if errors else np.nan
    return results


def verify_intensity(fcst_df, best_df, lead_times=[24, 48, 72, 96, 120]):
    """
    强度预报检验

    参数：
        fcst_df: 预报数据，含 init_time, lead_time, vmax
        best_df: 最佳路径数据，含 time, vmax

    返回：各时效的平均绝对误差 (kt)
    """
    results = {}
    for lt in lead_times:
        fcst_lt = fcst_df[fcst_df['lead_time'] == lt].copy()
        errors = []
        for _, row in fcst_lt.iterrows():
            valid_time = row['init_time'] + pd.Timedelta(hours=lt)
            best_match = best_df[best_df['time'] == valid_time]
            if len(best_match) > 0:
                err = abs(row['vmax'] - best_match.iloc[0]['vmax'])
                errors.append(err)
        results[lt] = np.mean(errors) if errors else np.nan
    return results


def skill_score(forecast_error, baseline_error):
    """
    技巧评分 = (1 - 预报误差/基准误差) × 100%
    """
    if baseline_error == 0:
        return np.nan
    return (1 - forecast_error / baseline_error) * 100


def plot_verification(track_errors, intensity_errors,
                       track_baseline=None, intensity_baseline=None,
                       model_name='', output_path='verify.png'):
    """
    绘制预报检验图

    参数：
        track_errors: {lead_time: error_km}
        intensity_errors: {lead_time: error_kt}
        track_baseline: 基准（CLIPER）路径误差
        intensity_baseline: 基准（SHIFOR）强度误差
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 路径误差
    ax1 = axes[0]
    lts = list(track_errors.keys())
    vals = [track_errors[lt] for lt in lts]
    ax1.plot(lts, vals, 'bo-', linewidth=2, markersize=8,
             label=f'{model_name} Track Error')
    if track_baseline:
        base_vals = [track_baseline.get(lt, np.nan) for lt in lts]
        ax1.plot(lts, base_vals, 'r--', linewidth=2, markersize=6,
                 label='CLIPER Baseline')
    ax1.set_xlabel('Forecast Lead Time (h)', fontsize=12)
    ax1.set_ylabel('Track Error (km)', fontsize=12)
    ax1.set_title('Track Forecast Verification', fontsize=14,
                  fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(lts)

    # 强度误差
    ax2 = axes[1]
    vals2 = [intensity_errors[lt] for lt in lts]
    ax2.plot(lts, vals2, 'bo-', linewidth=2, markersize=8,
             label=f'{model_name} Intensity Error')
    if intensity_baseline:
        base_vals2 = [intensity_baseline.get(lt, np.nan) for lt in lts]
        ax2.plot(lts, base_vals2, 'r--', linewidth=2, markersize=6,
                 label='SHIFOR Baseline')
    ax2.set_xlabel('Forecast Lead Time (h)', fontsize=12)
    ax2.set_ylabel('Intensity Error (kt)', fontsize=12)
    ax2.set_title('Intensity Forecast Verification', fontsize=14,
                  fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(lts)

    plt.suptitle(f'Forecast Verification: {model_name}',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"预报检验图已保存: {output_path}")


def multi_model_comparison(models_errors, model_names, output_path='multi_verify.png'):
    """
    多模式预报对比图

    参数：
        models_errors: [{lt: err, ...}, ...] 路径误差字典列表
        model_names: 模式名称列表
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Set1(np.linspace(0, 1, len(models_errors)))
    lead_times = sorted(models_errors[0].keys())

    for errors, name, color in zip(models_errors, model_names, colors):
        vals = [errors.get(lt, np.nan) for lt in lead_times]
        ax.plot(lead_times, vals, 'o-', color=color, linewidth=2,
                markersize=8, label=name)

    ax.set_xlabel('Forecast Lead Time (h)', fontsize=12)
    ax.set_ylabel('Track Error (km)', fontsize=12)
    ax.set_title('Multi-Model Track Forecast Comparison', fontsize=14,
                 fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(lead_times)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"多模式对比图已保存: {output_path}")


def error_distribution(fcst_df, best_df, lead_time=72,
                        output_path='error_dist.png'):
    """
    误差分布直方图

    参数：
        fcst_df: 预报数据
        best_df: 最佳路径数据
        lead_time: 预报时效
    """
    fcst_lt = fcst_df[fcst_df['lead_time'] == lead_time].copy()
    errors = []
    for _, row in fcst_lt.iterrows():
        valid_time = row['init_time'] + pd.Timedelta(hours=lead_time)
        best_match = best_df[best_df['time'] == valid_time]
        if len(best_match) > 0:
            err = great_circle_distance(
                row['lat'], row['lon'],
                best_match.iloc[0]['lat'], best_match.iloc[0]['lon']
            )
            errors.append(err)

    if not errors:
        print(f"无 {lead_time}h 预报数据")
        return

    errors = np.array(errors)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 直方图
    ax1 = axes[0]
    ax1.hist(errors, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(x=np.mean(errors), color='red', linestyle='--', linewidth=2,
                label=f'Mean = {np.mean(errors):.0f} km')
    ax1.axvline(x=np.median(errors), color='green', linestyle='--', linewidth=2,
                label=f'Median = {np.median(errors):.0f} km')
    ax1.set_xlabel('Track Error (km)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title(f'{lead_time}h Forecast Error Distribution', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 累积分布
    ax2 = axes[1]
    sorted_err = np.sort(errors)
    cdf = np.arange(1, len(sorted_err) + 1) / len(sorted_err)
    ax2.plot(sorted_err, cdf, 'b-', linewidth=2)
    for pct in [50, 75, 90]:
        val = np.percentile(errors, pct)
        ax2.axhline(y=pct/100, color='gray', linestyle='--', alpha=0.3)
        ax2.axvline(x=val, color='gray', linestyle='--', alpha=0.3)
        ax2.text(val, pct/100, f' {pct}%: {val:.0f}km', fontsize=9)
    ax2.set_xlabel('Track Error (km)', fontsize=12)
    ax2.set_ylabel('Cumulative Probability', fontsize=12)
    ax2.set_title(f'{lead_time}h Error CDF', fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"误差分布图已保存: {output_path}")


def summary_table(track_errors, intensity_errors,
                   track_baseline=None, intensity_baseline=None):
    """
    生成检验结果汇总表
    """
    rows = []
    for lt in sorted(track_errors.keys()):
        te = track_errors[lt]
        ie = intensity_errors.get(lt, np.nan)
        ts = skill_score(te, track_baseline.get(lt, np.nan)) if track_baseline else np.nan
        iss = skill_score(ie, intensity_baseline.get(lt, np.nan)) if intensity_baseline else np.nan
        rows.append({
            'Lead Time (h)': lt,
            'Track Error (km)': f'{te:.1f}',
            'Intensity Error (kt)': f'{ie:.1f}',
            'Track Skill (%)': f'{ts:.1f}' if not np.isnan(ts) else '—',
            'Intensity Skill (%)': f'{iss:.1f}' if not np.isnan(iss) else '—',
        })
    df = pd.DataFrame(rows)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='台风预报检验')
    parser.add_argument('--fcst', required=True, help='预报数据 CSV')
    parser.add_argument('--best', required=True, help='最佳路径 CSV')
    parser.add_argument('--model', default='', help='模式名称')
    parser.add_argument('--output', default='verify.png', help='输出路径')
    args = parser.parse_args()

    fcst = pd.read_csv(args.fcst)
    fcst['init_time'] = pd.to_datetime(fcst['init_time'])
    best = pd.read_csv(args.best)
    best['time'] = pd.to_datetime(best['time'])

    lead_times = [24, 48, 72, 96, 120]
    track_errs = verify_track(fcst, best, lead_times)
    intensity_errs = verify_intensity(fcst, best, lead_times)

    print("\n检验结果:")
    for lt in lead_times:
        print(f"  {lt}h: Track={track_errs.get(lt, 0):.1f} km, "
              f"Intensity={intensity_errs.get(lt, 0):.1f} kt")

    plot_verification(track_errs, intensity_errs,
                      model_name=args.model, output_path=args.output)

    error_distribution(fcst, best, lead_time=72,
                       output_path=args.output.replace('.png', '_dist.png'))

    table = summary_table(track_errs, intensity_errs)
    print("\n汇总表:")
    print(table.to_string(index=False))
