# 降水分析方法

## 目录

1. [卫星降水数据处理](#1-卫星降水数据处理)
2. [降水空间分布](#2-降水空间分布)
3. [降水时间演变](#3-降水时间演变)
4. [降水非对称性分析](#4-降水非对称性分析)
5. [地形增强效应诊断](#5-地形增强效应诊断)
6. [极端降水统计](#6-极端降水统计)
7. [降水形态分类](#7-降水形态分类)

---

## 1. 卫星降水数据处理

### GPM IMERG Final Run 读取

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

### 台风区域裁剪

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

### 累积降水计算

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
            lon=slice(lon_c - radius_deg, lon_c + radius_deg)
        )
        result.append({'time': t, 'mean_precip': float(region.mean()),
                       'max_precip': float(region.max())})
    return pd.DataFrame(result)
```

---

## 2. 降水空间分布

### 等值线填色图

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

### 极坐标降水分布

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

---

## 3. 降水时间演变

### Hovmöller 图

Hovmöller 图展示降水随时间和半径（或方位角）的演变，是台风降水诊断的经典工具：

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

### 方位角-时间 Hovmöller

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

**科学提示**：Hovmöller 图能揭示——眼壁置换过程中降水双峰结构的时间演变、螺旋雨带的旋转传播（方位角方向的波动）、外雨带向内传播的对流信号。半径-时间图中的向内传播通常与涡旋罗斯贝波有关。

---

## 4. 降水非对称性分析

### 方位角分布与傅里叶分解

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

### 非对称性的物理来源

| 非对称分量 | 典型方向 | 物理机制 |
|-----------|---------|---------|
| 移动方向非对称 | 移动方向右侧（北半球） | 涡旋移动速度叠加 |
| 切变方向非对称 | 切变下风方 | 深对流在切变下风方发展 |
| 地形非对称 | 迎风坡 | 地形抬升增强降水 |
| 内核非对称 | 随时间变化 | 涡旋罗斯贝波、VHTs组织化 |

**分析要点**：
- 降水非对称性在台风登陆时最强（地形+摩擦+移动效应叠加）
- 切变下风方降水增强是业务预报关注重点——切变方向决定了暴雨落区
- 分离各因子的贡献需要：比较陆地/海洋台风、改变切变方向、对比有无地形

---

## 5. 地形增强效应诊断

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

**科学提示**：地形增强是台风暴雨预报的核心难点。中国台湾岛、菲律宾吕宋岛、日本本州岛、中国东南沿海丘陵对台风降水有显著增强作用。典型量级：台湾中央山脉可使降水增幅 2-3 倍。地形效应与台风移速有关——慢速移动台风有更充分的地形抬升时间。

---

## 6. 极端降水统计

### 年最大值序列 (AMS)

```python
def annual_max_series(daily_precip_series, threshold=None):
    """构建年最大降水序列"""
    yearly_max = daily_precip_series.resample('Y').max()
    return yearly_max
```

### GEV 拟合（广义极值分布）

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

### GPD 拟合（超阈值模型，POT）

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

**方法选择**：
- GEV（年最大值法）：适合较长记录（>20年），稳定性好但采样效率低
- GPD（超阈值法）：适合较短记录，采样效率高但阈值选择敏感
- 台风降水的极端性通常比一般降水更强，GEV/GPD 的形状参数可能为正（重尾分布）

---

## 7. 降水形态分类

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

**科学提示**：台风降水中层状性降水通常占面积 70-80%，但贡献总降水约 50-60%；对流性降水面积占 20-30%，但贡献 40-50%。眼壁主要是对流性降水，外雨带以层状性为主。降水形态的演变与台风强度变化有关——减弱的台风往往对流比例下降。

---

## 注意事项

1. **IMERG 数据的不确定性**：GPM IMERG 在强降水（>50 mm/hr）时可能低估，在弱降水时可能高估。地形区的卫星反演精度更差。建议用地面雨量站数据做验证。
2. **时间匹配**：IMERG 是 30 分钟数据，最佳路径是 6 小时间隔。做相关分析时需统一时间分辨率。
3. **陆地 vs 海洋精度**：IMERG 在海洋上精度较好（无地形干扰），陆地上受地形和岸基影响，误差增大。
4. **极端事件评估**：单个台风的极端降水不能简单归因于气候变化——需要用归因方法（如条件归因法）区分气候变率和自然变率的贡献。
