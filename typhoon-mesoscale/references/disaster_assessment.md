# 灾害影响评估方法

## 目录

1. [风灾评估](#1-风灾评估)
2. [暴雨灾害评估](#2-暴雨灾害评估)
3. [风暴潮评估](#3-风暴潮评估)
4. [经济损失统计](#4-经济损失统计)
5. [伤亡分析](#5-伤亡分析)
6. [综合风险评估](#6-综合风险评估)

---

## 1. 风灾评估

### 风场重建

台风灾害评估的第一步是获取风场——通常用最佳路径 + 风场模型重建：

```python
def holland_wind_field(pmin, pn, vmax, rmax, lat0, lon0, r_array, theta_array):
    """Holland (1980) 梯度风模型重建风场
    pmin: 中心气压 (hPa)
    pn: 环境气压 (hPa), 通常 1010
    vmax: 最大风速 (m/s)
    rmax: 最大风速半径 (km)
    r_array: 半径数组 (km)
    theta_array: 方位角数组 (度)
    """
    rho = 1.15  # 空气密度 kg/m^3
    f = 2 * 7.292e-5 * np.sin(np.radians(lat0))  # 科氏参数

    # Holland B 参数
    B = (vmax**2 * rho * np.e) / (100 * (pn - pmin))  # 简化估计
    B = np.clip(B, 1.0, 2.5)

    # 梯度风方程
    r_m = r_array * 1000  # 转为 m
    dp = pn - pmin  # hPa
    gradient_wind = np.sqrt(
        (B / rho) * (rmax * 1000 / r_m)**B * dp * 100 * np.exp(-(rmax*1000/r_m)**B)
        + (r_m * f / 2)**2
    ) - r_m * f / 2

    return gradient_wind  # m/s
```

### 脆弱性曲线

```python
def damage_ratio(wind_speed, vulnerability_curve='EU'):
    """根据风速计算建筑物损毁率
    vulnerability_curve: 脆弱性曲线类型
    """
    curves = {
        'EU': lambda v: 0 if v < 25 else min(1.0, 0.002 * (v - 25)**2.5),
        'NA': lambda v: 0 if v < 30 else min(1.0, 0.001 * (v - 30)**3),
        'CN': lambda v: 0 if v < 17 else min(1.0, 0.0005 * (v - 17)**3),
    }
    return curves.get(vulnerability_curve, curves['EU'])(wind_speed)
```

### 风灾等级

中国气象局的台风灾害等级划分（基于风速和灾害影响）：

| 等级 | 风速 (m/s) | 影响 |
|------|-----------|------|
| 轻微 | <17.2 | 树枝摇摆，轻损 |
| 中等 | 17.2-24.4 | 屋顶损坏，电力中断 |
| 严重 | 24.5-32.6 | 建筑物结构损毁 |
| 特大 | 32.7-41.5 | 大范围房屋倒塌 |
| 极端 | >41.5 | 毁灭性破坏 |

---

## 2. 暴雨灾害评估

### 降水阈值与风险

```python
def rainfall_risk_assessment(precip_24h, precip_1h, thresholds):
    """暴雨风险评估
    precip_24h: 24小时累积降水 (mm)
    precip_1h: 最大1小时降水 (mm)
    thresholds: 风险阈值字典
    """
    risk_level = 'low'
    if precip_24h > thresholds.get('extreme_24h', 250):
        risk_level = 'extreme'
    elif precip_24h > thresholds.get('severe_24h', 100):
        risk_level = 'severe'
    elif precip_24h > thresholds.get('moderate_24h', 50):
        risk_level = 'moderate'

    # 结合短时降水强度
    if precip_1h > thresholds.get('extreme_1h', 50):
        risk_level = 'extreme'

    return risk_level
```

### 重现期对比

```python
def return_period_comparison(observed_precip, gev_params):
    """将观测降水与历史重现期对比"""
    from scipy.stats import genextreme
    shape, loc, scale = gev_params
    # 计算观测值的重现期
    return_period = 1 / (1 - genextreme.cdf(observed_precip, shape, loc=loc, scale=scale))
    return return_period
```

### 中国暴雨风险阈值参考

| 风险等级 | 24h降水 (mm) | 1h降水 (mm) | 影响 |
|---------|-------------|------------|------|
| 蓝色预警 | 50 | — | 注意 |
| 黄色预警 | 100 | 30 | 需防范 |
| 橙色预警 | 200 | 50 | 严重 |
| 红色预警 | 250+ | 100+ | 极端 |

---

## 3. 风暴潮评估

### SLOSH/ADCIRC 模型

风暴潮是台风灾害的重要组成，常导致沿海严重灾情：

```python
def storm_surge_analysis(surge_data, tidal_data):
    """分离风暴潮和天文潮
    surge_data: 潮位观测/模拟
    tidal_data: 天文潮预报
    """
    surge_residual = surge_data - tidal_data
    # 最大增水
    max_surge = surge_residual.max()
    # 增水峰值时间
    peak_time = surge_residual.idxmax()
    return max_surge, peak_time, surge_residual
```

### 风暴潮经验估计

```python
def empirical_surge(vmax, rmax, track_angle, bathymetry_factor=1.0):
    """经验风暴潮估计（简化）
    vmax: 最大风速 (m/s)
    rmax: 最大风速半径 (km)
    track_angle: 路径与海岸夹角 (度)
    bathymetry_factor: 水深修正
    """
    # 简化经验公式
    surge = 0.25 * vmax * bathymetry_factor  # m
    # 右侧（危险半圆）增水更大
    if track_angle < 90:
        surge *= 1.3  # 近垂直登陆，右侧增水大
    return surge
```

---

## 4. 经济损失统计

### 归一化方法

历史灾情数据需要做归一化——考虑通胀、人口增长和财富增长的影响：

```python
def normalize_losses(raw_loss, year, cpi_index, population_index, wealth_index):
    """将历史经济损失归一化到参考年
    参考 Pielke & Landsea (1999) 归一化方法
    """
    cpi_ratio = cpi_index[reference_year] / cpi_index[year]
    pop_ratio = population_index[reference_year] / population_index[year]
    wealth_ratio = wealth_index[reference_year] / wealth_index[year]

    normalized = raw_loss * cpi_ratio * pop_ratio * wealth_ratio
    return normalized
```

### 损失-强度关系

```python
def loss_intensity_regression(losses, intensities):
    """拟合经济损失与台风强度的关系"""
    from scipy.stats import linregress
    # 通常用对数线性模型
    log_losses = np.log(losses + 1)
    slope, intercept, r, p, se = linregress(intensities, log_losses)
    return {
        'slope': slope, 'intercept': intercept,
        'r_squared': r**2, 'p_value': p,
        'interpretation': f'风速每增加 1 m/s, 损失增加 {np.exp(slope)-1:.1%}'
    }
```

**科学提示**：归一化后的台风经济损失在长期趋势上可能不显著（Pielke et al. 2008），这意味着社会经济发展（而非气候变化）是损失增长的主要原因。这一结论在学术界仍有争议——Weinkle et al. (2018) 指出不同的归一化方法可能给出不同结论。

---

## 5. 伤亡分析

### 伤亡与强度的统计关系

```python
def casualty_analysis(casualty_data, intensity_data):
    """分析伤亡人数与台风特征的关系"""
    import pandas as pd
    import statsmodels.api as sm

    # 通常用负二项回归（伤亡数据过度离散）
    X = sm.add_constant(intensity_data[['vmax', 'landfall_pressure', 'precip_max']])
    model = sm.GLM(casualty_data['deaths'], X,
                   family=sm.families.NegativeBinomial())
    result = model.fit()
    return result
```

### 伤亡与预警时效

伤亡人数与预警提前时间、疏散执行情况强相关。发达地区的台风伤亡通常主要来自暴雨次生灾害（山洪、泥石流），而非风灾直接致死。

---

## 6. 综合风险评估

### 多因子风险叠加

```python
def comprehensive_risk_assessment(wind_risk, flood_risk, surge_risk,
                                  population_density, vulnerability):
    """多因子综合风险等级"""
    # 各维度 0-1 归一化
    # 加权叠加
    weights = {'wind': 0.25, 'flood': 0.35, 'surge': 0.25, 'vuln': 0.15}

    total_risk = (wind_risk * weights['wind'] +
                  flood_risk * weights['flood'] +
                  surge_risk * weights['surge'] +
                  population_density * vulnerability * weights['vuln'])
    return total_risk
```

### 风险等级划分

```python
def risk_level(comprehensive_score):
    if comprehensive_score > 0.75:
        return 'extreme'
    elif comprehensive_score > 0.5:
        return 'severe'
    elif comprehensive_score > 0.25:
        return 'moderate'
    else:
        return 'low'
```

### GIS 制图

综合风险通常以空间地图形式呈现：

```python
import cartopy.crs as ccrs

def plot_risk_map(risk_field, lats, lons):
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines()
    levels = [0, 0.25, 0.5, 0.75, 1.0]
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    ax.contourf(lons, lats, risk_field, levels=levels, colors=colors,
                transform=ccrs.PlateCarree())
    ax.set_title('Comprehensive Typhoon Risk Assessment')
```

---

## 注意事项

1. **灾情数据的可靠性**：不同来源的灾情统计标准不同（EM-DAT vs 中国气象灾害年鉴），死亡人数和经济损失的统计可能相差数倍。
2. **近因效应**：历史灾情数据存在"近因效应"——近年灾害被更充分记录，可能导致虚假的上升趋势。归一化分析可部分修正这一问题。
3. **间接损失**：经济影响不仅包括直接损失（建筑/基础设施损毁），还有间接损失（停产、供应链中断、灾后重建成本）。通常间接损失可达直接损失的 50-100%。
4. **脆弱性变化**：社会脆弱性随发展水平变化——同样的台风在 20 年前和现在的经济损失和伤亡可能截然不同。风险评估必须考虑脆弱性的时间变化。
5. **复合灾害**：台风灾害往往是风+雨+潮的复合效应，单因子的风险评估可能低估总风险。
