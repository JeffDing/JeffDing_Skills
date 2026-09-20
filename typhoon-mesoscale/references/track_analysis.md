# 路径研究方法

## 目录

1. [最佳路径数据读取与解析](#1-最佳路径数据读取与解析)
2. [路径可视化](#2-路径可视化)
3. [移速移向计算](#3-移速移向计算)
4. [路径相似性分析](#4-路径相似性分析)
5. [路径聚类](#5-路径聚类)
6. [路径预报误差评估](#6-路径预报误差评估)

---

## 1. 最佳路径数据读取与解析

### IBTrACS NetCDF 读取

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

### CMA Best Track 解析

CMA 数据为类 ATCF 的文本格式，每行包含编号、时间、位置、强度等：

```python
col_names = ['id', 'name', 'time', 'grade', 'lat', 'lon', 'pres', 'wnd', 'wnd_dir']
df = pd.read_csv('CMA_BST.txt', sep='\s+', names=col_names, na_values='9')
# lat/lon 格式：度*10（如 152 = 15.2°），方向由符号判断
df['lat'] = df['lat'] / 10.0
df['lon'] = df['lon'] / 10.0
```

### 风速统一化

做跨机构分析前，将所有风速统一到同一标准（推荐 10-min 平均）：

```python
def unify_to_10min(wnd, source):
    factors = {'JTWC': 1/1.14, 'CMA': 1/1.10, 'JMA': 1.0, 'NHC': 1/1.14}
    return wnd * factors.get(source, 1.0)
```

---

## 2. 路径可视化

### 基本路径图（Python + Cartopy）

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

### 多路径叠加

适合展示某一时期的路径特征或路径聚类结果：

```python
for storm_id, group in all_storms.groupby('sid'):
    ax.plot(group['lon'], group['lat'], transform=ccrs.PlateCarree(), alpha=0.5)
```

### 路径密度图

用核密度估计展示路径气候态：

```python
from scipy.stats import gaussian_kde
kde = gaussian_kde(np.vstack([df['lon'], df['lat']]), bw_method=0.15)
# 在网格上评估
xi, yi = np.mgrid[100:160:200j, 5:45:200j]
zi = kde(np.vstack([xi.ravel(), yi.ravel()])).reshape(xi.shape)
ax.contourf(xi, yi, zi, levels=15, cmap='YlOrRd', transform=ccrs.PlateCarree())
```

---

## 3. 移速移向计算

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

**科学提示**：移速变化与引导气流变化相关联。路径突然北翘/西折通常意味着引导气流的改变（如副高断裂、冷空气侵入、季风涌增强），值得在分析中关注这些天气学背景。

---

## 4. 路径相似性分析

### 动态时间规整 (DTW)

DTW 能处理长度不同的路径序列，是路径相似性的常用方法：

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

### Hausdorff 距离

衡量两条路径之间的最大不匹配程度：

```python
from scipy.spatial.distance import directed_hausdorff

def hausdorff_dist(track1, track2):
    d1 = directed_hausdorff(track1, track2)[0]
    d2 = directed_hausdorff(track2, track1)[0]
    return max(d1, d2)
```

**应用**：路径相似性分析常用于——历史相似台风检索（"今年第 X 号台风的路径历史上有没有类似的"）、路径预报集成（找历史相似路径的最终归宿）、路径分类研究。

---

## 5. 路径聚类

### K-means + DTW

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

### 层次聚类

适合路径自然分类，无需预设类别数：

```python
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram

Z = linkage(dist_matrix, method='ward')
labels = fcluster(Z, t=4, criterion='maxclust')
```

**科学提示**：西北太平洋台风路径通常可归纳为西行型、西北行型、转向型和异常型，聚类结果应与副高脊线位置、西风槽活动和季风涌位置等大尺度环流型态对应。如果聚类结果与已知天气学型态不一致，可能需要检查数据预处理或聚类参数。

---

## 6. 路径预报误差评估

### 逐时绝对误差

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

### 技巧评分

```python
def skill_score(model_error, baseline_error):
    """相对于基准（如 CLIPER）的技巧评分 (%)"""
    return (1 - model_error / baseline_error) * 100
```

### 评估指标

| 指标 | 含义 | 计算方式 |
|------|------|---------|
| 24h/48h/72h 路径误差 | 各预报时效的平均误差 | 逐时大圆距离 |
| 技巧评分 | 相对于基准预报的改进程度 | (1 - 模型误差/基准误差) × 100% |
| 路向偏差 | 预报方向偏离程度 | 移向角度差 |
| 移速偏差 | 预报移速偏离程度 | 预报移速 - 最佳路径移速 |
| 稳定度 | 集合预报路径发散程度 | 各成员路径间 DTW 距离均值 |

**标准基准**：
- CLIPER（气候-持续性预报）是路径预报的标准基准，技巧评分为 0
- 技巧评分 > 0 表示优于纯统计方法
- 全球模式路径预报技巧在 72h 内可达 30-50%，而区域模式在近海可能更高

---

## 注意事项

1. **路径中断**：热带气旋可能因减弱为热带低压而中断记录，或在变性为温带气旋后记录方式改变。分析时注意 ID 是否连续。
2. **经度跨越**：路径可能跨越日界线（180°），作图时注意经度范围连续性。
3. **早期数据质量**：卫星时代前（1970 前）的路径数据不确定性较大，特别是强度估计。做气候统计时建议从 1970 或 1980 开始。
4. **登陆点信息**：IBTrACS 的 `landfall` 字段标记登陆时间点，CMA 数据含详细登陆信息（登陆地点、强度）。
