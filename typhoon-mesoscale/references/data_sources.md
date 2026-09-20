# 数据源指南

本文档汇总台风研究中常用的数据源，包括下载方式、变量清单、格式说明和使用建议。

## 目录

1. [最佳路径数据](#1-最佳路径数据)
2. [再分析数据](#2-再分析数据)
3. [卫星降水数据](#3-卫星降水数据)
4. [卫星风场数据](#4-卫星风场数据)
5. [数值模式数据](#5-数值模式数据)
6. [预报与统计预报数据](#6-预报与统计预报数据)
7. [灾情数据](#7-灾情数据)
8. [地形与陆面数据](#8-地形与陆面数据)

---

## 1. 最佳路径数据

### IBTrACS v04（NOAA NCEI）— 推荐，全球整合

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

### CMA-STI Best Track（上海台风研究所）

- **获取**：中国气象局上海台风研究所，http://www.typhoon.org.cn
- **格式**：TXT（类似 ATCF格式）
- **时间范围**：1949 年至今，每 6 小时
- **变量**：编号、国际名称、中心经纬度、中心最低气压、近中心最大风速（2-min平均）
- **特色**：包含中国大陆登陆点信息、灾害简况

### JMA Best Track（日本气象厅）

- **获取**：RSMC Tokyo，https://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks.html
- **格式**：TXT
- **时间范围**：1951 年至今，每 6 小时（部分每 3 小时）
- **变量**：中心经纬度、中心气压、最大持续风速（10-min平均）、最大瞬间风速
- **特色**：西北太平洋权威 RSMC 数据

### JTWC Best Track（美国联合台风警报中心）

- **获取**：https://www.metoc.navy.mil/jtwc/jtwc.html
- **格式**：TXT（ATCF格式 .dat）
- **时间范围**：1945 年至今，每 6 小时
- **变量**：编号、名称、经纬度、最大持续风速（1-min平均）、中心气压、风圈半径
- **特色**：包含风圈半径数据（34/50/64 kt），适合风场结构研究

### HURDAT2（NHC，北大西洋/东北太平洋）

- **获取**：https://www.nhc.noaa.gov/data/#hurdat
- **格式**：TXT
- **时间范围**：1851 年至今
- **变量**：名称、时间、经纬度、最大风速（1-min）、中心气压、强度等级

---

## 2. 再分析数据

### ERA5（ECMWF）— 最推荐

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

### JRA-55（日本气象厅）

- 时间范围：1958 至今，0.5° 分辨率
- 适用：需要更长一致记录的气候研究

### MERRA-2（NASA）

- 时间范围：1980 至今，0.5° × 0.625°
- 特色：含详细的大气水汽和能量收支变量

---

## 3. 卫星降水数据

### GPM IMERG（推荐）

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

### TRMM 3B42/3B43（历史数据）

- 时间范围：1998-2019（已停止更新）
- 分辨率：0.25°，3 小时
- 特色：长期降水气候研究，可与 GPM 衔接做时间一致性分析

### CMORPH（NOAA）

- 时间范围：1998 至今
- 分辨率：0.25°/8km，30 分钟
- 特色：纯卫星反演，无地面校正

---

## 4. 卫星风场数据

### ASCAT（MetOp 系列）

- 散射计海面风场，25/12.5 km 分辨率
- 覆盖：每日 2 次，全球
- 适用：台风外围风场验证、海面风场非对称性

### SMAP/SMOS 海面风场

- L 波段辐射计，可在强降水条件下获取海面风场
- 适用：台风内核区风场估计

### RapidScan（静止卫星）

- 风向风速推导（AMV），高频次
- 适用：台风环流演变、引导气流诊断

---

## 5. 数值模式数据

### WRF（Weather Research and Forecasting）

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

### GFS（NCEP）— 实时预报

- 分辨率：0.25°，每 6 小时到 384h
- 获取：https://nomads.ncep.noaa.gov/
- 用途：预报对比、环境场分析

### ECMWF IFS — 实时预报

- 分辨率：0.25°/0.1°（HRES），每 6h 到 240h
- 用途：预报对比（ECMWF 通常路径预报技巧最高）

### CMIP6 / HighResMIP — 气候预估

- 用途：台风活动未来情景分析
- 关键模式：HiRAM、FLOR、HadGEM3-GC31
- 变量：海温、风场、湿度（需用台风检测算法从模式输出中识别气旋）

---

## 6. 预报与统计预报数据

### SHIPS（SHIPS-RI）

- **获取**：NOAA AOML，https://www.aoml.noaa.gov/hrs/
- **内容**：各预报因子值（环境切变、SST、Pot、Persistence 等）
- **用途**：RI 预报、强度预报因子分析

### 各机构官方预报

- CMA、JMA、JTWC、NHC 每年发布预报数据
- 格式：类似 ATCF，含路径和强度预报
- 用途：预报检验、技巧评分计算

---

## 7. 灾情数据

### EM-DAT（国际灾害数据库）

- **获取**：https://www.emdat.be
- **内容**：全球自然灾害记录，含伤亡人数、经济损失
- **时间范围**：1900 至今

### 中国气象灾害年鉴

- **获取**：中国气象局
- **内容**：中国台风灾害详细记录

### IBTrACS 附带灾情

- 部分记录含登陆点信息和简单灾情描述

---

## 8. 地形与陆面数据

### ETOPO1

- 全球地形/水深，1 分分辨率
- 用途：地形降水分析、风暴潮模拟

### GTOPO30 / SRTM

- 陆地高程数据
- 用途：地形对降水和风场的影响分析

---

## 数据使用注意事项

1. **风速定义差异**：不同机构使用不同平均时段，做跨机构对比前必须统一。CMA 用 2-min，JMA 用 10-min，JTWC/NHC 用 1-min。换算关系见 IBTrACS 部分。
2. **时间对齐**：IBTrACS 每 6 小时，ERA5 每 1 小时，GPM 每 30 分钟。做多源融合时需做时间插值或选择共同时次。
3. **空间投影**：台风数据用经纬度，再分析用规则格点。画图时注意选择合适地图投影（西北太平洋用兰伯特或墨卡托，全球用等距圆柱/正交投影）。
4. **版本一致性**：ERA5 有 back-extension（1950-1978）和 main（1979-至今），拼接时需检查一致性。IBTrACS 版本更新会修改历史记录，论文中需注明使用版本。
5. **缺失值处理**：早期台风记录（特别是 1950 年代前）可靠性较低，气候统计通常截取 1970 或 1980 年后。
