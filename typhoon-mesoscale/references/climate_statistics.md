# 气候统计与趋势分析方法

## 目录

1. [频数气候态](#1-频数气候态)
2. [强度气候态](#2-强度气候态)
3. [路径气候态](#3-路径气候态)
4. [长期趋势检测](#4-长期趋势检测)
5. [年际变率与遥相关](#5-年际变率与遥相关)
6. [生成潜势指数 (GPI)]#6-生成潜势指数-gpi)
7. [未来气候预估](#7-未来气候预估)

---

## 1. 频数气候态

### 年频数统计

```python
import pandas as pd
import matplotlib.pyplot as plt

def annual_frequency(best_track_df):
    """计算台风年频数"""
    best_track_df['year'] = pd.to_datetime(best_track_df['time']).dt.year
    # 每年达到热带风暴强度及以上的数量
    annual = best_track_df[best_track_df['wmo_wind'] >= 34].groupby('year')['sid'].nunique()
    return annual

# 绘制年际变化
annual.plot(kind='bar', figsize=(14, 5))
```

### 季节分布

```python
def seasonal_distribution(best_track_df):
    """台风生成的月际分布"""
    df = best_track_df.copy()
    df['month'] = pd.to_datetime(df['time']).dt.month
    monthly_gen = df.groupby(['sid'])['month'].min()  # 每个台风的生成月
    counts = monthly_gen.value_counts().sort_index()
    counts.plot(kind='bar')
    plt.xlabel('Month')
    plt.ylabel('Number of Genesis')
```

**西北太平洋气候态参考**：
- 年均生成数：约 26 个（达到热带风暴及以上）
- 年均登陆中国数：约 7 个
- 生成高峰月：7-9 月（占总数约 70%）
- 双峰特征：6月小峰 + 8-9月主峰 + 10月次峰

---

## 2. 强度气候态

### 强度比例分布

```python
def intensity_climatology(best_track_df):
    """各强度等级的年均频数"""
    df = best_track_df.copy()
    df['year'] = pd.to_datetime(df['time']).dt.year

    # 取每个台风的生命史最大强度
    max_intensity = df.groupby('sid')['wmo_wind'].max()

    # 分等级统计
    bins = [0, 34, 64, 96, 114, 137, 200]
    labels = ['TD', 'TS', 'Cat1-2', 'Cat3', 'Cat4', 'Cat5']
    cats = pd.cut(max_intensity, bins=bins, labels=labels)
    annual_counts = cats.groupby([df.groupby('sid')['year'].first(), cats]).count().unstack()
    return annual_counts
```

### 强度-频数分布

台风强度服从特定的统计分布——可用幂律或指数分布拟合。近年来对"最强台风比例"的变化关注增多（高频强台风比例增加的信号）。

---

## 3. 路径气候态

### 路径密度分布

```python
def track_density(best_track_df, resolution=1):
    """计算路径密度分布（每平方度内路径点数）"""
    from scipy.stats import binned_statistic_2d

    lat_bins = np.arange(-30, 60, resolution)
    lon_bins = np.arange(40, 180, resolution)
    density, _, _, _ = binned_statistic_2d(
        best_track_df['lat'], best_track_df['lon'],
        best_track_df['wmo_wind'], statistic='count',
        bins=[lat_bins, lon_bins]
    )
    # 归一化为年密度
    n_years = best_track_df['year'].nunique()
    density_per_year = density / n_years
    return density_per_year, lat_bins, lon_bins
```

### 盛行路径分类

西北太平洋路径通常分为：
1. **西行型**：副高强盛，台风直行西移登陆华南/越南
2. **西北行型**：副高偏弱，路径偏北，登陆华东/朝鲜半岛
3. **转向型**：西风槽东移引导台风转向东北，不登陆或登陆后出海
4. **异常型**：打转、回旋、突然北翘等异常路径

---

## 4. 长期趋势检测

### Mann-Kendall 趋势检验

非参数趋势检验，适合非正态分布的气象数据：

```python
from scipy.stats import kendalltau

def mann_kendall_trend(series):
    """Mann-Kendall 趋势检验
    series: 时间序列
    返回: 趋势方向、p值、Sen 斜率
    """
    n = len(series)
    S = 0
    for i in range(n-1):
        for j in range(i+1, n):
            S += np.sign(series[j] - series[i])

    # 方差修正
    var_S = n * (n - 1) * (2 * n + 5) / 18

    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0

    from scipy.stats import norm
    p_value = 2 * (1 - norm.cdf(abs(Z)))

    # Sen 斜率
    slopes = []
    for i in range(n-1):
        for j in range(i+1, n):
            slopes.append((series[j] - series[i]) / (j - i))

    sen_slope = np.median(slopes)

    return {'Z': Z, 'p_value': p_value, 'sen_slope': sen_slope,
            'trend': 'increasing' if Z > 0 else 'decreasing'}
```

### 线性回归趋势

```python
from scipy.stats import linregress

def linear_trend(years, values):
    """线性回归趋势"""
    slope, intercept, r, p, se = linregress(years, values)
    return {'slope': slope, 'p_value': p, 'r_squared': r**2,
            'trend_per_decade': slope * 10}
```

**趋势检测的注意事项**：
- 台风频数/强度数据有显著的年际变率（ENSO 影响可达 ±30%），短期趋势可能被自然变率掩盖
- 至少需要 30 年数据才能可靠检测趋势
- 不同数据源的趋势可能不一致（CMA vs JMA vs JTWC 因定强方法差异）
- 要区分"频数趋势"和"强度趋势"——频数可能减少但平均强度可能增加

---

## 5. 年际变率与遥相关

### ENSO 遥相关

```python
def enso_correlation(tc_data, nino34_index):
    """分析台风活动与 ENSO 的关系"""
    # 年频数与 Niño3.4 的相关
    annual_counts = tc_data.groupby('year').size()
    correlation = np.corrcoef(annual_counts.values, nino34_index.values)[0, 1]

    # El Niño vs La Niña 对比
    nino_years = nino34_index[nino34_index > 0.5].index
    nina_years = nino34_index[nino34_index < -0.5].index

    el_nino_freq = annual_counts[annual_counts.index.isin(nino_years)].mean()
    la_nina_freq = annual_counts[annual_counts.index.isin(nina_years)].mean()

    return {'correlation': correlation,
            'el_nino_mean': el_nino_freq,
            'la_nina_mean': la_nina_freq}
```

### 西北太平洋 ENSO 影响特征

| ENSO 位相 | 生成位置 | 生成数 | 路径特征 | 强度 |
|-----------|---------|--------|---------|------|
| El Niño | 偏东南（远洋） | 略增 | 转向比例高 | 偏强 |
| La Niña | 偏西北（近海） | 略减 | 西行比例高 | 偏弱 |
| 中性 | 正常 | 正常 | 正常 | 正常 |

**其他遥相关**：
- PDO（太平洋年代际振荡）：调制 ENSO 的影响
- IOD（印度洋偶极子）：正 IOD 时西北太平洋台风偏强
- MJO（马登-朱利安振荡）：调制台风生成的活跃期和静默期

---

## 6. 生成潜势指数 (GPI)

### Emanuel-Nolan GPI

```python
def calc_gpi(sst, vor_850, shear_200_850, rh_600, potential_intensity):
    """Emanuel-Nolan (2004) 生成潜势指数
    GPI = |η850|^1.5 * (1+0.1*Vshear)^(-2) * RH600 * PI^3 * exp(-(SST-26)/15)
    """
    gpi = (np.abs(vor_850)**1.5 *
           (1 + 0.1 * shear_200_850)**(-2) *
           rh_600 *
           potential_intensity**3 *
           np.exp(-(sst - 26) / 15))
    return gpi
```

**GPI 的用途**：
- 诊断气候模式中台风活动的变化原因（哪个因子贡献最大）
- 未来气候情景下台风活动的预估
- 解释台风生成位置和季节的气候态分布

---

## 7. 未来气候预估

### CMIP6 / HighResMIP 分析

```python
def future_projection_analysis(cmip6_data, period_historical, period_future):
    """分析 CMIP6/HighResMIP 中台风活动变化"""
    # 用台风检测算法从模式输出中识别气旋
    # 常用工具：
    # - TempestExtremes (Ullrich)
    # - TRACK (Hodgson)
    # - cyclone detection (Walsh)

    historical = cmip6_data.sel(time=period_historical)
    future = cmip6_data.sel(time=period_future)

    # 对比频数、强度、路径的统计差异
    freq_change = len(future) - len(historical)
    intensity_change = future['vmax'].mean() - historical['vmax'].mean()

    return {'freq_change': freq_change,
            'intensity_change': intensity_change}
```

**IPCC AR6 共识**：
- 台风总频数可能减少或不变
- 强台风（Cat4-5）比例可能增加
- 台风降水率可能增加（+10-15%， Clausius-Clapeyron 关系 + 动力学变化）
- 台风可能移动减缓（外围环流减弱）

---

## 注意事项

1. **数据一致性**：做气候统计必须使用同一版本、同一机构的数据。IBTrACS 版本更新会修改历史记录。
2. **热带低压的处理**：不同机构对热带低压的记录标准不同，做频数统计前要明确统计口径。
3. **季节调整**：台风活动有强季节性，做年际趋势分析前需要做季节调整或用年总量。
4. **显著性检验**：气候趋势一定要报告统计显著性。自然变率大时，即使有趋势也可能不显著。
5. **归因与相关**：发现台风活动与某气候指数相关不等于因果关系。需要动力机制解释和模式验证。
