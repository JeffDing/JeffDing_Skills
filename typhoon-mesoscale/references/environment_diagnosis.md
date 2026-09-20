# 环境场诊断方法

## 目录

1. [海表温度 (SST) 分析](#1-海表温度-sst-分析)
2. [垂直风切变](#2-垂直风切变)
3. [大气湿度与水汽通量](#3-大气湿度与水汽通量)
4. [引导气流计算](#4-引导气流计算)
5. [位涡 (PV) 诊断](#5-位涡-pv-诊断)
6. [潜在强度 (PI) 计算](#6-潜在强度-pi-计算)
7. [热力学环境诊断](#7-热力学环境诊断)

---

## 1. 海表温度 (SST) 分析

### SST 空间分布

```python
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# ERA5 SST
sst = xr.open_dataset('era5_sst.nc')['sst']

fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.coastlines()
cf = ax.contourf(sst.lon, sst.lat, sst.isel(time=0), levels=20, cmap='RdYlBu_r',
                 transform=ccrs.PlateCarree())
ax.plot(storm_lon, storm_lat, 'k*', markersize=15, transform=ccrs.PlateCarree())
# 标注 26.5°C 和 28°C 等温线
ax.contour(sst.lon, sst.lat, sst.isel(time=0), levels=[26.5, 28],
           colors='k', linewidths=1.5, transform=ccrs.PlateCarree())
```

### 台风冷尾迹 (Cold Wake)

台风经过后，海洋混合层翻混合产生 SST 冷异常，可降低后续台风的强度：

```python
def cold_wake_analysis(sst_before, sst_after, track):
    """计算台风经过前后的 SST 变化"""
    delta_sst = sst_after - sst_before
    # 沿路径提取冷尾迹
    return delta_sst

# 冷尾迹典型量级：1-3°C，强台风可达 4-6°C
# 冷尾迹可维持 5-10 天，对后续台风有"冷却效应"
```

**分析要点**：
- 26.5°C 是台风生成的传统阈值，但暖区(SST > 28°C)的台风更容易增强
- 海洋热含量(OHC)比 SST 更能反映海洋对台风的热力支持——深厚暖核海洋允许更强的台风
- 冷尾迹效应可解释连续台风路径上的强度变化（第二个台风可能因第一个台风留下的冷水而减弱）

---

## 2. 垂直风切变

### 深层切变 (200-850 hPa)

```python
import numpy as np

def deep_shear(u200, v200, u850, v850, storm_center, radius=200):
    """计算 200-850 hPa 深层切变
    u200/v200: 200hPa 风场
    u850/v850: 850hPa 风场
    storm_center: 台风中心位置
    radius: 环境平均半径 (km，通常 200-800 km)
    """
    # 在台风周围半径范围内做面积平均（去除涡旋本身的影响）
    u200_env = area_mean_around_center(u200, storm_center, radius)
    v200_env = area_mean_around_center(v200, storm_center, radius)
    u850_env = area_mean_around_center(u850, storm_center, radius)
    v850_env = area_mean_around_center(v850, storm_center, radius)

    du = u200_env - u850_env
    dv = v200_env - v850_env
    shear_mag = np.sqrt(du**2 + dv**2)
    shear_dir = np.degrees(np.arctan2(-du, -dv)) % 360  # 切变向量方向

    return shear_mag, shear_dir
```

### 切变阈值

| 切变强度 (m/s) | 对台风的影响 |
|---------------|-------------|
| < 5 | 极弱切变，台风容易增强，RI 有利条件之一 |
| 5-10 | 弱切变，台风可正常发展 |
| 10-15 | 中等切变，增强减缓，强台风难以维持 |
| 15-20 | 强切变，台风容易减弱，结构倾斜 |
| > 20 | 极强切变，台风结构严重破坏，难以增强 |

**科学提示**：切变方向对降水分布至关重要——对流在切变下风方更活跃，因此暴雨落区偏向切变下风方。切变方向 + 台风移动方向 = 降水最大方位角。在业务中，"切变下风方 + 移动右侧（北半球）"叠加方向通常是最大降水风险区。

---

## 3. 大气湿度与水汽通量

### 相对湿度廓线

```python
def humidity_profile(rh_field, storm_center, radius=500):
    """提取台风环境湿度廓线"""
    rh_env = area_mean_around_center(rh_field, storm_center, radius)
    return rh_env  # 各气压层的平均相对湿度

# 中层湿度 (700-500 hPa 平均) < 60% 不利于台风增强
# 高层湿度好 + 低层充分水汽输入 = 良好的湿热力学条件
```

### 水汽通量散度

```python
def moisture_flux_divergence(q, u, v, lats, lons):
    """计算水汽通量散度
    q: 比湿 (kg/kg)
    u, v: 风分量 (m/s)
    """
    import metpy.calc as mpcalc
    from metpy.units import units

    qu = q * u
    qv = q * v
    div = mpcalc.divergence(qu, qv)  # 水汽通量散度
    return div  # 正值 = 辐散(水汽减少), 负值 = 辐合(水汽增加)

# 积分 (1000-300 hPa) 得整层水汽通量散度
```

**分析要点**：
- 整层水汽辐合是台风降水的主要水汽来源
- 中层干燥空气侵入(dry air intrusion)可抑制对流，导致减弱
- 台风东侧的偏南风暖湿输送是登陆台风暴雨的关键水汽通道

---

## 4. 引导气流计算

### 深层平均引导气流

```python
def steering_flow(u_levels, v_levels, levels, storm_intensity='TS'):
    """计算深层平均引导气流
    u_levels, v_levels: 各层风场
    levels: 气压层 (hPa)
    storm_intensity: 'TD' | 'TS' | 'TY' | 'ST' (影响平均层选择)
    """
    # 不同强度台风的引导层范围（Galarneau & Kay 2010）
    layer_ranges = {
        'TD': (850, 700),
        'TS': (850, 500),
        'TY': (850, 300),
        'ST': (700, 200),  # 强台风的引导层更高
    }
    p_low, p_high = layer_ranges.get(storm_intensity, (850, 500))

    # 在引导层范围内做质量加权平均
    mask = (levels >= p_high) & (levels <= p_low)
    weights = levels[mask] / np.sum(levels[mask])
    u_steer = np.average(u_levels[mask], weights=weights)
    v_steer = np.average(v_levels[mask], weights=weights)

    speed = np.sqrt(u_steer**2 + v_steer**2)
    direction = np.degrees(np.arctan2(-u_steer, -v_steer)) % 360

    return u_steer, v_steer, speed, direction
```

### 引导气流与实际路径对比

```python
def steering_vs_actual(track, steering_series):
    """比较引导气流方向与实际移向
    track: 台风路径
    steering_series: 各时刻引导气流
    """
    actual_dir = calc_translation_direction(track)  # 移向
    steer_dir = [s['direction'] for s in steering_series]
    deviation = np.array(actual_dir) - np.array(steer_dir)
    return deviation
```

**科学提示**：引导气流偏差（steering deviation）反映涡旋运动偏离引导气流的程度。偏差来源包括：β漂移（使台风向极运动）、摩擦效应（使路径偏移）、对流强迫（涡旋不对称产生的运动偏差）。在弱引导气流（<5 m/s）时，偏差可达 30-60°，路径预报最困难。

---

## 5. 位涡 (PV) 诊断

### PV 计算

```python
import metpy.calc as mpcalc
from metpy.units import units

def potential_vorticity(theta, u, v, temp, levels, lats, lons):
    """计算 Ertel 位涡
    theta: 位温 (K)
    u, v: 风场
    temp: 温度
    levels: 气压层
    """
    # 绝对涡度 = 相对涡度 + 科氏参数
    avort = mpcalc.absolute_vorticity(u, v)
    # 静力稳定度 = -g * d(theta)/dp
    stability = mpcalc.static_stability(levels, temp)

    # PV = -g * (zeta + f) * d(theta)/dp
    # 或用 metpy 的内置函数
    pv = mpcalc.potential_vorticity_baroclinic(theta, u, v, temp, levels)
    return pv
```

### 高空 PV 异常与台风发展

```python
def pv_anomaly(pv_field, climatology):
    """计算 PV 异常"""
    return pv_field - climatology

# 高空 PV 异常（高空冷低压/高空正 PV 异常）
# 可通过下传促进台风发展——高空辐散 + 涡度下传机制
```

**科学提示**：高空 PV 异常对台风生成和快速增强有重要影响。PV 异常通过"位涡下传"机制——高空正 PV 异常诱导低层气旋性环流发展。典型情景是西风槽前的高空 PV 异常东移叠加到热带扰动上方，触发台风增强。

---

## 6. 潜在强度 (PI) 计算

### Emanuel 公式

```python
def potential_intensity(sst, t_profile, q_profile, ps, pe=50):
    """计算 Emanuel 潜在强度
    使用 Emanuel (1986, 1995) 热力学方法
    sst: 海表温度 (K)
    t_profile, q_profile: 大气温度和湿度廓线
    ps: 地面气压
    pe: 模式顶气压 (hPa)
    """
    # 简化版——实际需用 BE00.13 或 PI.py 程序
    # 核心计算：
    # 1. 计算卡诺热机效率 η = (Ts - To) / Ts
    #    Ts = SST, To = 对流层顶热力学温度
    # 2. 计算 CAPE* (饱和气块从海面上升的 CAPE)
    # 3. PI = sqrt(CAPE* * η / (Ck * Cd))

    # 此处给出概念性框架，完整实现建议用
    # Kerry Emanuel 的 pcmin.f90 或 Python 移植版
    pass
```

**使用说明**：
- 完整的 PI 计算建议使用 Kerry Emanuel 的 pcmin.f90 程序或 Python 移植版（如 `tcpyPI` 库）
- 输入数据：ERA5 的温度和湿度廓线 + SST
- 输出：最大潜在风速 (PI_V) 和最小潜在中心气压 (PI_P)
- PI 与实际强度的比较可反映台风的发展空间——当实际强度接近 PI 时，台风接近理论极限

---

## 7. 热力学环境诊断

### CAPE 和 CIN

```python
import metpy.calc as mpcalc
from metpy.units import units

def calc_cape_cin(pressure, temperature, dewpoint):
    """计算 CAPE 和 CIN"""
    cape, cin = mpcalc.cape_cin(pressure * units.hPa,
                                 temperature * units.kelvin,
                                 dewpoint * units.kelvin)
    return cape.m, cin.m
```

### 假相当位温 (θse)

```python
def theta_se(pressure, temperature, dewpoint):
    """假相当位温——反映大气的湿热力学状态"""
    theta_se = mpcalc.equivalent_potential_temperature(
        pressure * units.hPa,
        temperature * units.kelvin,
        dewpoint * units.kelvin
    )
    return theta_se.m
```

**分析要点**：
- CAPE > 1000 J/kg 有利于强对流发展
- 高 θse（>340 K）的湿舌从低层伸入台风区域是水汽和热力条件良好的标志
- 中层 θse 低值区（<320 K）指示干冷空气，可能抑制对流
- θse 廓线的对流不稳定（低层 θse > 高层 θse）是台风对流组织化的前提

---

## 注意事项

1. **环境场的定义**：环境场应该去除台风本身的影响。常用方法是在台风周围 200-800 km 范围内做面积平均，或用大尺度分析场（更大范围平均）。直接取中心点附近的环境场会受台风环流污染。
2. **时间匹配**：环境场分析需要与台风强度在时间上对齐。ERA5 每小时数据可满足精细分析需求。
3. **多重线性回归**：强度预报因子通常用多元线性回归做组合（如 SHIPS 方法），但因子间的共线性（如 SST 和 PI 高度相关）需要注意。
4. **环境场的气候态**：评估某次台风的环境条件是否"异常"，需要与同期气候态做对比——某次 RI 事件的环境条件可能只是"略好于气候态"，关键是多重因子的协同作用。
