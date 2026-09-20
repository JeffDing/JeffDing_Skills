# 强度与风场研究方法

## 目录

1. [强度时间序列分析](#1-强度时间序列分析)
2. [强度分级系统对照](#2-强度分级系统对照)
3. [风场结构分析](#3-风场结构分析)
4. [非对称风场重建](#4-非对称风场重建)
5. [眼壁与螺旋雨带识别](#5-眼壁与螺旋雨带识别)
6. [暖心结构诊断](#6-暖心结构诊断)
7. [Dvorak 技术](#7-dvorak-技术)

---

## 1. 强度时间序列分析

强度演变图是台风研究最基本的图表，展示 Vmax 和 Pmin 随时间变化：

```python
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(12, 5))
color1 = 'tab:red'
ax1.plot(df['time'], df['wmo_wind'], color=color1, linewidth=2, label='Vmax')
ax1.set_ylabel('Maximum Wind Speed (kt)', color=color1)
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx()
color2 = 'tab:blue'
ax2.plot(df['time'], df['wmo_pres'], color=color2, linewidth=2, label='Pmin')
ax2.set_ylabel('Minimum Sea Level Pressure (hPa)', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)
ax2.invert_yaxis()  # 气压越低越往上

# 标注生命史关键节点
ax1.axhline(y=64, color='gray', linestyle='--', alpha=0.5)  # 台风等级线
ax1.axhline(y=96, color='gray', linestyle='--', alpha=0.5)   # 强台风等级线
ax1.axhline(y=114, color='gray', linestyle='--', alpha=0.5) # 超强台风等级线
```

**分析要点**：
- 强度变化速率（dVmax/dt）比绝对强度更能反映发展/衰亡过程
- 快速增强(RI)定义为 30 kt/24h（Kaplan-DeMaria 标准），详见 `rapid_intensification.md`
- 强度和气压不一定完美耦合——"pressure-wind relationship"因气旋大小和环境而异
- 登陆后快速减弱率与下垫面摩擦、水汽供给中断有关

---

## 2. 强度分级系统对照

不同海域使用不同分级系统，做跨海域对比时需要统一：

| 等级 | CMA（西北太平洋） | SSHWS（大西洋/东太平洋） | JMA | 泛TC分类 |
|------|-------------------|------------------------|-----|---------|
| 热带低压(TD) | <17.2 m/s | <34 kt | <34 kt | 17-32 kt |
| 热带风暴(TS) | 17.2-24.4 m/s | 34-63 kt | 34-63 kt | 34-63 kt |
| 台风/飓风 Cat1 | 24.5-32.6 m/s | 64-82 kt | 34-47 kt | 64-82 kt |
| 强台风 Cat2 | 32.7-37.0 m/s | 83-95 kt | 40-47 kt | 83-95 kt |
| 强台风 Cat3 | 37.1-41.5 m/s | 96-112 kt | 44-47 kt | 96-112 kt |
| 超强台风 Cat4 | 41.6-46.1 m/s | 113-136 kt | 54-63 kt | 113-136 kt |
| 超强台风 Cat5 | ≥46.2 m/s | ≥137 kt | ≥64 kt | ≥137 kt |

**注意**：CMA 使用 2-min 平均风速，SSHWS 使用 1-min 平均，JMA 使用 10-min 平均。换算系数见 `data_sources.md`。

---

## 3. 风场结构分析

### 最大风速半径 (RMW)

RMW 是台风风场结构的关键参数，影响灾害评估和模式初始化：

```python
def calc_rmw(wind_profile, radii):
    """从方位角平均风廓线找最大风速半径
    wind_profile: 各半径处的方位角平均风速
    radii: 对应半径 (km)
    """
    idx = np.argmax(wind_profile)
    return radii[idx], wind_profile[idx]
```

### 风圈半径

JTWC/NHC 提供 34/50/64 kt 风圈半径，反映台风影响范围：

```python
def plot_wind_radii(quadrant_radii, quadrants=['NE','SE','SW','NW']):
    """绘制风圈四象限半径
    quadrant_radii: dict, {'NE': r, 'SE': r, 'SW': r, 'NW': r}
    """
    angles = [45, 135, 225, 315]  # NE, SE, SW, NW
    r_values = [quadrant_radii[q] for q in quadrants]
    # 转换为极坐标
    theta = np.radians(angles)
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.bar(theta, r_values, width=np.radians(60))
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)  # 顺时针
```

### 风场参数间经验关系

| 关系 | 经验公式 | 来源 |
|------|---------|------|
| Vmax-Pmin | Vmax = 3.7 × (1010 - Pmin)^0.6 | Atkinson & Holliday (1977) |
| RMW-Size | RMW 随气旋增大而增大 | 实际关系复杂，有反例 |
| ROCI-RMW | ROCI ≈ 2-3 × RMW | 大致范围，非严格关系 |
| Holland 模型 | V(r) = sqrt(B/ρ₀ × (Rmax/r)^B × (Pn-Pc) × exp(-(Rmax/r)^B) + (r×f/2)²) - r×f/2) | Holland (1980) |

**科学提示**：Holland (1980) 梯度风模型是台风风场重建的经典方法，但假设轴对称且梯度风平衡，不适用于非对称或强对流区。后续改进如 Holland (2010)、Emanuel-Rotunno (2011) 可处理更复杂的情况。

---

## 4. 非对称风场重建

台风风场可分解为轴对称分量和非对称扰动：

### 傅里叶分解

```python
def azimuthal_decompose(u_field, v_field, radii, azimuths):
    """将风场分解为轴对称+非对称分量
    u_field, v_field: (n_radii, n_azimuths) 风场
    radii: 半径数组 (km)
    azimuths: 方位角数组 (度)
    """
    # 转换为切向风和径向风
    az_rad = np.radians(azimuths)
    vt = -u_field * np.sin(az_rad) + v_field * np.cos(az_rad)  # 切向风
    vr = u_field * np.cos(az_rad) + v_field * np.sin(az_rad)   # 径向风

    # 方位角方向的傅里叶分解
    from numpy.fft import fft
    vt_sym = np.mean(vt, axis=1)  # 轴对称（波数0）
    vt_asym = vt - vt_sym[:, np.newaxis]

    # 波数1（偶极子）分量
    vt_fft = fft(vt, axis=1)
    vt_wave1 = np.real(vt_fft[:, 1])  # 波数1

    return vt_sym, vt_asym, vt_wave1
```

### 非对称性的物理来源

| 非对称分量 | 主要原因 | 诊断方法 |
|-----------|---------|---------|
| 波数1（移动方向非对称） | 涡旋移动效应（β漂移+摩擦） | 最大风在移动方向右侧（北半球） |
| 波数1（切变方向非对称） | 垂直风切变导致的对流偏移 | 切变下风方对流活跃 |
| 波数2 | 眼壁不闭合、双眼壁 | 卫星红外/微波图像 |
| 高波数 | 螺旋雨带 | 雷达/卫星降水 |

**科学提示**：非对称风场分析在台风研究中非常重要。移动方向非对称是最基本的——北半球台风移动方向右侧风更强（因为移动速度叠加到环流上）。垂直风切变造成的非对称则影响对流分布，进而影响降水分布（切变下风方降水更多）。

---

## 5. 眼壁与螺旋雨带识别

### 卫星图像识别

```python
# 使用卫星红外亮温识别眼壁和雨带
def identify_eyewall(ir_tb, lats, lons, storm_center):
    """通过红外亮温识别眼壁位置
    ir_tb: 亮温场 (K)
    storm_center: (lat, lon) 台风中心
    """
    # 计算各点到中心的距离
    dist = calc_distance(storm_center, lats, lons)  # km
    # 方位角平均亮温廓线
    az_mean_tb = azimuthal_mean(ir_tb, dist, r_bins=np.arange(0, 300, 5))
    # 眼壁 = 亮温极小值（冷云顶）附近的高梯度区
    gradient = np.gradient(az_mean_tb)
    eyewall_r = r_bins[np.argmin(az_mean_tb)]  # 粗略估计
    return eyewall_r, az_mean_tb
```

### 雷达识别

多普勒雷达是眼壁结构研究的主要工具：
- **眼壁**：高反射率环状结构（>40 dBZ），切向风极值区
- **双眼壁**：外眼壁形成后内眼壁减弱——眼壁置换过程
- **螺旋雨带**：从眼壁向外旋转的带状对流区

**科学提示**：眼壁置换(Eyewall Replacement Cycle, ERC)是强台风（Cat3+）的重要过程，会导致短暂减弱后再次增强。识别 ERC 对强度预报至关重要。

---

## 6. 暖心结构诊断

台风的暖心结构是其与温带气旋的根本区别：

```python
def warm_core_diagnosis(temp_field, storm_center, lats, lons, levels):
    """诊断台风暖心结构
    temp_field: (n_levels, n_lat, n_lon) 温度场
    levels: 气压层 (hPa)
    """
    # 找到中心位置对应的网格点
    ci, cj = find_nearest_grid(storm_center, lats, lons)
    # 暖心强度 = 中心温度 - 环境温度（取外围平均）
    r_env = 500  # 环境平均半径 km
    env_temp = azimuthal_mean_around_center(temp_field, storm_center, r_env)
    warm_anomaly = temp_field[:, ci, cj] - env_temp
    return warm_anomaly, levels
```

**分析要点**：
- 暖心在对流层中上层（300-200 hPa）最强，可达 +10°C 以上
- 暖心强度与台风强度正相关
- 暖心的维持机制：眼壁对流释放的潜热 + 绝热下沉增温
- 暖心不对称可指示垂直风切变的影响方向

---

## 7. Dvorak 技术

Dvorak (1975, 1984) 是基于卫星图像估计台风强度的经典方法，至今仍是业务定强的重要依据。

### 基本原理

1. **模式法**：利用云型特征（眼特征、云带弯曲程度、中心密蔽区）判定强度
2. **T指数**：从 1.0（弱）到 8.0（极强）的连续强度指数
3. **CI指数**：Current Intensity，考虑强度变化趋势的调整值

### T指数 → 强度换算

| T指数 | Vmax (kt) | Pmin (hPa) | 大致等级 |
|-------|-----------|-----------|---------|
| 2.0 | 30 | 1000 | TD |
| 2.5 | 35 | 997 | TS |
| 3.0 | 45 | 990 | TS/Cat1 |
| 4.0 | 65 | 974 | Cat1-2 |
| 5.0 | 90 | 948 | Cat3 |
| 6.0 | 115 | 915 | Cat4 |
| 7.0 | 140 | 880 | Cat5 |
| 8.0 | 165 | 850 | 极端 |

### 局限性

- 主观性：不同分析者可能给不同 T 指数
- 眼特征依赖：有清晰台风眼的系统定强较准，无眼或弱系统不确定性大
- 对流层顶温度假设：假设最强对流对应最强台风，但快速增强期可能滞后
- 现代 Automated Dvorak (ADT) 减少了主观性但仍存在系统性偏差

**科学提示**：在研究早期数据（1980s 前）时，强度数据主要来自 Dvorak 技术，需要考虑其系统性偏差。近年来 ADT 和 SATCON（融合多种卫星估计）在逐步改善，但最佳路径中的强度仍是台风研究中不确定性最大的变量之一。

---

## 注意事项

1. **风速-气压关系的不确定性**：经验公式（如 Atkinson-Holliday）在强台风时可能高估风速、低估气压。Emanuel (2003) 的理论关系在超强台风时可能更适用。
2. **不同数据源的强度差异**：同一台风，JTWC 通常给出比 JMA 更高的风速值（因 1-min vs 10-min 平均 + 定强方法差异）。做气候统计时必须使用单一数据源。
3. **风场重建的分辨率依赖**：再分析数据（ERA5 0.25°）无法解析台风内核结构，RMW 通常被高估。高分辨率模式或观测（雷达/卫星）更适合内核研究。
4. **登陆台风的风场变形**：登陆后摩擦增大、水汽减少，风场结构急剧变化。需注意轴对称假设失效，非对称性增强。
