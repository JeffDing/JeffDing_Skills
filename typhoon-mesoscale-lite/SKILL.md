---
name: typhoon-mesoscale-lite
description: 用于台风（热带气旋）科研研究的系统性工作流，纯 SKILL.md 实现。涵盖路径研究、强度与风场、降水分析、环境场诊断、气候统计与趋势、数值模拟与预报检验、灾害影响评估、快速增强(RI)分析、文献搜索与综述生成。当用户提到台风/热带气旋/飓风/气旋的研究、分析、可视化、路径追踪、强度分析、降水研究、气候统计、文献综述、WRF模拟、ERA5再分析、GPM降水、IBTrACS数据、CMA/JMA/JTWC最佳路径、SHIPS因子、Mann-Kendall趋势检验、RI快速增强诊断、路径聚类、风暴潮评估、灾害评估、台风报告撰写、台风个例分析、台风对比研究、台风生成潜势、台风-ENSO关系、台风未来预估、CMIP6台风分析、深度学习台风预报，或涉及西北太平洋/南海/北大西洋/北印度洋/全球台风数据分析时，务必使用此 skill。即使用户只是提到"台风研究"、"气旋分析"、"热带气旋科研"而未明确具体方向，也应触发此 skill 以引导用户进入完整的研究工作流。不要只做简单的单步数据处理，要用此 skill 提供完整的研究分析框架。
---

# 台风中尺度系统科研研究

## 概述

本 skill 为台风（热带气旋）科研研究提供系统化的工作流，覆盖从数据获取、分析可视化到文献综述的完整流程。适用于气象/大气科学领域的研究人员，支持西北太平洋、北大西洋、东北太平洋、北印度洋、南半球等全球各海域。

设计理念：**方法论导向**，而非简单的画图工具——每个研究维度都包含科学背景、标准方法、关键指标和注意事项，帮助研究者做出规范、可发表的分析。

本 skill 为纯文本实现，所有方法学内容直接内联在本文档中，无需外部脚本或模板文件。代码以指导性片段和生成原则形式提供，用户可根据具体数据和研究需求自行实现。

---

## 核心工作流程

### 第一步：确定研究海域

首先询问用户（或从上下文推断）研究哪个海域。不同海域对应不同的最佳路径数据源和机构预报：

| 海域 | 主要机构 | 最佳路径数据 | 特殊说明 |
|------|---------|-------------|---------|
| 西北太平洋（含南海） | CMA / JMA / JTWC | CMA-STI Best Track, JMA, JTWC | 中国台风委员会命名体系 |
| 北大西洋 | NHC | HURDAT2 | Saffir-Simpson 分级 |
| 东北太平洋 | NHC | HURDAT2 | |
| 北印度洋 | IMD | IMD RSMC | 双季风季 |
| 南太平洋/南印度洋 | 各区域中心 | IBTrACS | 无统一命名规范 |
| 全球 | — | IBTrACS (NOAA) | 整合各机构数据 |

### 第二步：确定研究维度

根据用户需求识别一个或多个研究维度：

| # | 研究维度 | 典型用户表述 | 详细方法见 |
|---|---------|-------------|-----------|
| 1 | 路径研究 | "台风路径""轨迹分析""路径相似性" | 下方"1. 路径研究" |
| 2 | 强度与风场 | "强度变化""最大风速""风场结构""眼壁" | 下方"2. 强度与风场研究" |
| 3 | 降水分析 | "降雨分布""暴雨""降水非对称性""GPM" | 下方"3. 降水分析" |
| 4 | 环境场诊断 | "SST""垂直切变""引导气流""湿度" | 下方"4. 环境场诊断" |
| 5 | 气候统计与趋势 | "频数变化""长期趋势""ENSO""气候态" | 下方"5. 气候统计与趋势" |
| 6 | 数值模拟与预报检验 | "WRF""预报误差""模式对比""检验" | 下方"6. 数值模拟与预报检验" |
| 7 | 灾害影响评估 | "风灾""暴雨灾害""经济损失""伤亡" | 下方"7. 灾害影响评估" |
| 8 | 快速增强(RI) | "快速增强""RI""SHIPS""骤然增强" | 下方"8. 快速增强(RI)分析" |

用户可能同时涉及多个维度——例如"分析台风 Hato 的路径和降水特征"涉及维度 1+3。

### 第三步：数据获取

根据海域和研究维度，确定需要哪些数据：

- **最佳路径数据**：IBTrACS（全球）、CMA-STI（西北太平洋）、HURDAT2（大西洋/东太平洋）
- **再分析数据**：ERA5（最常用）、JRA-55、MERRA-2
- **卫星降水**：GPM IMERG（近实时+研究级）、TRMM 3B42（历史）
- **卫星风场**：ASCAT、RapidScan、SMAP
- **数值模式输出**：WRF、GFS、ECMWF-IFS
- **预报数据**：各机构官方预报、SHIPS 统计-动力预报

具体下载方式、变量清单、格式说明见下方"数据源速查"。

若用户提供了本地数据文件，跳过下载步骤，直接进入分析。

### 第四步：分析与可视化

根据研究维度，阅读下方对应的方法学章节了解标准方法，然后：

1. **生成代码**：本 skill 提供各研究维度的标准方法和代码框架。根据用户偏好语言生成对应代码（Python/NCL/GrADS/MATLAB/R），或使用用户提供的环境直接运行。
2. **执行分析**：运行代码处理数据，生成中间结果和图表。
3. **方法学引导**：不仅是画图——在分析过程中提醒用户关注科学意义，如"路径北翘可能与副热带高压断裂有关""降水非对称性需考虑地形和环境风切变"。

### 第五步：文献搜索与综述

详见下方"文献搜索工作流"。

### 第六步：输出

根据任务性质选择输出格式，详见下方"输出格式指南"。

## 研究维度索引

以下为各维度的简要说明，完整方法学在对应章节中。

### 1. 路径研究

- 最佳路径数据读取与解析（IBTrACS CSV、CMA 格式）
- 路径可视化：轨迹图、彩色路径（按强度/时间着色）
- 路径相似性分析：动态时间规整(DTW)、Hausdorff 距离
- 路径聚类：K-means、层次聚类
- 移速移向计算与统计
- 路径预报误差评估：逐时/逐 24h 误差、引导气流对比

#### 1.1 最佳路径数据读取与解析

IBTrACS NetCDF 读取：

```python
import xarray as xr
import pandas as pd

ds = xr.open_dataset('IBTrACS.ALL.v04r00.nc')
# 筛选西北太平洋
wp = ds.where(ds['basin'] == 'WP', drop=True)
# 提取单个台风
storm = wp.isel(storm=wp['name'].values == 'HATO')
# 转为 DataFrame
df = storm[['time', 'lat', 'lon', 'wmo_wind', 'wmo_pres']].to_dataframe()
```

CMA Best Track 解析：
CMA 数据为类 ATCF 的文本格式，每行包含编号、时间、位置、强度等。

```python
col_names = ['id', 'name', 'time', 'grade', 'lat', 'lon', 'pres', 'wnd', 'wnd_dir']
df = pd.read_csv('CMA_BST.txt', sep='\s+', names=col_names, na_values='9')
# lat/lon 格式：度*10（如 152 = 15.2°），方向由符号判断
df['lat'] = df['lat'] / 10.0
df['lon'] = df['lon'] / 10.0
```

风速统一化：
做跨机构分析前，将所有风速统一到同一标准（推荐 10-min 平均）。

```python
def unify_to_10min(wnd, source):
    factors = {'JTWC': 1/1.14, 'CMA': 1/1.10, 'JMA': 1.0, 'NHC': 1/1.14}
    return wnd * factors.get(source, 1.0)
```

#### 1.2 路径可视化

基本路径图（Python + Cartopy）：

```python
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax.coastlines(resolution='50m')
ax.set_extent([100, 160, 5, 45], crs=ccrs.PlateCarree())
ax.gridlines(draw_labels=True)

# 按强度着色
sc = ax.scatter(df['lon'], df['lat'], c=df['wmo_wind'],
                cmap='YlOrRd', transform=ccrs.PlateCarree())
ax.plot(df['lon'], df['lat'], 'k-', linewidth=0.8, transform=ccrs.PlateCarree())
plt.colorbar(sc, label='Maximum Wind Speed (kt)')
```

多路径叠加：
适合展示某一时期的路径特征或路径聚类结果。

```python
for storm_id, group in all_storms.groupby('sid'):
    ax.plot(group['lon'], group['lat'], transform=ccrs.PlateCarree(), alpha=0.5)
```

路径密度图：
用核密度估计展示路径气候态。

```python
from scipy.stats import gaussian_kde
kde = gaussian_kde(np.vstack([df['lon'], df['lat']]), bw_method=0.15)
# 在网格上评估
xi, yi = np.mgrid[100:160:200j, 5:45:200j]
zi = kde(np.vstack([xi.ravel(), yi.ravel()])).reshape(xi.shape)
ax.contourf(xi, yi, zi, levels=15, cmap='YlOrRd', transform=ccrs.PlateCarree())
```

#### 1.3 移速移向计算

```python
from metpy.calc import wind_components
from metpy.units import units
import numpy as np

def calc_translation(df):
    """计算台风移速移向"""
    R = 6371  # 地球半径 km
    lat1, lon1 = np.radians(df['lat'].shift()), np.radians(df['lon'].shift())
    lat2, lon2 = np.radians(df['lat']), np.radians(df['lon'])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Haversine 公式
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    d = 2 * R * np.arcsin(np.sqrt(a))
    dt_hours = (df['time'] - df['time'].shift()).dt.total_seconds() / 3600
    speed = d / dt_hours  # km/h
    # 移向（气象学风向：0=北，顺时针）
    bearing = np.degrees(np.arctan2(np.sin(dlon) * np.cos(lat2),
                     np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)))
    bearing = (bearing + 360) % 360
    return speed, bearing
```

科学提示：
移速变化与引导气流变化相关联。路径突然北翘/西折通常意味着引导气流的改变（如副高断裂、冷空气侵入、季风涌增强），值得在分析中关注这些天气学背景。

#### 1.4 路径相似性分析

动态时间规整 (DTW)：
DTW 能处理长度不同的路径序列，是路径相似性的常用方法。

```python
from scipy.spatial.distance import cdist

def dtw_distance(track1, track2):
    """track1, track2: [(lat, lon), ...]"""
    n, m = len(track1), len(track2)
    D = cdist(track1, track2, metric='euclidean')
    # 动态规划
    acc = np.full((n+1, m+1), np.inf)
    acc[0, 0] = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            acc[i, j] = D[i-1, j-1] + min(acc[i-1, j], acc[i, j-1], acc[i-1, j-1])
    return acc[n, m] / max(n, m)
```

Hausdorff 距离：
衡量两条路径之间的最大不匹配程度。

```python
from scipy.spatial.distance import directed_hausdorff

def hausdorff_dist(track1, track2):
    d1 = directed_hausdorff(track1, track2)[0]
    d2 = directed_hausdorff(track2, track1)[0]
    return max(d1, d2)
```

应用：
路径相似性分析常用于——历史相似台风检索（"今年第 X 号台风的路径历史上有没有类似的"）、路径预报集成（找历史相似路径的最终归宿）、路径分类研究。

#### 1.5 路径聚类

K-means + DTW：

```python
from sklearn.cluster import KMeans

def cluster_tracks(tracks, n_clusters=4):
    """tracks: list of [(lat, lon), ...]"""
    # 计算两两 DTW 距离矩阵
    n = len(tracks)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            dist_matrix[i, j] = dtw_distance(tracks[i], tracks[j])
            dist_matrix[j, i] = dist_matrix[i, j]
    # 用距离矩阵做 K-means（需自定义或用 precomputed）
    from sklearn.cluster import SpectralClustering
    sc = SpectralClustering(n_clusters=n_clusters, affinity='precomputed',
                           random_state=42)
    labels = sc.fit_predict(-dist_matrix)  # 负距离作为相似度
    return labels
```

层次聚类：
适合路径自然分类，无需预设类别数。

```python
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram

Z = linkage(dist_matrix, method='ward')
labels = fcluster(Z, t=4, criterion='maxclust')
```

科学提示：
西北太平洋台风路径通常可归纳为西行型、西北行型、转向型和异常型，聚类结果应与副高脊线位置、西风槽活动和季风涌位置等大尺度环流型态对应。如果聚类结果与已知天气学型态不一致，可能需要检查数据预处理或聚类参数。

#### 1.6 路径预报误差评估

逐时绝对误差：

```python
def track_error(fcst_lon, fcst_lat, best_lon, best_lat):
    """计算路径预报的绝对误差 (km)"""
    R = 6371
    lat1, lat2 = np.radians(fcst_lat), np.radians(best_lat)
    dlat = np.radians(best_lat - fcst_lat)
    dlon = np.radians(best_lon - fcst_lon)
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))
```

技巧评分：

```python
def skill_score(model_error, baseline_error):
    """相对于基准（如 CLIPER）的技巧评分 (%)"""
    return (1 - model_error / baseline_error) * 100
```

评估指标：

| 指标 | 含义 | 计算方式 |
|------|------|---------|
| 24h/48h/72h 路径误差 | 各预报时效的平均误差 | 逐时大圆距离 |
| 技巧评分 | 相对于基准预报的改进程度 | (1 - 模型误差/基准误差) × 100% |
| 路向偏差 | 预报方向偏离程度 | 移向角度差 |
| 移速偏差 | 预报移速偏离程度 | 预报移速 - 最佳路径移速 |
| 稳定度 | 集合预报路径发散程度 | 各成员路径间 DTW 距离均值 |

标准基准：
- CLIPER（气候-持续性预报）是路径预报的标准基准，技巧评分为 0
- 技巧评分 > 0 表示优于纯统计方法
- 全球模式路径预报技巧在 72h 内可达 30-50%，而区域模式在近海可能更高

### 2. 强度与风场研究

- 强度时间序列：Vmax、Pmin 演变曲线
- 强度分级与等级转换：CMA/SSHWS/泛热带气旋分级对照
- 风场结构分析：最大风速半径(RMW)、34/50/64 kt 风圈半径
- 非对称风场重建：轴对称平均 + 傅里叶分解
- 眼壁与螺旋雨带识别
- 暖心结构诊断
- Dvorak 技术（卫星强度估计）原理与局限性

#### 2.1 强度时间序列分析

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

分析要点：
- 强度变化速率（dVmax/dt）比绝对强度更能反映发展/衰亡过程
- 快速增强(RI)定义为 30 kt/24h（Kaplan-DeMaria 标准），详见快速增强章节
- 强度和气压不一定完美耦合——"pressure-wind relationship"因气旋大小和环境而异
- 登陆后快速减弱率与下垫面摩擦、水汽供给中断有关

#### 2.2 强度分级系统对照

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

注意：
CMA 使用 2-min 平均风速，SSHWS 使用 1-min 平均，JMA 使用 10-min 平均。换算系数见数据源速查部分。

#### 2.3 风场结构分析

最大风速半径 (RMW)：
RMW 是台风风场结构的关键参数，影响灾害评估和模式初始化。

```python
def calc_rmw(wind_profile, radii):
    """从方位角平均风廓线找最大风速半径
    wind_profile: 各半径处的方位角平均风速
    radii: 对应半径 (km)
    """
    idx = np.argmax(wind_profile)
    return radii[idx], wind_profile[idx]
```

风圈半径：
JTWC/NHC 提供 34/50/64 kt 风圈半径，反映台风影响范围。

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

风场参数间经验关系：

| 关系 | 经验公式 | 来源 |
|------|---------|------|
| Vmax-Pmin | Vmax = 3.7 × (1010 - Pmin)^0.6 | Atkinson & Holliday (1977) |
| RMW-Size | RMW 随气旋增大而增大 | 实际关系复杂，有反例 |
| ROCI-RMW | ROCI ≈ 2-3 × RMW | 大致范围，非严格关系 |
| Holland 模型 | V(r) = sqrt(B/ρ₀ × (Rmax/r)^B × (Pn-Pc) × exp(-(Rmax/r)^B) + (r×f/2)²) - r×f/2) | Holland (1980) |

科学提示：
Holland (1980) 梯度风模型是台风风场重建的经典方法，但假设轴对称且梯度风平衡，不适用于非对称或强对流区。后续改进如 Holland (2010)、Emanuel-Rotunno (2011) 可处理更复杂的情况。

#### 2.4 非对称风场重建

台风风场可分解为轴对称分量和非对称扰动：

傅里叶分解：

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

非对称性的物理来源：

| 非对称分量 | 主要原因 | 诊断方法 |
|-----------|---------|---------|
| 波数1（移动方向非对称） | 涡旋移动效应（β漂移+摩擦） | 最大风在移动方向右侧（北半球） |
| 波数1（切变方向非对称） | 垂直风切变导致的对流偏移 | 切变下风方对流活跃 |
| 波数2 | 眼壁不闭合、双眼壁 | 卫星红外/微波图像 |
| 高波数 | 螺旋雨带 | 雷达/卫星降水 |

科学提示：
非对称风场分析在台风研究中非常重要。移动方向非对称是最基本的——北半球台风移动方向右侧风更强（因为移动速度叠加到环流上）。垂直风切变造成的非对称则影响对流分布，进而影响降水分布（切变下风方降水更多）。

#### 2.5 眼壁与螺旋雨带识别

卫星图像识别：

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

雷达识别：
多普勒雷达是眼壁结构研究的主要工具：
- **眼壁**：高反射率环状结构（>40 dBZ），切向风极值区
- **双眼壁**：外眼壁形成后内眼壁减弱——眼壁置换过程
- **螺旋雨带**：从眼壁向外旋转的带状对流区

科学提示：
眼壁置换(Eyewall Replacement Cycle, ERC)是强台风（Cat3+）的重要过程，会导致短暂减弱后再次增强。识别 ERC 对强度预报至关重要。

#### 2.6 暖心结构诊断

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

分析要点：
- 暖心在对流层中上层（300-200 hPa）最强，可达 +10°C 以上
- 暖心强度与台风强度正相关
- 暖心的维持机制：眼壁对流释放的潜热 + 绝热下沉增温
- 暖心不对称可指示垂直风切变的影响方向

#### 2.7 Dvorak 技术

Dvorak (1975, 1984) 是基于卫星图像估计台风强度的经典方法，至今仍是业务定强的重要依据。

基本原理：
1. **模式法**：利用云型特征（眼特征、云带弯曲程度、中心密蔽区）判定强度
2. **T指数**：从 1.0（弱）到 8.0（极强）的连续强度指数
3. **CI指数**：Current Intensity，考虑强度变化趋势的调整值

T指数 → 强度换算：

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

局限性：
- 主观性：不同分析者可能给不同 T 指数
- 眼特征依赖：有清晰台风眼的系统定强较准，无眼或弱系统不确定性大
- 对流层顶温度假设：假设最强对流对应最强台风，但快速增强期可能滞后
- 现代 Automated Dvorak (ADT) 减少了主观性但仍存在系统性偏差

科学提示：
在研究早期数据（1980s 前）时，强度数据主要来自 Dvorak 技术，需要考虑其系统性偏差。近年来 ADT 和 SATCON（融合多种卫星估计）在逐步改善，但最佳路径中的强度仍是台风研究中不确定性最大的变量之一。

强度与风场研究注意事项：
1. **风速-气压关系的不确定性**：经验公式（如 Atkinson-Holliday）在强台风时可能高估风速、低估气压。Emanuel (2003) 的理论关系在超强台风时可能更适用。
2. **不同数据源的强度差异**：同一台风，JTWC 通常给出比 JMA 更高的风速值（因 1-min vs 10-min 平均 + 定强方法差异）。做气候统计时必须使用单一数据源。
3. **风场重建的分辨率依赖**：再分析数据（ERA5 0.25°）无法解析台风内核结构，RMW 通常被高估。高分辨率模式或观测（雷达/卫星）更适合内核研究。
4. **登陆台风的风场变形**：登陆后摩擦增大、水汽减少，风场结构急剧变化。需注意轴对称假设失效，非对称性增强。

### 3. 降水分析

- 卫星降水数据处理：GPM IMERG（Final/Late/Early Run）、TRMM 3B42/3B43
- 降水空间分布：等值线图、填色图
- 降水时间演变：Hovmöller 图、面积平均降水时间序列
- 降水非对称性分析：方位角-半径分布、傅里叶分解
- 地形增强效应诊断
- 极端降水统计：GEV/GPD 拟合、重现期计算
- 降水形态分类：层状/对流性（利用 TRMM PR/GPM DPR）

#### 3.1 卫星降水数据处理

GPM IMERG Final Run 读取：

```python
import xarray as xr
import glob

# 读取单文件
ds = xr.open_dataset('3B-HHR.MS.MRG.3IMERG.20180823-S120000-E122959.0720.V07B.HDF5')

# IMERG 的降水量变量名：precipitationCal（校正后）或 precipitationUncal
precip = ds['precipitationCal']  # mm/hr
lats = ds['lat'].values
lons = ds['lon'].values

# 多文件时间序列合并
files = sorted(glob.glob('3B-HHR.*.HDF5'))
ds_list = [xr.open_dataset(f) for f in files]
combined = xr.concat(ds_list, dim='time')
```

台风区域裁剪：

```python
def extract_tc_region(precip, storm_center, radius_deg=10):
    """提取台风影响区域的降水
    storm_center: (lat, lon)
    radius_deg: 影响半径 (度，约 10 度 ≈ 1100 km)
    """
    lat_c, lon_c = storm_center
    precip_tc = precip.sel(
        lat=slice(lat_c - radius_deg, lat_c + radius_deg),
        lon=slice(lon_c - radius_deg, lon_c + radius_deg)
    )
    return precip_tc
```

累积降水计算：

```python
# 24小时累积降水
daily_precip = precip_tc.resample(time='24h').sum()

# 台风生命史累积降水
total_precip = precip_tc.sum(dim='time')

# 跟随台风中心的移动累计降水（需逐时移动窗口）
def moving_accumulation(precip, track_df, radius_deg=5):
    """沿台风路径计算移动累积降水"""
    result = []
    for _, row in track_df.iterrows():
        t = row['time']
        lat_c, lon_c = row['lat'], row['lon']
        region = precip.sel(time=t, method='nearest').sel(
            lat=slice(lat_c - radius_deg, lat_c + radius_deg),
            lon=slice(lat_c - radius_deg, lon_c + radius_deg)
        )
        result.append({'time': t, 'mean_precip': float(region.mean()),
                       'max_precip': float(region.max())})
    return pd.DataFrame(result)
```

#### 3.2 降水空间分布

等值线填色图：

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.coastlines(resolution='50m')
ax.gridlines(draw_labels=True)

# 标注台风中心位置
ax.plot(storm_lon, storm_lat, 'k*', markersize=15, transform=ccrs.PlateCarree())

# 降水填色
levels = [0, 10, 25, 50, 100, 200, 300, 500]
cf = ax.contourf(lons, lats, precip_2d, levels=levels,
                 cmap='jet', extend='max', transform=ccrs.PlateCarree())
plt.colorbar(cf, label='Precipitation (mm)')
```

极坐标降水分布：

```python
def polar_precip(precip_2d, lats, lons, center_lat, center_lon,
                 r_max=500, dr=10, daz=5):
    """将降水转换为极坐标（以台风中心为原点）
    返回: (r, az, precip_polar)
    """
    r_bins = np.arange(0, r_max+dr, dr)
    az_bins = np.arange(0, 360+daz, daz)
    precip_polar = np.full((len(r_bins)-1, len(az_bins)-1), np.nan)

    for i in range(len(lats)):
        for j in range(len(lons)):
            dist = haversine(center_lat, center_lon, lats[i], lons[j])
            bearing = calc_bearing(center_lat, center_lon, lats[i], lons[j])
            ri = np.digitize(dist, r_bins) - 1
            ai = np.digitize(bearing, az_bins) - 1
            if 0 <= ri < len(r_bins)-1 and 0 <= ai < len(az_bins)-1:
                if np.isnan(precip_polar[ri, ai]):
                    precip_polar[ri, ai] = precip_2d[i, j]
                else:
                    precip_polar[ri, ai] = np.nanmean([precip_polar[ri, ai], precip_2d[i, j]])

    return r_bins[:-1], az_bins[:-1], precip_polar
```

#### 3.3 降水时间演变

Hovmöller 图：
Hovmöller 图展示降水随时间和半径（或方位角）的演变，是台风降水诊断的经典工具。

```python
def hovmoller_radius_time(precip_polar_series, r_bins):
    """半径-时间 Hovmöller 图
    precip_polar_series: list of (n_r, n_az) arrays, 各时刻极坐标降水
    """
    # 方位角平均
    az_mean = [np.nanmean(p, axis=1) for p in precip_polar_series]
    hov = np.array(az_mean).T  # (n_r, n_t)

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.pcolormesh(times, r_bins, hov, cmap='jet', vmin=0, vmax=50)
    ax.set_xlabel('Time')
    ax.set_ylabel('Radius (km)')
    ax.set_title('Radius-Time Hovmöller of Azimuthal Mean Precipitation')
    plt.colorbar(im, label='Precipitation (mm/hr)')
```

方位角-时间 Hovmöller：

```python
def hovmoller_azimuth_time(precip_polar_series, az_bins, r_range=(50, 200)):
    """方位角-时间 Hovmöller 图（固定半径范围）"""
    r_idx = (r_bins >= r_range[0]) & (r_bins <= r_range[1])
    r_mean = [np.nanmean(p[r_idx, :], axis=0) for p in precip_polar_series]
    hov = np.array(r_mean).T  # (n_az, n_t)

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.pcolormesh(times, az_bins, hov, cmap='jet', vmin=0, vmax=30)
    ax.set_xlabel('Time')
    ax.set_ylabel('Azimuth (°)')
    ax.set_title(f'Azimuth-Time Hovmöller ({r_range[0]}-{r_range[1]} km)')
    plt.colorbar(im, label='Precipitation (mm/hr)')
```

科学提示：
Hovmöller 图能揭示——眼壁置换过程中降水双峰结构的时间演变、螺旋雨带的旋转传播（方位角方向的波动）、外雨带向内传播的对流信号。半径-时间图中的向内传播通常与涡旋罗斯贝波有关。

#### 3.4 降水非对称性分析

方位角分布与傅里叶分解：

```python
def precip_asymmetry(precip_polar, r_range=(50, 200)):
    """分析降水在固定半径范围内的方位角非对称性"""
    r_idx = (r_bins >= r_range[0]) & (r_bins <= r_range[1])
    az_profile = np.nanmean(precip_polar[r_idx, :], axis=0)  # 方位角廓线

    # 傅里叶分解
    from numpy.fft import fft
    n = len(az_profile)
    fft_coeffs = fft(az_profile)
    asym_0 = np.real(fft_coeffs[0]) / n  # 轴对称
    asym_1 = np.abs(fft_coeffs[1]) / n * 2  # 波数1振幅
    asym_2 = np.abs(fft_coeffs[2]) / n * 2  # 波数2振幅

    # 波数1的方向（最大降水方位角）
    phase_1 = np.angle(fft_coeffs[1])
    max_az = (np.degrees(phase_1) % 360)

    return {'symmetric': asym_0, 'waven1_amp': asym_1, 'waven1_az': max_az,
            'waven2_amp': asym_2, 'profile': az_profile}
```

非对称性的物理来源：

| 非对称分量 | 典型方向 | 物理机制 |
|-----------|---------|---------|
| 移动方向非对称 | 移动方向右侧（北半球） | 涡旋移动速度叠加 |
| 切变方向非对称 | 切变下风方 | 深对流在切变下风方发展 |
| 地形非对称 | 迎风坡 | 地形抬升增强降水 |
| 内核非对称 | 随时间变化 | 涡旋罗斯贝波、VHTs组织化 |

分析要点：
- 降水非对称性在台风登陆时最强（地形+摩擦+移动效应叠加）
- 切变下风方降水增强是业务预报关注重点——切变方向决定了暴雨落区
- 分离各因子的贡献需要：比较陆地/海洋台风、改变切变方向、对比有无地形

#### 3.5 地形增强效应诊断

```python
def orographic_enhancement(precip_field, topo_field, lats, lons, storm_track):
    """诊断地形对台风降水的影响
    precip_field: 降水场
    topo_field: 地形高度场
    storm_track: 台风路径
    """
    # 计算坡度方向与水汽通量的点积
    # 水汽通量方向 ≈ 台风环流方向（切向风为主）
    # 迎风坡：dot_product > 0 → 地形增强
    # 背风坡：dot_product < 0 → 地形减弱

    # 1. 计算地形坡度
    grad_topo_y, grad_topo_x = np.gradient(topo_field)
    # 2. 在每个格点计算地形-风夹角
    # 3. 迎风坡降水量与地形高度的关系
    # ...

    # 简化版：比较迎风坡和背风坡降水量
    pass

# 更实用的方法：对比有地形 vs 平滑地形模式模拟
```

科学提示：
地形增强是台风暴雨预报的核心难点。中国台湾岛、菲律宾吕宋岛、日本本州岛、中国东南沿海丘陵对台风降水有显著增强作用。典型量级：台湾中央山脉可使降水增幅 2-3 倍。地形效应与台风移速有关——慢速移动台风有更充分的地形抬升时间。

#### 3.6 极端降水统计

年最大值序列 (AMS)：

```python
def annual_max_series(daily_precip_series, threshold=None):
    """构建年最大降水序列"""
    yearly_max = daily_precip_series.resample('Y').max()
    return yearly_max
```

GEV 拟合（广义极值分布）：

```python
from scipy.stats import genextreme

def fit_gev(ams):
    """拟合 GEV 分布
    ams: 年最大降水序列
    """
    shape, loc, scale = genextreme.fit(ams)
    # 返回重现期
    return_periods = [10, 20, 50, 100, 200]
    return_levels = genextreme.ppf(1 - 1/rp, shape, loc=loc, scale=scale
                                    for rp in return_periods)
    return {'shape': shape, 'loc': loc, 'scale': scale,
            'return_periods': return_periods, 'return_levels': return_levels}
```

GPD 拟合（超阈值模型，POT）：

```python
from scipy.stats import genpareto

def fit_gpd(precip_series, threshold):
    """超阈值法拟合 GPD
    threshold: 阈值（如 95th 百分位）
    """
    exceedances = precip_series[precip_series > threshold] - threshold
    shape, loc, scale = genpareto.fit(exceedances, floc=0)
    return {'shape': shape, 'scale': scale, 'threshold': threshold}
```

方法选择：
- GEV（年最大值法）：适合较长记录（>20年），稳定性好但采样效率低
- GPD（超阈值法）：适合较短记录，采样效率高但阈值选择敏感
- 台风降水的极端性通常比一般降水更强，GEV/GPD 的形状参数可能为正（重尾分布）

#### 3.7 降水形态分类

利用 GPM DPR（双频降水雷达）或 TRMM PR 可区分对流性/层状性降水：

```python
def classify_precip_type(dpr_data):
    """GPM DPR 降水类型分类
    dpr_data: 含 typePrecip 变量的数据
    typePrecip: 0=无降水, 1=层状, 2=对流, 3=其他
    """
    stratiform = dpr_data.where(dpr_data['typePrecip'] == 1)
    convective = dpr_data.where(dpr_data['typePrecip'] == 2)

    # 计算各类型占比
    total = dpr_data['precipRate'].count()
    strat_frac = stratiform['precipRate'].count() / total * 100
    conv_frac = convective['precipRate'].count() / total * 100

    return strat_frac, conv_frac
```

科学提示：
台风降水中层状性降水通常占面积 70-80%，但贡献总降水约 50-60%；对流性降水面积占 20-30%，但贡献 40-50%。眼壁主要是对流性降水，外雨带以层状性为主。降水形态的演变与台风强度变化有关——减弱的台风往往对流比例下降。

降水分析注意事项：
1. **IMERG 数据的不确定性**：GPM IMERG 在强降水（>50 mm/hr）时可能低估，在弱降水时可能高估。地形区的卫星反演精度更差。建议用地面雨量站数据做验证。
2. **时间匹配**：IMERG 是 30 分钟数据，最佳路径是 6 小时间隔。做相关分析时需统一时间分辨率。
3. **陆地 vs 海洋精度**：IMERG 在海洋上精度较好（无地形干扰），陆地上受地形和岸基影响，误差增大。
4. **极端事件评估**：单个台风的极端降水不能简单归因于气候变化——需要用归因方法（如条件归因法）区分气候变率和自然变率的贡献。

### 4. 环境场诊断

- 海表温度(SST)：空间分布、台风冷尾迹(SST cooling)
- 垂直风切变：200-850 hPa 切变计算、深层/浅层切变
- 大气湿度：相对湿度廓线、水汽输送
- 引导气流：深层平均气流计算
- 位涡(PV)：高空 PV 异常与台风发展
- 潜在强度(PI)：Emanuel 公式计算
- 热力学环境：CAPE、CIN、假相当位温

#### 4.1 海表温度 (SST) 分析

SST 空间分布：

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

台风冷尾迹 (Cold Wake)：
台风经过后，海洋混合层翻混合产生 SST 冷异常，可降低后续台风的强度。

```python
def cold_wake_analysis(sst_before, sst_after, track):
    """计算台风经过前后的 SST 变化"""
    delta_sst = sst_after - sst_before
    # 沿路径提取冷尾迹
    return delta_sst

# 冷尾迹典型量级：1-3°C，强台风可达 4-6°C
# 冷尾迹可维持 5-10 天，对后续台风有"冷却效应"
```

分析要点：
- 26.5°C 是台风生成的传统阈值，但暖区(SST > 28°C)的台风更容易增强
- 海洋热含量(OHC)比 SST 更能反映海洋对台风的热力支持——深厚暖核海洋允许更强的台风
- 冷尾迹效应可解释连续台风路径上的强度变化（第二个台风可能因第一个台风留下的冷水而减弱）

#### 4.2 垂直风切变

深层切变 (200-850 hPa)：

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

切变阈值：

| 切变强度 (m/s) | 对台风的影响 |
|---------------|-------------|
| < 5 | 极弱切变，台风容易增强，RI 有利条件之一 |
| 5-10 | 弱切变，台风可正常发展 |
| 10-15 | 中等切变，增强减缓，强台风难以维持 |
| 15-20 | 强切变，台风容易减弱，结构倾斜 |
| > 20 | 极强切变，台风结构严重破坏，难以增强 |

科学提示：
切变方向对降水分布至关重要——对流在切变下风方更活跃，因此暴雨落区偏向切变下风方。切变方向 + 台风移动方向 = 降水最大方位角。在业务中，"切变下风方 + 移动右侧（北半球）"叠加方向通常是最大降水风险区。

#### 4.3 大气湿度与水汽通量

相对湿度廓线：

```python
def humidity_profile(rh_field, storm_center, radius=500):
    """提取台风环境湿度廓线"""
    rh_env = area_mean_around_center(rh_field, storm_center, radius)
    return rh_env  # 各气压层的平均相对湿度

# 中层湿度 (700-500 hPa 平均) < 60% 不利于台风增强
# 高层湿度好 + 低层充分水汽输入 = 良好的湿热力学条件
```

水汽通量散度：

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

分析要点：
- 整层水汽辐合是台风降水的主要水汽来源
- 中层干燥空气侵入(dry air intrusion)可抑制对流，导致减弱
- 台风东侧的偏南风暖湿输送是登陆台风暴雨的关键水汽通道

#### 4.4 引导气流计算

深层平均引导气流：

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

引导气流与实际路径对比：

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

科学提示：
引导气流偏差（steering deviation）反映涡旋运动偏离引导气流的程度。偏差来源包括：β漂移（使台风向极运动）、摩擦效应（使路径偏移）、对流强迫（涡旋不对称产生的运动偏差）。在弱引导气流（<5 m/s）时，偏差可达 30-60°，路径预报最困难。

#### 4.5 位涡 (PV) 诊断

PV 计算：

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

高空 PV 异常与台风发展：

```python
def pv_anomaly(pv_field, climatology):
    """计算 PV 异常"""
    return pv_field - climatology

# 高空 PV 异常（高空冷低压/高空正 PV 异常）
# 可通过下传促进台风发展——高空辐散 + 涡度下传机制
```

科学提示：
高空 PV 异常对台风生成和快速增强有重要影响。PV 异常通过"位涡下传"机制——高空正 PV 异常诱导低层气旋性环流发展。典型情景是西风槽前的高空 PV 异常东移叠加到热带扰动上方，触发台风增强。

#### 4.6 潜在强度 (PI) 计算

Emanuel 公式：

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

使用说明：
- 完整的 PI 计算建议使用 Kerry Emanuel 的 pcmin.f90 程序或 Python 移植版（如 `tcpyPI` 库）
- 输入数据：ERA5 的温度和湿度廓线 + SST
- 输出：最大潜在风速 (PI_V) 和最小潜在中心气压 (PI_P)
- PI 与实际强度的比较可反映台风的发展空间——当实际强度接近 PI 时，台风接近理论极限

#### 4.7 热力学环境诊断

CAPE 和 CIN：

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

假相当位温 (θse)：

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

分析要点：
- CAPE > 1000 J/kg 有利于强对流发展
- 高 θse（>340 K）的湿舌从低层伸入台风区域是水汽和热力条件良好的标志
- 中层 θse 低值区（<320 K）指示干冷空气，可能抑制对流
- θse 廓线的对流不稳定（低层 θse > 高层 θse）是台风对流组织化的前提

环境场诊断注意事项：
1. **环境场的定义**：环境场应该去除台风本身的影响。常用方法是在台风周围 200-800 km 范围内做面积平均，或用大尺度分析场（更大范围平均）。直接取中心点附近的环境场会受台风环流污染。
2. **时间匹配**：环境场分析需要与台风强度在时间上对齐。ERA5 每小时数据可满足精细分析需求。
3. **多重线性回归**：强度预报因子通常用多元线性回归做组合（如 SHIPS 方法），但因子间的共线性（如 SST 和 PI 高度相关）需要注意。
4. **环境场的气候态**：评估某次台风的环境条件是否"异常"，需要与同期气候态做对比——某次 RI 事件的环境条件可能只是"略好于气候态"，关键是多重因子的协同作用。

### 5. 气候统计与趋势

- 频数气候态：年际/年代际变化、季节分布
- 强度气候态：各级强度频数分布
- 路径气候态：密度分布图、盛行路径
- 长期趋势检测：Mann-Kendall 趋势检验、线性回归
- 年际变率：ENSO/PDO/MODIKI 遥相关
- 生成潜势指数(GPI)：Emanuel-Nolan 公式
- 未来预估：CMIP6/HighResMIP 情景分析

#### 5.1 频数气候态

年频数统计：

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

季节分布：

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

西北太平洋气候态参考：
- 年均生成数：约 26 个（达到热带风暴及以上）
- 年均登陆中国数：约 7 个
- 生成高峰月：7-9 月（占总数约 70%）
- 双峰特征：6月小峰 + 8-9月主峰 + 10月次峰

#### 5.2 强度气候态

强度比例分布：

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

强度-频数分布：
台风强度服从特定的统计分布——可用幂律或指数分布拟合。近年来对"最强台风比例"的变化关注增多（高频强台风比例增加的信号）。

#### 5.3 路径气候态

路径密度分布：

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

盛行路径分类：
西北太平洋路径通常分为：
1. **西行型**：副高强盛，台风直行西移登陆华南/越南
2. **西北行型**：副高偏弱，路径偏北，登陆华东/朝鲜半岛
3. **转向型**：西风槽东移引导台风转向东北，不登陆或登陆后出海
4. **异常型**：打转、回旋、突然北翘等异常路径

#### 5.4 长期趋势检测

Mann-Kendall 趋势检验：
非参数趋势检验，适合非正态分布的气象数据。

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

线性回归趋势：

```python
from scipy.stats import linregress

def linear_trend(years, values):
    """线性回归趋势"""
    slope, intercept, r, p, se = linregress(years, values)
    return {'slope': slope, 'p_value': p, 'r_squared': r**2,
            'trend_per_decade': slope * 10}
```

趋势检测的注意事项：
- 台风频数/强度数据有显著的年际变率（ENSO 影响可达 ±30%），短期趋势可能被自然变率掩盖
- 至少需要 30 年数据才能可靠检测趋势
- 不同数据源的趋势可能不一致（CMA vs JMA vs JTWC 因定强方法差异）
- 要区分"频数趋势"和"强度趋势"——频数可能减少但平均强度可能增加

#### 5.5 年际变率与遥相关

ENSO 遥相关：

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

西北太平洋 ENSO 影响特征：

| ENSO 位相 | 生成位置 | 生成数 | 路径特征 | 强度 |
|-----------|---------|--------|---------|------|
| El Niño | 偏东南（远洋） | 略增 | 转向比例高 | 偏强 |
| La Niña | 偏西北（近海） | 略减 | 西行比例高 | 偏弱 |
| 中性 | 正常 | 正常 | 正常 | 正常 |

其他遥相关：
- PDO（太平洋年代际振荡）：调制 ENSO 的影响
- IOD（印度洋偶极子）：正 IOD 时西北太平洋台风偏强
- MJO（马登-朱利安振荡）：调制台风生成的活跃期和静默期

#### 5.6 生成潜势指数 (GPI)

Emanuel-Nolan GPI：

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

GPI 的用途：
- 诊断气候模式中台风活动的变化原因（哪个因子贡献最大）
- 未来气候情景下台风活动的预估
- 解释台风生成位置和季节的气候态分布

#### 5.7 未来气候预估

CMIP6 / HighResMIP 分析：

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

IPCC AR6 共识：
- 台风总频数可能减少或不变
- 强台风（Cat4-5）比例可能增加
- 台风降水率可能增加（+10-15%， Clausius-Clapeyron 关系 + 动力学变化）
- 台风可能移动减缓（外围环流减弱）

气候统计与趋势注意事项：
1. **数据一致性**：做气候统计必须使用同一版本、同一机构的数据。IBTrACS 版本更新会修改历史记录。
2. **热带低压的处理**：不同机构对热带低压的记录标准不同，做频数统计前要明确统计口径。
3. **季节调整**：台风活动有强季节性，做年际趋势分析前需要做季节调整或用年总量。
4. **显著性检验**：气候趋势一定要报告统计显著性。自然变率大时，即使有趋势也可能不显著。
5. **归因与相关**：发现台风活动与某气候指数相关不等于因果关系。需要动力机制解释和模式验证。

### 6. 数值模拟与预报检验

- WRF 模式配置：微物理、积云、PBL、海面通量方案选择
- WRF 输出分析：wrf-python 处理、诊断量计算
- 涡旋追踪(Bogus)与初始化
- 预报检验标准：逐时绝对误差、相对误差、技巧评分
- 多模式对比：GFS/ECMWF/UM/GRAPES
- 集合预报：概率预报、 dispersedness
- 错涡诊断：初始场误差增长

#### 6.1 WRF 模式配置

台风研究推荐配置：
台风数值模拟的物理方案选择对结果影响很大。以下是基于文献的综合推荐：

| 配置项 | 推荐方案 | 备选 | 理由 |
|--------|---------|------|------|
| 动力核 | ARW | — | 先进的非静力核心 |
| 微物理 | Thompson | WSM6, Morrison | 适合强对流，双参数方案 |
| 长波辐射 | RRTM | CAM | |
| 短波辐射 | Dudhia | CAM | |
| 积云对流 | Kain-Fritsch | 关闭(<4km) | 粗网格必需，细网格关闭 |
| PBL | YSU | MYJ, MYNN | YSU 非局地闭合，适合台风边界层 |
| 海面通量 | Charnock 或 COARE 3.0 | — | 感热/潜热通量是台风能量来源 |
| 陆面 | Noah | — | |
| 嵌套 | 2-3 重 | — | 最内层 1-2 km |

namelist.input 关键参数：

```fortran
&domains
 time_step = 60,            # 母域时间步长（秒）
 time_step_max = 60,
 max_dom = 3,               # 3重嵌套
 parent_id = 1, 1, 2,
 parent_grid_ratio = 1, 3, 3,
 i_parent_start = 31, 31, 31,
 j_parent_start = 17, 17, 17,
 e_we = 301, 301, 301,
 e_sn = 201, 201, 201,
 dx = 9000, 3000, 1000,      # 网格间距 (m)
 dy = 9000, 3000, 1000,
&phys
 mp_physics = 8,            # Thompson 微物理
 ra_lw_physics = 1,         # RRTM
 ra_sw_physics = 1,         # Dudhia
 cu_physics = 1, 1, 0,      # KF (粗), KF (中), 关闭 (细)
 bl_pbl_physics = 1,        # YSU
 sf_surface_physics = 1,    # Noah
 sf_sfclay_physics = 1,     # Monin-Obukhov
&domains
 spec_bdy_width = 5,
 specified = .true., .false., .false.,
```

科学提示：
网格分辨率对台风模拟至关重要。<5 km 时可以分辨眼壁结构；1-2 km 可以分辨双眼壁和螺旋雨带。但分辨率越高计算成本越大，需要权衡。积云对流方案在 <4 km 时应关闭（对流已被显式解析），但有些研究表明 4-8 km 网格仍需部分积云修正。

#### 6.2 WRF 输出分析

wrf-python 处理：

```python
from netCDF4 import Dataset
from wrf import getvar, interplevel, latlon_coords, to_np

ncfile = Dataset('wrfout_d01_2018-08-23_12:00:00')

# 提取基本变量
slp = getvar(ncfile, 'slp')
ua = getvar(ncfile, 'ua')  # U风
va = getvar(ncfile, 'va')  # V风
dbz = getvar(ncfile, 'dbz')  # 雷达反射率
pw = getvar(ncfile, 'pw')  # 整层可降水量

# 插值到等压面
u_850 = interplevel(getvar(ncfile, 'ua'), getvar(ncfile, 'p'), 850)
v_850 = interplevel(getvar(ncfile, 'va'), getvar(ncfile, 'p'), 850)

# 经纬度坐标
lats, lons = latlon_coords(slp)

# 计算涡度
from wrf import getvar
avo = getvar(ncfile, 'avo')  # 绝对涡度
```

台风中心定位：

```python
from wrf import getvar, latlon_coords
import numpy as np

def find_tc_center(slp, lats, lons, initial_guess):
    """用海平面气压极小值定位模式台风中心"""
    # 在初始猜测附近搜索最小值
    lat0, lon0 = initial_guess
    mask = (np.abs(lats - lat0) < 3) & (np.abs(lons - lon0) < 3)
    slp_masked = np.where(mask, slp, np.inf)
    ci, cj = np.unravel_index(np.argmin(slp_masked), slp.shape)
    return lats[ci, cj], lons[ci, cj]
```

诊断量计算：

```python
# 水汽通量散度
from wrf import getvar
q = getvar(ncfile, 'QVAPOR')  # 比湿
u = getvar(ncfile, 'ua')
v = getvar(ncfile, 'va')
# 水汽通量 = q * V
# 散度 = ∇·(q*V)

# 位涡
theta = getvar(ncfile, 'theta')
pv = calc_pv(theta, u, v, p)  # 需自定义

# 涡度分解
vorticity = getvar(ncfile, 'avo')  # 绝对涡度
```

#### 6.3 涡旋初始化与 Bogus

涡旋重定位和强度调整：
模式初始场中的涡旋通常位置和强度不准确，需要做 bogus 处理：

```python
# WRF 的涡旋初始化通过 namelist 控制
&domains
 vortex_interval = 120,       # 涡旋初始化间隔（分钟）
 max_vortex_intensity = 30,   # 最大强度（m/s）
 remove_existing_bogus_storms = .true.,
```

涡旋分离：

```python
def vortex_separation(field, storm_center, radius=500):
    """将台风涡旋与大尺度环境场分离
    field: 全场变量
    radius: 涡旋影响半径 (km)
    """
    # 方法1：Barnes滤波
    # 方法2：空间滤波（大尺度保留 + 涡旋 = 原始场）
    from scipy.ndimage import gaussian_filter
    env_field = gaussian_filter(field, sigma=20)  # 大尺度
    vortex = field - env_field  # 涡旋扰动
    return env_field, vortex
```

科学提示：
涡旋分离是台风数值模拟的重要预处理。错误初始涡旋会导致前 12-24h 的"spin-up"问题——模式需要时间让涡旋与动力框架协调。Bogus 方案可以加速 spin-up，但可能导致与实际不一致。

#### 6.4 预报检验标准

路径预报误差：

```python
def track_forecast_error(fcst_track, best_track, forecast_lead_times):
    """计算各预报时效的路径误差
    fcst_track: 预报路径 DataFrame
    best_track: 最佳路径 DataFrame
    forecast_lead_times: [24, 48, 72, 96, 120] 小时
    """
    errors = {}
    for lt in forecast_lead_times:
        fcst_at_lt = fcst_track[fcst_track['lead_time'] == lt]
        errors[lt] = []
        for _, row in fcst_at_lt.iterrows():
            best = best_track[best_track['time'] == row['valid_time']]
            if len(best) > 0:
                err = great_circle_distance(
                    row['lat'], row['lon'],
                    best['lat'].values[0], best['lon'].values[0]
                )
                errors[lt].append(err)
    return {lt: np.mean(v) for lt, v in errors.items() if v}
```

强度预报误差：

```python
def intensity_forecast_error(fcst_intensity, best_intensity, forecast_lead_times):
    """强度预报绝对误差"""
    errors = {}
    for lt in forecast_lead_times:
        fcst = fcst_intensity[fcst_intensity['lead_time'] == lt]
        diffs = []
        for _, row in fcst.iterrows():
            best = best_intensity[best_intensity['time'] == row['valid_time']]
            if len(best) > 0:
                diffs.append(abs(row['vmax'] - best['vmax'].values[0]))
        errors[lt] = np.mean(diffs) if diffs else np.nan
    return errors
```

技巧评分：

```python
def skill_score(forecast_error, baseline_error):
    """技巧评分 = (1 - 预报误差/基准误差) × 100%"""
    return (1 - forecast_error / baseline_error) * 100
```

标准基准模型：
- 路径：CLIPER（气候-持续性预报）
- 强度：SHIFOR（气候-持续性强度预报）
- SHIPS（统计-动力强度预报）是更高级的基准

常用检验指标汇总：

| 指标 | 路径 | 强度 | 集合 |
|------|------|------|------|
| 绝对误差 (AE) | 大圆距离 (km) | Vmax 差 (kt) | — |
| 偏差 (Bias) | 预报-实际位置差 | 预报-实际强度差 | — |
| 技巧评分 | 相对CLIPER | 相对SHIFOR | — |
| 集合散布 | — | — | 成员间路径DTW均值 |
| Brier评分 | — | RI概率预报 | 概率预报准确性 |
| 可靠性图 | — | — | 概率预报校准 |

#### 6.5 多模式对比

```python
import pandas as pd

def multi_model_comparison(models_forecast, best_track, lead_times):
    """多模式预报对比"""
    results = {}
    for model_name, fcst in models_forecast.items():
        track_err = track_forecast_error(fcst, best_track, lead_times)
        intensity_err = intensity_forecast_error(fcst, best_track, lead_times)
        results[model_name] = {'track': track_err, 'intensity': intensity_err}

    # 汇总表
    summary = pd.DataFrame({
        m: {f'{lt}h_track': r['track'][lt] for lt in lead_times if lt in r['track']}
        for m, r in results.items()
    })
    return summary
```

全球模式路径预报参考水平（近年）：
- ECMWF-IFS：72h 误差约 200 km（最佳）
- UKMO：72h 误差约 250 km
- GFS：72h 误差约 280 km
- 区域模式（如 BAM、HWRF）：近海路径可能更优

#### 6.6 集合预报分析

集合离散度：

```python
def ensemble_spread(members_tracks, lead_time):
    """计算集合离散度
    members_tracks: list of DataFrames, 各集合成员路径
    """
    spreads = []
    for lt in lead_time:
        positions = [(m[m['lead_time'] == lt]['lat'].values[0],
                       m[m['lead_time'] == lt]['lon'].values[0])
                      for m in members_tracks if lt in m['lead_time'].values]
        if len(positions) > 1:
            # 计算成员间平均两两距离
            dists = [great_circle_distance(p1[0], p1[1], p2[0], p2[1])
                      for i, p1 in enumerate(positions)
                      for p2 in positions[i+1:]]
            spreads.append(np.mean(dists))
    return spreads
```

Talagrand 直方图：

```python
def talagrand_histogram(forecasts, observation, n_bins):
    """Talagrand 直方图——检验集合预报的可靠性"""
    ranks = []
    for i in range(len(observation)):
        sorted_fcst = np.sort(forecasts[i])
        rank = np.searchsorted(sorted_fcst, observation[i])
        ranks.append(rank)
    hist, _ = np.histogram(ranks, bins=n_bins)
    return hist
```

科学提示：
理想的集合离散度应等于均方根误差(RMSE)。如果离散度 < RMSE，集合欠发散（under-dispersive），概率预报过于自信。全球模式路径预报的集合通常就是欠发散的。

#### 6.7 误差增长诊断

初值误差敏感试验：

```python
def error_growth_analysis(control_run, perturbed_runs, lead_times):
    """分析初始误差的增长
    control_run: 控制试验
    perturbed_runs: 扰动试验列表
    """
    growth = {}
    for lt in lead_times:
        diffs = [great_circle_distance(
            p[p['lead_time'] == lt].iloc[0]['lat'],
            p[p['lead_time'] == lt].iloc[0]['lon'],
            control_run[control_run['lead_time'] == lt].iloc[0]['lat'],
            control_run[control_run['lead_time'] == lt].iloc[0]['lon']
        ) for p in perturbed_runs]
        growth[lt] = np.mean(diffs)
    return growth
```

误差增长倍增时间：
台风预报误差的倍增时间约 1.5-2.5 天（可预报性上限约 2 周）。路径预报误差在 72h 后增长明显加快。

数值模拟与预报检验注意事项：
1. **WRF 版本兼容**：不同 WRF 版本的物理方案选项可能不同。WRF 4.x 系列推荐 Thompson 微物理的优化版本。
2. **Spin-up 时间**：模式启动后前 6-12 小时物理场需要协调（spin-up），这段时间的输出通常不用做分析。涡旋初始化可以缩短 spin-up。
3. **边界条件更新频率**：嵌套边界条件更新频率应至少每 6 小时一次，高频更新（如每 1 小时）可减少边界伪反射。
4. **预报检验的样本量**：个例检验意义有限，业务检验通常需要至少一个台风季节（30-50 个样本）才能有统计意义。
5. **模式分辨率与涡旋表示**：粗网格（>10 km）可能无法解析台风眼，涡旋会偏大偏弱。做结构研究至少需要 2-5 km 分辨率。

### 7. 灾害影响评估

- 风灾评估：风场重建 + 脆弱性曲线
- 暴雨灾害：降水阈值 + 历史重现期对比
- 风暴潮：SLOSH/ADCIRC 模型输出分析
- 经济损失：历史灾情数据库、归一化方法
- 伤亡分析：与强度的统计关系
- 综合风险评估：多因子叠加、风险等级划分

#### 7.1 风灾评估

风场重建：
台风灾害评估的第一步是获取风场——通常用最佳路径 + 风场模型重建。

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

脆弱性曲线：

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

风灾等级：
中国气象局的台风灾害等级划分（基于风速和灾害影响）：

| 等级 | 风速 (m/s) | 影响 |
|------|-----------|------|
| 轻微 | <17.2 | 树枝摇摆，轻损 |
| 中等 | 17.2-24.4 | 屋顶损坏，电力中断 |
| 严重 | 24.5-32.6 | 建筑物结构损毁 |
| 特大 | 32.7-41.5 | 大范围房屋倒塌 |
| 极端 | >41.5 | 毁灭性破坏 |

#### 7.2 暴雨灾害评估

降水阈值与风险：

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

重现期对比：

```python
def return_period_comparison(observed_precip, gev_params):
    """将观测降水与历史重现期对比"""
    from scipy.stats import genextreme
    shape, loc, scale = gev_params
    # 计算观测值的重现期
    return_period = 1 / (1 - genextreme.cdf(observed_precip, shape, loc=loc, scale=scale))
    return return_period
```

中国暴雨风险阈值参考：

| 风险等级 | 24h降水 (mm) | 1h降水 (mm) | 影响 |
|---------|-------------|------------|------|
| 蓝色预警 | 50 | — | 注意 |
| 黄色预警 | 100 | 30 | 需防范 |
| 橙色预警 | 200 | 50 | 严重 |
| 红色预警 | 250+ | 100+ | 极端 |

#### 7.3 风暴潮评估

SLOSH/ADCIRC 模型：
风暴潮是台风灾害的重要组成，常导致沿海严重灾情。

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

风暴潮经验估计：

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

#### 7.4 经济损失统计

归一化方法：
历史灾情数据需要做归一化——考虑通胀、人口增长和财富增长的影响。

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

损失-强度关系：

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

科学提示：
归一化后的台风经济损失在长期趋势上可能不显著（Pielke et al. 2008），这意味着社会经济发展（而非气候变化）是损失增长的主要原因。这一结论在学术界仍有争议——Weinkle et al. (2018) 指出不同的归一化方法可能给出不同结论。

#### 7.5 伤亡分析

伤亡与强度的统计关系：

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

伤亡与预警时效：
伤亡人数与预警提前时间、疏散执行情况强相关。发达地区的台风伤亡通常主要来自暴雨次生灾害（山洪、泥石流），而非风灾直接致死。

#### 7.6 综合风险评估

多因子风险叠加：

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

风险等级划分：

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

GIS 制图：
综合风险通常以空间地图形式呈现。

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

灾害影响评估注意事项：
1. **灾情数据的可靠性**：不同来源的灾情统计标准不同（EM-DAT vs 中国气象灾害年鉴），死亡人数和经济损失的统计可能相差数倍。
2. **近因效应**：历史灾情数据存在"近因效应"——近年灾害被更充分记录，可能导致虚假的上升趋势。归一化分析可部分修正这一问题。
3. **间接损失**：经济影响不仅包括直接损失（建筑/基础设施损毁），还有间接损失（停产、供应链中断、灾后重建成本）。通常间接损失可达直接损失的 50-100%。
4. **脆弱性变化**：社会脆弱性随发展水平变化——同样的台风在 20 年前和现在的经济损失和伤亡可能截然不同。风险评估必须考虑脆弱性的时间变化。
5. **复合灾害**：台风灾害往往是风+雨+潮的复合效应，单因子的风险评估可能低估总风险。

### 8. 快速增强(RI)分析

- RI 定义与判据：30 kt/24h（Kaplan-DeMaria）、35 kt/24h
- SHIPS 预报因子：环境场因子、持续性因子、内部结构因子
- RI 概率预报：SHIPS-RI、DTFA、深度学习方法
- RI 环境条件：暖 SST、弱切变、高湿度、高空辐散
- RI 内部过程：眼壁收缩、对流体耦合、暖心增强
- RI 个例对比分析：RI vs 非 RI 环境场差异
- 近年来 RI 预报能力评估

#### 8.1 RI 定义与判据

标准定义：
快速增强(Rapid Intensification, RI)是台风预报中最具挑战性的过程：

| 定义来源 | 判据 | 说明 |
|---------|------|------|
| Kaplan & DeMaria (2006) | 30 kt/24h | 最常用，SHIPS-RI 标准 |
| Kaplan et al. (2010) | 35 kt/24h | 更高阈值 |
| Xu & Wang (2015) | 20 m/s/24h | CMA 研究 |
|极端增强 | 40+ kt/24h | 极端事件 |

代码实现：

```python
def identify_ri(intensity_series, threshold=30, window=24):
    """识别 RI 事件
    intensity_series: 逐时/6小时间隔的最大风速序列 (kt)
    threshold: 增强阈值 (kt)
    window: 时间窗口 (小时)
    """
    ri_events = []
    dt = 6  # 假设6小时间隔
    steps = window // dt

    for i in range(len(intensity_series) - steps):
        change = intensity_series.iloc[i + steps] - intensity_series.iloc[i]
        if change >= threshold:
            ri_events.append({
                'start_time': intensity_series.index[i],
                'end_time': intensity_series.index[i + steps],
                'intensity_change': change,
                'start_intensity': intensity_series.iloc[i],
                'end_intensity': intensity_series.iloc[i + steps]
            })
    return ri_events
```

RI 发生频率：
- 全球热带气旋中 RI 发生率约 20-30%
- 西北太平洋 RI 发生率较高（约 25-35%）
- 大西洋约 15-25%
- RI 多发生在 60 kt 以下的发展阶段——已经很强的台风 RI 概率降低

#### 8.2 SHIPS 预报因子

SHIPS (Statistical Hurricane Intensity Prediction Scheme) 提供了系统化的强度预报因子体系：

主要因子分类：

| 类别 | 因子 | 含义 |
|------|------|------|
| 持续性 | Vmax (初始) | 当前强度 |
| 持续性 | DVmax_12h | 过去12h强度变化 |
| 持续性 | DVmax_24h | 过去24h强度变化 |
| 持续性 | 提前24h变化率 | 近期变化趋势 |
| 环境SST | SST | 台风中心海表温度 |
| 环境SST | Pot | 潜在强度-当前强度 |
| 环境SST | OHC | 海洋热含量 |
| 环境切变 | SHR200850 | 深层切变(200-850hPa) |
| 环境切变 | SHR500850 | 浅层切变 |
| 环境湿度 | RHMD | 中层湿度(700-500hPa) |
| 环境湿度 | D200 | 200hPa散度(高空辐散) |
| 环境涡度 | VORT850 | 850hPa相对涡度 |
| 距陆距离 | LAND | 距陆地距离 |
| 速度 | SPD | 台风移速 |

SHIPS 数据读取：

```python
def read_ships(ship_file):
    """读取 SHIPS 文本数据"""
    # SHIPS 文件格式：头部信息行 + 因子值行
    with open(ship_file) as f:
        lines = f.readlines()

    # 跳过头部行，解析因子行
    # 每行对应一个预报时刻
    data = []
    for line in lines[header_lines:]:
        parts = line.strip().split()
        data.append({
            'time': parts[0],
            'vmax': float(parts[1]),
            'sst': float(parts[2]),
            'shear': float(parts[3]),
            'rh_md': float(parts[4]),
            # ... 更多因子
        })
    return pd.DataFrame(data)
```

#### 8.3 RI 概率预报

SHIPS-RI：
SHIPS-RI 是基于逻辑回归的 RI 概率预报模型。

```python
from sklearn.linear_model import LogisticRegression

def ships_ri_model(factors, ri_labels):
    """构建 SHIPS-RI 逻辑回归模型
    factors: 预报因子 DataFrame
    ri_labels: RI 发生(1) / 不发生(0)
    """
    model = LogisticRegression(max_iter=1000)
    model.fit(factors, ri_labels)
    # 预报概率
    ri_prob = model.predict_proba(factors)[:, 1]
    return model, ri_prob
```

深度学习方法：
近年来深度学习在 RI 预报中展现了潜力。

```python
import tensorflow as tf
from tensorflow.keras import layers

def ri_deep_learning_model(input_shape):
    """基于卫星图像+环境因子的 RI 预报深度学习模型
    结构参考: Tan et al. (2024)
    """
    # 双流网络：卫星图像 + 环境因子
    img_input = layers.Input(shape=input_shape, name='satellite_image')
    x1 = layers.Conv2D(32, 3, activation='relu')(img_input)
    x1 = layers.MaxPooling2D(2)(x1)
    x1 = layers.Conv2D(64, 3, activation='relu')(x1)
    x1 = layers.GlobalAveragePooling2D()(x1)

    env_input = layers.Input(shape=(15,), name='env_factors')
    x2 = layers.Dense(32, activation='relu')(env_input)

    merged = layers.Concatenate()([x1, x2])
    x = layers.Dense(64, activation='relu')(merged)
    x = layers.Dropout(0.3)(x)
    output = layers.Dense(1, activation='sigmoid', name='ri_probability')(x)

    model = tf.keras.Model([img_input, env_input], output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model
```

#### 8.4 RI 环境条件诊断

RI 有利条件综合判据：

```python
def ri_favorable_conditions(sst, shear, rh_mid, d200, pot, land_dist, speed):
    """RI 有利条件判据
    返回各条件的满足情况
    """
    conditions = {
        'warm_sst': sst > 28.5,           # 暖海温
        'weak_shear': shear < 8,           # 弱切变
        'moist_mid': rh_mid > 60,          # 中层湿润
        'upper_div': d200 > 2,             # 高空辐散
        'high_pot': pot > 20,              # 潜在强度裕量大
        'far_land': land_dist > 200,       # 远离陆地
        'slow_move': speed < 5,            # 移速慢(充分吸收海洋能量)
    }
    conditions['all_met'] = all(conditions.values())
    conditions['n_met'] = sum(conditions.values())
    return conditions
```

环境因子阈值参考：

| 因子 | RI 有利 | RI 不利 | 来源 |
|------|---------|---------|------|
| SST | > 28.5°C | < 27°C | Kaplan & DeMaria (2006) |
| 深层切变 | < 8 m/s | > 15 m/s | Kaplan & DeMaria (2006) |
| 中层RH (700-500) | > 60% | < 50% | Kaplan & DeMaria (2006) |
| 高空散度 (200hPa) | > 2 × 10⁻⁶ s⁻¹ | < 0 | |
| OHC | > 50 kJ/cm² | < 20 kJ/cm² | Lin et al. (2013) |
| 初始强度 | 30-65 kt | > 100 kt | 已强的台风RI概率低 |
| 移速 | < 5 m/s | > 10 m/s | |

科学提示：
单因子阈值判断 RI 的效果有限——RI 往往需要多个条件同时满足。Kaplan & DeMaria 发现满足 5 个以上条件时 RI 概率约 40%，但仅满足 2-3 个条件时 RI 概率仍可达 10-15%（假阳性率高）。多因子的"非线性组合"效应是 RI 预报的核心难点。

#### 8.5 RI 内部过程分析

眼壁收缩：

```python
def eyewall_contraction(time_series_eyewall_radius, time_series_intensity):
    """分析眼壁半径随强度的变化
    RI 过程中通常伴随眼壁收缩
    """
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(time_series_eyewall_radius.index,
             time_series_eyewall_radius.values, 'b-', label='Eyewall Radius')
    ax1.set_ylabel('Eyewall Radius (km)', color='b')

    ax2 = ax1.twinx()
    ax2.plot(time_series_intensity.index,
             time_series_intensity.values, 'r-', label='Intensity')
    ax2.set_ylabel('Vmax (kt)', color='r')
```

内部过程关键指标：

| 指标 | RI 中典型变化 | 检测方法 |
|------|-------------|---------|
| 眼壁半径 | 缩小（50→30 km） | 卫星微波、雷达 |
| 眼直径 | 减小 | 红外/可见光卫星 |
| 对流深度 | 增加（CTT降低） | 红外亮温 |
| 雷暴频数 | 增加 | 红外/微波 |
| 暖心强度 | 增强 | AMSU/MHS |
| 轴对称化 | 提高 | 旋转对称度 |
| 涡旋罗斯贝波 | 向内传播 | 波数分析 |

#### 8.6 RI vs 非 RI 对比分析

合成(Composite)分析：

```python
def ri_composite_analysis(ri_cases, non_ri_cases, env_fields, field_names):
    """RI vs 非 RI 环境场合成分析
    ri_cases: RI 事件列表
    non_ri_cases: 非 RI 事件列表
    env_fields: 各事件对应的环境场字典
    """
    ri_composite = {f: np.mean([env_fields[c][f] for c in ri_cases], axis=0)
                     for f in field_names}
    nonri_composite = {f: np.mean([env_fields[c][f] for c in non_ri_cases], axis=0)
                        for f in field_names}

    # 差异场
    diffs = {f: ri_composite[f] - nonri_composite[f] for f in field_names}

    # 统计显著性
    from scipy.stats import ttest_ind
    significance = {}
    for f in field_names:
        ri_vals = [env_fields[c][f] for c in ri_cases]
        nonri_vals = [env_fields[c][f] for c in non_ri_cases]
        t_stat, p_val = ttest_ind(ri_vals, nonri_vals, axis=0)
        significance[f] = {'t_stat': t_stat, 'p_val': p_val}

    return ri_composite, nonri_composite, diffs, significance
```

对比分析要点：
在对比 RI 和非 RI 事件时，需注意：
1. **匹配初始强度**：RI 更多发生在中等强度（40-65 kt），直接对比不同初始强度的事件会引入偏差。建议按初始强度区间做匹配。
2. **匹配海域和季节**：不同海域的 RI 概率不同。
3. **样本量**：RI 是相对稀有事件（约 20%），合成分析需要足够的样本（通常 >50 例）。
4. **时间对齐**：合成分析需要以 RI 发生时刻为时间原点（t=0），前后各取若干时段。

#### 8.7 RI 预报能力评估

常用指标：

```python
def ri_forecast_verification(forecast_prob, observed_ri, threshold=0.4):
    """RI 概率预报检验"""
    from sklearn.metrics import (confusion_matrix, brier_score_loss,
                                  roc_auc_score)

    # 二值化预报
    forecast_binary = (forecast_prob >= threshold).astype(int)

    # 混淆矩阵
    cm = confusion_matrix(observed_ri, forecast_binary)
    tn, fp, fn, tp = cm.ravel()

    # 指标
    pod = tp / (tp + fn) if (tp + fn) > 0 else 0  # 命中率
    far = fp / (fp + tp) if (fp + tp) > 0 else 0  # 虚警率
    brier = brier_score_loss(observed_ri, forecast_prob)        # Brier评分
    auc = roc_auc_score(observed_ri, forecast_prob)             # AUC

    return {
        'POD': pod, 'FAR': far,
        'Brier': brier, 'AUC': auc,
        'confusion_matrix': cm
    }
```

当前预报水平参考：

| 方法 | POD | FAR | 说明 |
|------|-----|-----|------|
| SHIPS-RI | ~30-40% | ~30-40% | 命中率低，虚警率高 |
| 深度学习 | ~50-60% | ~25-35% | 近年改善明显 |
| 人类预报员 | ~40-50% | ~30-40% | 综合多源信息 |

科学提示：
RI 预报是台风强度预报的核心难点。目前业务预报的 POD 普遍低于 50%，意味着超过一半的 RI 事件无法提前预报。这主要是因为 RI 的物理机制——内部对流的组织化过程——在当前观测分辨率下难以充分捕捉。

快速增强(RI)分析注意事项：
1. **RI 的定义敏感性**：30 kt/24h vs 35 kt/24h 的判定结果可能有 20% 的差异。研究中需注明使用的具体定义。
2. **时间分辨率影响**：6 小时间隔的最佳路径数据可能平滑掉短时峰值增强。理想情况下应使用逐时或 3 小时间隔数据。
3. **RI 的季节性**：西北太平洋 RI 多发生在 7-10 月（SST 高、切变弱），冬季几乎不发生。
4. **RI 和眼壁置换的关系**：眼壁置换过程中的暂时减弱可能被误判为 RI 的"反面"，而置换完成后的再次增强可能触发 RI。两者需区分。
5. **模式模拟 RI 的限制**：粗网格（>5 km）模式难以模拟 RI——对流组织化、眼壁形成等过程需要高分辨率。做 RI 机理研究建议用 ≤2 km 的对流分辨模拟

## 文献搜索工作流

### 1. 关键词策略

#### 概念组构建

将研究主题拆解为多个概念组，每组列出同义词和相关词，确保搜索覆盖全面：

```
概念组A（现象）：
  typhoon, tropical cyclone, hurricane, 台风, 热带气旋, TC, TCs

概念组B（研究维度）：
  track / trajectory / path / 路径 / 轨迹
  intensity / rapid intensification / RI / 强度 / 快速增强
  rainfall / precipitation / 降水 / 降雨 / 暴雨
  structure / eyewall / rainband / 结构 / 眼壁 / 雨带
  environment / SST / shear / 环境 / 切变

概念组C（方法）：
  WRF / numerical simulation / 数值模拟
  climatology / trend / 气候 / 趋势
  satellite / GPM / IMERG / TRMM / 卫星
  reanalysis / ERA5 / 再分析

概念组D（海域）：
  Western North Pacific / WNP / 西北太平洋 / 南海
  North Atlantic / NA / 大西洋
  South China Sea / SCS
  global / 全球
```

#### 搜索式构建

使用布尔逻辑组合概念组：

```
(A: typhoon OR tropical cyclone OR hurricane)
AND (B: track OR trajectory)
AND (C: climatology OR trend)
AND (D: "Western North Pacific")
```

#### 关键词扩展策略

- **同义词扩展**：确保英中文术语都覆盖
- **截词符**：`cyclon*` 匹配 cyclone, cyclones, cyclonic
- **引号精确匹配**：`"rapid intensification"` 精确匹配短语
- **排除词**：`NOT (Atlantic OR hurricane)` 排除其他海域

### 2. 搜索执行

#### 英文文献数据库

Google Scholar：
- URL: https://scholar.google.com
- 特点：覆盖面广，含被引次数，可追溯参考文献
- 搜索策略：用概念组构建搜索式，按被引次数排序，先取高被引论文
- 工具：可通过 webfetch 访问搜索结果页面

Semantic Scholar：
- URL: https://www.semanticscholar.org
- 特点：AI 驱动的文献推荐，含 TL;DR 摘要
- API: 可通过 API 获取结构化文献信息

```
GET https://api.semanticscholar.org/graph/v1/paper/search?query=typhoon+rapid+intensification&limit=20&fields=title,year,abstract,citationCount
```

NASA ADS：
- URL: https://ui.adsabs.harvard.edu
- 特点：天文学/地球物理学领域权威数据库，含气象类期刊
- 适合：检索 JAS, MWR, GRL, JGR-Atmospheres 等期刊文章

Web of Science / Scopus：
- 特点：引文分析工具，可做引文追溯和前向引用搜索
- 适合：系统性综述，识别高影响力论文和研究脉络

#### 中文文献数据库

中国知网 (CNKI)：
- URL: https://www.cnki.net
- 特点：中文期刊全文数据库，含气象学报、热带气象学报等核心期刊
- 搜索策略：用中文关键词搜索，按被引/下载次数排序

万方数据：
- URL: https://www.wanfangdata.com.cn
- 特色：学位论文收录较全，可检索博硕论文

#### 预印本

arXiv (physics.ao-ph)：
- 大气物理预印本，适合获取最新研究

#### 搜索流程

```
1. 第一轮搜索：核心关键词组合，获取 50-100 篇候选论文
2. 筛选：阅读标题和摘要，保留 20-30 篇高相关论文
3. 引文追溯：检查筛后论文的参考文献，补充经典文献
4. 前向引用：在 Google Scholar 中查看经典论文的"被引用"列表，找最新进展
5. 精读：对核心论文做全文精读，提取方法、数据、结论
```

### 3. 文献摘要生成

#### 单篇文献摘要模板

对每篇检索到的文献，提取以下信息：

```markdown
### [作者, 年份] 标题
- **期刊**: 期刊名, 卷(期), 页码
- **DOI**: 10.xxxx/xxxxx
- **被引次数**: N次 (截至 YYYY-MM)
- **数据**: 使用了什么数据（IBTrACS, ERA5, GPM, WRF模拟等）
- **方法**: 核心方法（统计方法、模式模拟、遥感分析等）
- **关键发现**: 2-3句话概括核心结论
- **局限**: 主要局限性
- **与本研究的关联**: 与当前研究主题的关系
```

#### 摘要生成示例

```
### [Emanuel, 2005] Increasing destructiveness of tropical cyclones over the past 30 years
- **期刊**: Nature, 436, 686-688
- **被引次数**: 3500+次
- **数据**: HURDAT (大西洋+东太平洋), 1974-2004
- **方法**: PDI (Power Dissipation Index) 趋势分析
- **关键发现**: 台风破坏力(PDI)在过去30年显著增加，
  与 SST 升高强相关。作者认为气候变化可能是原因之一。
- **局限**: 仅分析了两个海域；相关不等于因果；
  后续研究指出数据质量和统计方法存在争议
- **关联**: 气候变化背景下台风强度趋势的经典论文，
  综述中必须引用
```

### 4. 综述撰写

#### 综述结构

```markdown
# [研究主题] 文献综述

## 1. 引言
- 研究背景与科学问题
- 综述范围与检索方法（数据库、关键词、时间范围）
- 综述结构说明

## 2. 数据与方法
- 常用数据源及其特点与局限
- 主要分析方法和技术路线
- 数据质量控制与不确定性来源

## 3. 主要研究进展
### 3.1 [子主题1：如路径变化]
- 历史趋势
- 年际变率
- 物理机制
- 存在争议

### 3.2 [子主题2：如强度变化]
- ...

### 3.3 [子主题3：如降水变化]
- ...

## 4. 研究空白与争议
- 数据一致性问题
- 方法论分歧
- 尚未解决的科学问题
- 观测能力不足之处

## 5. 未来方向
- 新数据/新方法
- 气候变化背景
- 技术发展趋势

## 6. 结论
- 主要共识
- 关键不确定性
- 对当前研究的启示

## 参考文献
[按引用顺序排列]
```

#### 综述撰写原则

1. **客观性**：公正呈现不同观点，不偏向某一结论
2. **批判性**：不仅罗列发现，还评价方法质量和结论可靠性
3. **系统性**：按主题（而非按论文）组织，避免"流水账"
4. **溯源性**：从经典文献到最新进展，呈现研究脉络
5. **可追溯性**：注明信息来源（哪篇论文说的），所有关键论断都有引用

#### 综述中的表格和图

汇总表：将多篇论文的方法和结论整理成对比表：

| 文献 | 海域 | 时段 | 数据 | 方法 | 主要结论 |
|------|------|------|------|------|---------|
| [1] | WNP | 1975-2015 | IBTrACS | MK趋势检验 | 频数无显著趋势 |
| [2] | 全球 | 1980-2020 | IBTrACS | 线性回归 | 强台风比例增加 |
| ... | ... | ... | ... | ... | ... |

研究脉络图：展示研究发展的时间线：

```
1975 ── Dvorak 技术提出
  │
1980 ── Holland 风场模型
  │
1995 ── 最佳路径数据电子化
  │
2000 ── TRMM 卫星降水数据
  │
2005 ── Emanuel PDI 趋势论文 → 争议开始
  │
2010 ── SHIPS-RI 概率预报
  │
2014 ── GPM 卫星发射
  │
2018 ── 深度学习应用于台风研究
  │
2020 ── ERA5 再分析延长至 1940
  │
2024 ── AI 预报模型 (GraphCast, Pangu)
```

### 5. 引用格式

#### 气象学常用引用格式

美国气象学会 (AMS) 使用 AMS 格式（类似 author-year）：

```
正文引用：(Emanuel 2005; Knutson et al. 2010)
两条以上：(Emanuel 2005; Webster et al. 2005; Elsner et al. 2008)

参考文献列表：
Emanuel, K., 2005: Increasing destructiveness of tropical cyclones over the past 30 years.
  Nature, 436, 686–688, https://doi.org/10.1038/nature03906.

Knutson, T. R., J. L. McBride, J. Chan, et al., 2010: Tropical cyclones and climate change.
  Nat. Geosci., 3, 157–163, https://doi.org/10.1038/ngeo779.
```

#### 中文期刊引用

```
正文：(陈联寿等 2012)
参考文献：陈联寿, 丁一汇, 1979: 西太平洋台风概论. 科学出版社, 491pp.
```

#### DOI 的重要性

- 所有引用的论文应尽量标注 DOI
- DOI 是论文的唯一永久标识，方便读者追溯

### 6. 研究空白识别

#### 常见研究空白来源

1. **数据局限**：某些海域/时段的数据质量或覆盖不足
2. **方法局限**：现有方法无法解决的问题
3. **尺度不匹配**：模式分辨率与观测能力的差距
4. **物理机制不明**：观测到的现象缺乏理论解释
5. **争议未解**：学术界的分歧尚未解决

#### 识别方法

```
# 在文献综述中，通过以下方式识别研究空白：
# 1. 统计论文中出现的"需要进一步研究""尚不清楚"等表述
# 2. 对比不同论文的结论——不一致之处可能指向未解决问题
# 3. 检查最新方法的局限——深度学习/AI方法在哪些方面仍有不足
# 4. 关注 IPCC 报告中的"低信度"结论——这些是科学界共识的空白区
```

#### 台风研究中的已知空白

- **RI 的物理机制**：为什么在看似相同的环境条件下，有些台风 RI 有些不 RI
- **台风-海洋耦合**：冷尾迹对后续台风的定量影响
- **台风降水的归因**：气候变化对单次台风极端降水的贡献
- **台风结构的高分辨率观测**：内核区观测数据仍然稀少
- **AI 预报的可解释性**：AI 模型为何在某些情况下优于传统模式

### 7. 文献搜索注意事项

1. **文献时效性**：优先引用近 5 年的论文，经典论文可追溯。对于快速发展的领域（如 AI 预报），近 2 年的论文最相关。
2. **期刊质量**：关注高影响因子期刊（Nature, Science, JAS, MWR, GRL, JGR-Atmospheres）的论文，但也不要忽视专业期刊（Tropical Cyclone Research and Review, 热带气象学报）。
3. **预印本的处理**：arXiv 等预印本未经同行评审，引用时需注明"preprint"。高影响预印本可引用但需谨慎。
4. **语言覆盖**：中文文献在中国台风研究中很重要（特别是 CMA/JMA 数据相关的早期研究），不要只搜英文文献。
5. **引用溯源**：对关键论断，追溯到原始论文而非二手引用。例如"IPCC AR6 说..."应找到 AR6 中的具体原文和其引用的原始研究。

## 数据源速查

| 数据 | 来源 | 格式 | 时间范围 | 详见 |
|------|------|------|---------|------|
| IBTrACS v04 | NOAA NCEI | NetCDF/CSV | 1842-至今 | 下方"数据源速查详情" |
| CMA Best Track | CMA-TJ | TXT/CSV | 1949-至今 | 下方"数据源速查详情" |
| JMA Best Track | JMA RSMC Tokyo | TXT | 1951-至今 | 下方"数据源速查详情" |
| JTWC | JTWC Guam | TXT | 1945-至今 | 下方"数据源速查详情" |
| HURDAT2 | NHC | TXT | 1851-至今 | 下方"数据源速查详情" |
| ERA5 | ECMWF CDS | NetCDF/GRIB | 1940-至今 | 下方"数据源速查详情" |
| GPM IMERG | NASA GES DISC | NetCDF/HDF5 | 2000-至今 | 下方"数据源速查详情" |
| SHIPS | NOAA AOML | TXT | 1989-至今 | 下方"数据源速查详情" |

### 数据源速查详情

#### 1. 最佳路径数据

IBTrACS v04（NOAA NCEI）— 推荐，全球整合：
- **官网**：https://www.ncei.noaa.gov/products/international-best-track-archive
- **格式**：NetCDF (.nc)、CSV、Shapefile
- **时间范围**：1842 年至今，每 3/6 小时
- **关键变量**：时间、经纬度、最大持续风速(VMAX)、中心气压(MIN_PRES)、命名、机构
- **多机构对照**：包含 CMA、JTWC、JMA、NHC、IMD 等机构数据，可交叉验证
- **下载**：
  ```python
  # 全量 NetCDF
  url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/code/IBTrACS.ALL.v04r00.nc"
  # 活跃气旋
  url_active = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/current/IBTrACS.active.v04r00.nc"
  ```
- **Python 读取**：`xarray.open_dataset()` 直接读取 NetCDF
- **注意**：不同机构对同一气旋的风速定义不同（1-min vs 10-min vs 3-min），需做风速换算：
  - 10-min 平均 → 1-min 平均：乘以约 1.14（Knapp & Kruk 2010）
  - 3-min 平均 → 1-min 平均：乘以约 1.06
  - 2-min 平均（CMA）→ 1-min 平均：乘以约 1.10

CMA-STI Best Track（上海台风研究所）：
- **获取**：中国气象局上海台风研究所，http://www.typhoon.org.cn
- **格式**：TXT（类似 ATCF格式）
- **时间范围**：1949 年至今，每 6 小时
- **变量**：编号、国际名称、中心经纬度、中心最低气压、近中心最大风速（2-min平均）
- **特色**：包含中国大陆登陆点信息、灾害简况

JMA Best Track（日本气象厅）：
- **获取**：RSMC Tokyo，https://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks.html
- **格式**：TXT
- **时间范围**：1951 年至今，每 6 小时（部分每 3 小时）
- **变量**：中心经纬度、中心气压、最大持续风速（10-min平均）、最大瞬间风速
- **特色**：西北太平洋权威 RSMC 数据

JTWC Best Track（美国联合台风警报中心）：
- **获取**：https://www.metoc.navy.mil/jtwc/jtwc.html
- **格式**：TXT（ATCF格式 .dat）
- **时间范围**：1945 年至今，每 6 小时
- **变量**：编号、名称、经纬度、最大持续风速（1-min平均）、中心气压、风圈半径
- **特色**：包含风圈半径数据（34/50/64 kt），适合风场结构研究

HURDAT2（NHC，北大西洋/东北太平洋）：
- **获取**：https://www.nhc.noaa.gov/data/#hurdat
- **格式**：TXT
- **时间范围**：1851 年至今
- **变量**：名称、时间、经纬度、最大风速（1-min）、中心气压、强度等级

#### 2. 再分析数据

ERA5（ECMWF）— 最推荐：
- **获取**：Copernicus Climate Data Store (CDS)，https://cds.climate.copernicus.eu
- **格式**：NetCDF/GRIB
- **时间范围**：1940 年至今
- **空间分辨率**：0.25°（约 31 km），137 垂直层
- **时间分辨率**：1 小时
- **常用变量**：
  - 单层：10m 风速、MSLP、SST、2m 温度/湿度、总降水量、CAPE、TCWV
  - 多层：位势高度、温度、比湿、U/V 风分量（1000-1 hPa）
  - 派生：垂直风切变(200-850hPa)、引导气流(多层平均)
- **下载方式**：
  ```python
  import cdsapi
  c = cdsapi.Client()
  c.retrieve('reanalysis-era5-pressure-levels', {
      'product_type': 'reanalysis',
      'format': 'netcdf',
      'variable': ['u_component_of_wind', 'v_component_of_wind', 'geopotential'],
      'pressure_level': ['200', '850'],
      'year': '2018', 'month': '09', 'day': ['15', '16'],
      'time': ['00:00', '06:00', '12:00', '18:00'],
  }, 'era5_200_850.nc')
  ```
- **API key**：需注册 CDS 账户，配置 `~/.cdsapirc`

JRA-55（日本气象厅）：
- 时间范围：1958 至今，0.5° 分辨率
- 适用：需要更长一致记录的气候研究

MERRA-2（NASA）：
- 时间范围：1980 至今，0.5° × 0.625°
- 特色：含详细的大气水汽和能量收支变量

#### 3. 卫星降水数据

GPM IMERG（推荐）：
- **获取**：NASA GES DISC，https://disc.gsfc.nasa.gov/datasets/GPM_3IMERG_07/summary
- **格式**：NetCDF4/HDF5
- **时间范围**：2000 年至今（GPM 卫星 2014 至今，含 TRMM 融合延伸期）
- **空间分辨率**：0.1°（约 10 km）
- **时间分辨率**：30 分钟
- **产品级别**：
  - IMERG Early：4 小时延迟，适合近实时
  - IMERG Late：14 小时延迟，利用后续卫星修正
  - IMERG Final：3.5 月延迟，融合地面台站校正，**科研首选**
- **变量**：precipitationCal（校正降水率，mm/hr）、precipitationUncal、概率降水
- **下载**：
  ```python
  # 通过 OpenDAP 或 GES DISC 下载
  url = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07"
  # 或使用 Python 的 podpac/ecmwf-data-client 库
  ```

TRMM 3B42/3B43（历史数据）：
- 时间范围：1998-2019（已停止更新）
- 分辨率：0.25°，3 小时
- 特色：长期降水气候研究，可与 GPM 衔接做时间一致性分析

CMORPH（NOAA）：
- 时间范围：1998 至今
- 分辨率：0.25°/8km，30 分钟
- 特色：纯卫星反演，无地面校正

#### 4. 卫星风场数据

ASCAT（MetOp 系列）：
- 散射计海面风场，25/12.5 km 分辨率
- 覆盖：每日 2 次，全球
- 适用：台风外围风场验证、海面风场非对称性

SMAP/SMOS 海面风场：
- L 波段辐射计，可在强降水条件下获取海面风场
- 适用：台风内核区风场估计

RapidScan（静止卫星）：
- 风向风速推导（AMV），高频次
- 适用：台风环流演变、引导气流诊断

#### 5. 数值模式数据

WRF（Weather Research and Forecasting）：
- **用途**：台风数值模拟（个例研究、敏感性试验）
- **输出格式**：NetCDF (wrfout)
- **处理工具**：wrf-python、NCL
- **关键配置建议**（台风研究）：
  - 微物理：Thompson 或 WSM6
  - 积云对流：Kain-Fritsch（粗网格）或关闭（<4km）
  - PBL：YSU 或 MYJ
  - 海面通量：Charnock 关系或 COARE
  - 动力核：高级（ARW）
  - 嵌套：2-3 重嵌套，最内层 1-2 km

GFS（NCEP）— 实时预报：
- 分辨率：0.25°，每 6 小时到 384h
- 获取：https://nomads.ncep.noaa.gov/
- 用途：预报对比、环境场分析

ECMWF IFS — 实时预报：
- 分辨率：0.25°/0.1°（HRES），每 6h 到 240h
- 用途：预报对比（ECMWF 通常路径预报技巧最高）

CMIP6 / HighResMIP — 气候预估：
- 用途：台风活动未来情景分析
- 关键模式：HiRAM、FLOR、HadGEM3-GC31
- 变量：海温、风场、湿度（需用台风检测算法从模式输出中识别气旋）

#### 6. 预报与统计预报数据

SHIPS（SHIPS-RI）：
- **获取**：NOAA AOML，https://www.aoml.noaa.gov/hrs/
- **内容**：各预报因子值（环境切变、SST、Pot、Persistence 等）
- **用途**：RI 预报、强度预报因子分析

各机构官方预报：
- CMA、JMA、JTWC、NHC 每年发布预报数据
- 格式：类似 ATCF，含路径和强度预报
- 用途：预报检验、技巧评分计算

#### 7. 灾情数据

EM-DAT（国际灾害数据库）：
- **获取**：https://www.emdat.be
- **内容**：全球自然灾害记录，含伤亡人数、经济损失
- **时间范围**：1900 至今

中国气象灾害年鉴：
- **获取**：中国气象局
- **内容**：中国台风灾害详细记录

IBTrACS 附带灾情：
- 部分记录含登陆点信息和简单灾情描述

#### 8. 地形与陆面数据

ETOPO1：
- 全球地形/水深，1 分分辨率
- 用途：地形降水分析、风暴潮模拟

GTOPO30 / SRTM：
- 陆地高程数据
- 用途：地形对降水和风场的影响分析

#### 数据使用注意事项

1. **风速定义差异**：不同机构使用不同平均时段，做跨机构对比前必须统一。CMA 用 2-min，JMA 用 10-min，JTWC/NHC 用 1-min。换算关系见 IBTrACS 部分。
2. **时间对齐**：IBTrACS 每 6 小时，ERA5 每 1 小时，GPM 每 30 分钟。做多源融合时需做时间插值或选择共同时次。
3. **空间投影**：台风数据用经纬度，再分析用规则格点。画图时注意选择合适地图投影（西北太平洋用兰伯特或墨卡托，全球用等距圆柱/正交投影）。
4. **版本一致性**：ERA5 有 back-extension（1950-1978）和 main（1979-至今），拼接时需检查一致性。IBTrACS 版本更新会修改历史记录，论文中需注明使用版本。
5. **缺失值处理**：早期台风记录（特别是 1950 年代前）可靠性较低，气候统计通常截取 1970 或 1980 年后。

## 代码生成原则

本 skill 不再提供独立的脚本文件，而是通过代码生成原则指导用户按需生成代码。

1. **语言选择**：用户指定语言时按指定语言生成；未指定时默认 Python。所有五种语言（Python/NCL/GrADS/MATLAB/R）的参考实现均可按本 skill 中的框架生成。
2. **可读性优先**：代码配 markdown 说明——关键步骤解释为什么这样做、参数含义、可能的替代方案。
3. **可复现性**：固定随机种子、标注数据版本和下载日期、注明依赖包版本。
4. **科研规范**：统计检验标注 p 值、图表标注单位和坐标轴、地图投影注明、色标选择考虑色觉友好。
5. **渐进引导**：对于复杂分析，先给骨架代码让用户跑通，再逐步增加诊断量和可选参数。

## 输出格式指南

根据任务性质灵活选择：

| 场景 | 推荐输出 | 说明 |
|------|---------|------|
| 数据处理/画图 | 可运行代码 + 图表文件 | 代码附 markdown 逐段说明 |
| 个例分析 | 分析报告（结构化文本+图表） | 参见下方"报告模板" |
| 气候统计 | 统计表格 + 图表 + 方法说明 | 含统计检验结果 |
| 文献综述 | 结构化综述文本 | 含引用列表 |
| 多维度综合研究 | 完整研究报告 | 各维度分节，最后综合讨论 |

## 报告模板

本 skill 为台风科研研究提供标准报告结构，可根据具体研究内容裁剪。删除不适用的章节，保留核心结构。

# [台风名称/编号] [研究维度] 研究报告

**研究者**: [姓名]  
**机构**: [单位]  
**日期**: YYYY-MM-DD  
**数据版本**: [IBTrACS v04r00 / ERA5 / GPM IMERG v07 等]

---

## 摘要

[200-300字概述研究目的、方法、主要发现和结论。]

**关键词**: 台风；[路径/强度/降水/环境场/RI等]；[方法关键词]

---

## 1. 引言

### 1.1 研究背景

[台风研究的科学意义，本次研究问题在大领域中的定位。]

### 1.2 科学问题

[本次研究要回答的具体科学问题。]

### 1.3 研究目标

[列出3-5个具体研究目标。]

---

## 2. 数据与方法

### 2.1 个例概述

| 项目 | 内容 |
|------|------|
| 台风名称 | [名称] |
| 编号 | [编号] |
| 生命史 | [起止日期] |
| 峰值强度 | [Vmax / Pmin] |
| 登陆地点 | [地点] |
| 登陆强度 | [Vmax / Pmin] |

### 2.2 数据来源

[描述使用的所有数据源，含版本、时间范围、空间分辨率等。]

| 数据 | 来源 | 变量 | 时间范围 | 分辨率 |
|------|------|------|---------|--------|
| 最佳路径 | [IBTrACS/CMA/JMA] | lat, lon, vmax, pres | [起止] | [6h] |
| 再分析 | [ERA5] | [u, v, t, q 等] | [起止] | [0.25°/1h] |
| 卫星降水 | [GPM IMERG] | precipitationCal | [起止] | [0.1°/30min] |
| ... | ... | ... | ... | ... |

### 2.3 分析方法

[概述使用的主要方法，引用方法学文献。详细的公式和推导可放附录。]

### 2.4 风速统一化

[说明不同数据源的风速定义差异及统一方法。]

---

## 3. 结果与分析

### 3.1 路径特征

[路径概述：生成位置、移动方向、转向特征、登陆路径等。]

[图：路径图，按强度/时间着色]

[路径异常点分析（如有）：突然北翘、打转、回旋等。]

[移速移向分析。]

### 3.2 强度演变

[强度时间序列描述：生成、增强、峰值、减弱各阶段。]

[图：Vmax/Pmin 双轴时间序列]

[快速增强(RI)事件分析（如有）。]

[强度变化率分析。]

### 3.3 风场结构

[最大风速半径(RMW)变化。]

[风圈半径(34/50/64kt)演变。]

[非对称风场分析。]

### 3.4 降水特征

[降水空间分布描述。]

[图：降水空间分布图]

[降水时间演变：Hovmöller 图分析。]

[降水非对称性分析。]

[地形增强效应（如登陆/近岸）。]

### 3.5 环境场条件

[海表温度(SST)。]

[垂直风切变。]

[中层湿度。]

[引导气流。]

[高空辐散。]

[RI 有利条件判据评估（如适用）。]

### 3.6 [其他研究维度]

[根据实际研究内容添加：气候统计/数值模拟/灾害评估/RI分析等。]

---

## 4. 讨论

### 4.1 与历史个例对比

[将本次个例与类似路径/强度的历史台风对比。]

### 4.2 与文献对比

[将分析结果与已有文献中的结论对比——一致或不一致之处。]

### 4.3 物理机制讨论

[分析现象背后的物理机制——为什么路径北翘？为什么突然增强？为什么降水非对称？]

### 4.4 不确定性分析

[讨论数据和方法的局限性。]

---

## 5. 结论

[总结主要发现，每个发现对应一个研究目标。]

1. [发现1]
2. [发现2]
3. [发现3]
...

---

## 参考文献

[按引用顺序排列。使用 AMS 格式或目标期刊格式。]

```
Emanuel, K., 2005: Increasing destructiveness of tropical cyclones over the past 30 years.
  Nature, 436, 686–688, https://doi.org/10.1038/nature03906.

Holland, G. J., 1980: An analytical model of the wind and pressure profiles in hurricanes.
  Mon. Wea. Rev., 108, 1212–1218, https://doi.org/10.1175/1520-0493(1980)108<1212:AAMOTW>2.0.CO;2.
```

---

## 附录

### 附录A: [补充图表]

### 附录B: [方法学详细推导]

### 附录C: [数据和处理日志]

---

## 图表清单

| 图号 | 标题 | 说明 |
|------|------|------|
| 图1 | 台风路径图 | 按强度着色 |
| 图2 | 强度时间序列 | Vmax + Pmin 双轴 |
| 图3 | 降水空间分布 | 24h累积降水 |
| 图4 | 环境场诊断 | 4面板综合图 |
| ... | ... | ... |

## 表格清单

| 表号 | 标题 |
|------|------|
| 表1 | 个例概述 |
| 表2 | 数据来源 |
| 表3 | 检验结果 |
| ... | ... |

## 使用建议

- 用户的表述可能模糊（如"帮我分析下这个台风"），主动追问：哪个台风/哪个海域/想做什么维度/有没有数据
- 研究维度之间常有交叉——路径+强度+降水是常见组合，环境场诊断可能同时服务于 RI 分析和个例研究
- 若用户是研究生或刚入门，在分析时多解释科学背景和为什么选择某方法；若用户是资深研究者，可更直接地给方法和代码
- 鼓励用户先确定数据是否就绪再开始分析——数据问题是科研中最常见的卡点

## 实现说明

本 skill 为纯文本实现，所有方法学内容直接内联在本文档中。

### 已实现的功能

- ✅ 确定研究海域（6大海域 + 数据源对应）
- ✅ 确定研究维度（8大研究维度）
- ✅ 数据获取指导（IBTrACS, ERA5, GPM, SHIPS 等）
- ✅ 路径研究方法（数据读取、可视化、相似性、聚类、误差评估）
- ✅ 强度与风场研究方法（时间序列、分级、RMW、非对称、Dvorak）
- ✅ 降水分析方法（GPM处理、空间分布、Hovmöller、非对称、极端统计）
- ✅ 环境场诊断方法（SST、切变、湿度、引导气流、PV、PI、CAPE）
- ✅ 气候统计与趋势（频数、强度、路径气候态、Mann-Kendall、ENSO、GPI、CMIP6）
- ✅ 数值模拟与预报检验（WRF配置、wrf-python、Bogus、误差评估、多模式对比、集合预报）
- ✅ 灾害影响评估（风灾、暴雨、风暴潮、经济损失、伤亡、综合风险）
- ✅ 快速增强(RI)分析（RI定义、SHIPS因子、概率预报、环境条件、内部过程、对比分析）
- ✅ 文献搜索与综述（关键词策略、数据库搜索、摘要生成、综述撰写、引用格式）
- ✅ 代码生成指导（Python/NCL/GrADS/MATLAB/R 生成原则）
- ✅ 输出格式指南（5种场景）
- ✅ 报告模板（标准研究报告结构）

### 受限/未实现的功能

以下功能在原始 skill 中以独立文件形式提供，本纯 SKILL.md 版本以指导性内容替代：

- ❌ **独立脚本文件**：原始 skill 提供 20+ 个可直接运行的 Python/NCL/GrADS/MATLAB/R 脚本。本版本以代码框架和指导性片段替代，用户需根据具体数据自行实现完整脚本。
- ❌ **报告模板文件**：原始 skill 提供 `assets/report_template.md` 模板文件。本版本将模板内容内联到本文档中。
- ❌ **外部 reference 文件**：原始 skill 提供 10 个独立的 reference 文件。本版本将所有方法学内容内联到本文档中。
- ❌ **自动执行数据处理**：本 skill 提供方法学指导，但不自动执行数据下载、处理或分析。用户需自行运行代码或使用提供的环境。

## 版本信息

- 版本：1.0.0
- 创建日期：2026-04-06
- 作者：CodeArts Agent
- 更新内容：
  - v1.0.0：初始纯 SKILL.md 版本，覆盖 8 大研究维度，内联所有方法学内容






。








