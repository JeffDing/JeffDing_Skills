# 数值模拟与预报检验方法

## 目录

1. [WRF 模式配置](#1-wrf-模式配置)
2. [WRF 输出分析](#2-wrf-输出分析)
3. [涡旋初始化与 Bogus](#3-涡旋初始化与-bogus)
4. [预报检验标准](#4-预报检验标准)
5. [多模式对比](#5-多模式对比)
6. [集合预报分析](#6-集合预报分析)
7. [误差增长诊断](#7-误差增长诊断)

---

## 1. WRF 模式配置

### 台风研究推荐配置

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

### namelist.input 关键参数

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

**科学提示**：网格分辨率对台风模拟至关重要。<5 km 时可以分辨眼壁结构；1-2 km 可以分辨双眼壁和螺旋雨带。但分辨率越高计算成本越大，需要权衡。积云对流方案在 <4 km 时应关闭（对流已被显式解析），但有些研究表明 4-8 km 网格仍需部分积云修正。

---

## 2. WRF 输出分析

### wrf-python 处理

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

### 台风中心定位

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

### 诊断量计算

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

---

## 3. 涡旋初始化与 Bogus

### 涡旋重定位和强度调整

模式初始场中的涡旋通常位置和强度不准确，需要做 bogus 处理：

```python
# WRF 的涡旋初始化通过 namelist 控制
&domains
 vortex_interval = 120,       # 涡旋初始化间隔（分钟）
 max_vortex_intensity = 30,   # 最大强度（m/s）
 remove_existing_bogus_storms = .true.,
```

### 涡旋分离

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

**科学提示**：涡旋分离是台风数值模拟的重要预处理。错误初始涡旋会导致前 12-24h 的"spin-up"问题——模式需要时间让涡旋与动力框架协调。Bogus 方案可以加速 spin-up，但可能导致与实际不一致。

---

## 4. 预报检验标准

### 路径预报误差

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

### 强度预报误差

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

### 技巧评分

```python
def skill_score(forecast_error, baseline_error):
    """技巧评分 = (1 - 预报误差/基准误差) × 100%"""
    return (1 - forecast_error / baseline_error) * 100
```

**标准基准模型**：
- 路径：CLIPER（气候-持续性预报）
- 强度：SHIFOR（气候-持续性强度预报）
- SHIPS（统计-动力强度预报）是更高级的基准

### 常用检验指标汇总

| 指标 | 路径 | 强度 | 集合 |
|------|------|------|------|
| 绝对误差 (AE) | 大圆距离 (km) | Vmax 差 (kt) | — |
| 偏差 (Bias) | 预报-实际位置差 | 预报-实际强度差 | — |
| 技巧评分 | 相对CLIPER | 相对SHIFOR | — |
| 集合散布 | — | — | 成员间路径DTW均值 |
| Brier评分 | — | RI概率预报 | 概率预报准确性 |
| 可靠性图 | — | — | 概率预报校准 |

---

## 5. 多模式对比

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

**全球模式路径预报参考水平（近年）**：
- ECMWF-IFS：72h 误差约 200 km（最佳）
- UKMO：72h 误差约 250 km
- GFS：72h 误差约 280 km
- 区域模式（如 BAM、HWRF）：近海路径可能更优

---

## 6. 集合预报分析

### 集合离散度

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

### Talagrand 直方图

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

**科学提示**：理想的集合离散度应等于均方根误差(RMSE)。如果离散度 < RMSE，集合欠发散（under-dispersive），概率预报过于自信。全球模式路径预报的集合通常就是欠发散的。

---

## 7. 误差增长诊断

### 初值误差敏感试验

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

### 误差增长倍增时间

台风预报误差的倍增时间约 1.5-2.5 天（可预报性上限约 2 周）。路径预报误差在 72h 后增长明显加快。

---

## 注意事项

1. **WRF 版本兼容**：不同 WRF 版本的物理方案选项可能不同。WRF 4.x 系列推荐 Thompson 微物理的优化版本。
2. **Spin-up 时间**：模式启动后前 6-12 小时物理场需要协调（spin-up），这段时间的输出通常不用做分析。涡旋初始化可以缩短 spin-up。
3. **边界条件更新频率**：嵌套边界条件更新频率应至少每 6 小时一次，高频更新（如每 1 小时）可减少边界伪反射。
4. **预报检验的样本量**：个例检验意义有限，业务检验通常需要至少一个台风季节（30-50 个样本）才能有统计意义。
5. **模式分辨率与涡旋表示**：粗网格（>10 km）可能无法解析台风眼，涡旋会偏大偏弱。做结构研究至少需要 2-5 km 分辨率。
