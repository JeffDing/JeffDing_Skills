---
name: typhoon-mesoscale
description: 用于台风（热带气旋）科研研究的系统性工作流。涵盖路径研究、强度与风场、降水分析、环境场诊断、气候统计与趋势、数值模拟与预报检验、灾害影响评估、快速增强(RI)分析、文献搜索与综述生成。当用户提到台风/热带气旋/飓风/气旋的研究、分析、可视化、路径追踪、强度分析、降水研究、气候统计、文献综述、WRF模拟、ERA5再分析、GPM降水、IBTrACS数据、CMA/JMA/JTWC最佳路径、SHIPS因子、Mann-Kendall趋势检验、RI快速增强诊断、路径聚类、风暴潮评估、灾害评估、台风报告撰写、台风个例分析、台风对比研究、台风生成潜势、台风-ENSO关系、台风未来预估、CMIP6台风分析、深度学习台风预报，或涉及西北太平洋/南海/北大西洋/北印度洋/全球台风数据分析时，务必使用此 skill。即使用户只是提到"台风研究"、"气旋分析"、"热带气旋科研"而未明确具体方向，也应触发此 skill 以引导用户进入完整的研究工作流。不要只做简单的单步数据处理，要用此 skill 提供完整的研究分析框架。
---

# 台风中尺度系统科研研究

## 概述

本 skill 为台风（热带气旋）科研研究提供系统化的工作流，覆盖从数据获取、分析可视化到文献综述的完整流程。适用于气象/大气科学领域的研究人员，支持西北太平洋、北大西洋、东北太平洋、北印度洋、南半球等全球各海域。

设计理念：**方法论导向**，而非简单的画图工具——每个研究维度都包含科学背景、标准方法、关键指标和注意事项，帮助研究者做出规范、可发表的分析。

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

详细数据源信息见 `references/data_sources.md`。

### 第二步：确定研究维度

根据用户需求识别一个或多个研究维度：

| # | 研究维度 | 典型用户表述 | 详细方法见 |
|---|---------|-------------|-----------|
| 1 | 路径研究 | "台风路径""轨迹分析""路径相似性" | `references/track_analysis.md` |
| 2 | 强度与风场 | "强度变化""最大风速""风场结构""眼壁" | `references/intensity_wind_analysis.md` |
| 3 | 降水分析 | "降雨分布""暴雨""降水非对称性""GPM" | `references/precipitation_analysis.md` |
| 4 | 环境场诊断 | "SST""垂直切变""引导气流""湿度" | `references/environment_diagnosis.md` |
| 5 | 气候统计与趋势 | "频数变化""长期趋势""ENSO""气候态" | `references/climate_statistics.md` |
| 6 | 数值模拟与预报检验 | "WRF""预报误差""模式对比""检验" | `references/numerical_modeling.md` |
| 7 | 灾害影响评估 | "风灾""暴雨灾害""经济损失""伤亡" | `references/disaster_assessment.md` |
| 8 | 快速增强(RI) | "快速增强""RI""SHIPS""骤然增强" | `references/rapid_intensification.md` |

用户可能同时涉及多个维度——例如"分析台风 Hato 的路径和降水特征"涉及维度 1+3。逐个读取对应 reference 文件获取方法学指导。

### 第三步：数据获取

根据海域和研究维度，确定需要哪些数据：

- **最佳路径数据**：IBTrACS（全球）、CMA-STI（西北太平洋）、HURDAT2（大西洋/东太平洋）
- **再分析数据**：ERA5（最常用）、JRA-55、MERRA-2
- **卫星降水**：GPM IMERG（近实时+研究级）、TRMM 3B42（历史）
- **卫星风场**：ASCAT、RapidScan、SMAP
- **数值模式输出**：WRF、GFS、ECMWF-IFS
- **预报数据**：各机构官方预报、SHIPS 统计-动力预报

具体下载方式、变量清单、格式说明见 `references/data_sources.md`。

若用户提供了本地数据文件，跳过下载步骤，直接进入分析。

### 第四步：分析与可视化

根据研究维度，读取对应的 reference 文件了解标准方法，然后：

1. **选择脚本**：本 skill 在 `scripts/` 下提供了 Python、NCL、GrADS、MATLAB、R 五种语言的脚本。根据用户偏好语言选择对应脚本，直接使用或按需修改。脚本路径见下方"脚本索引"。
2. **执行分析**：运行脚本处理数据，生成中间结果和图表。
3. **多语言代码生成原则**：当用户需要自定义代码时，按用户指定语言生成。若用户未指定，默认用 Python（气象领域最通用）。所有生成的代码应附 markdown 格式的逐行/逐段说明，让用户理解原理后可自行修改。
4. **方法学引导**：不仅是画图——在分析过程中提醒用户关注科学意义，如"路径北翘可能与副热带高压断裂有关""降水非对称性需考虑地形和环境风切变"。

### 第五步：文献搜索与综述

详见下方"文献搜索工作流"和 `references/literature_review.md`。

### 第六步：输出

根据任务性质选择输出格式，详见下方"输出格式指南"。

---

## 研究维度索引

以下为各维度的简要说明，完整方法学在对应 reference 文件中。

### 1. 路径研究（`references/track_analysis.md`）

- 最佳路径数据读取与解析（IBTrACS CSV、CMA 格式）
- 路径可视化：轨迹图、彩色路径（按强度/时间着色）
- 路径相似性分析：动态时间规整(DTW)、Hausdorff 距离
- 路径聚类：K-means、层次聚类
- 移速移向计算与统计
- 路径预报误差评估：逐时/逐 24h 误差、引导气流对比

### 2. 强度与风场研究（`references/intensity_wind_analysis.md`）

- 强度时间序列：Vmax、Pmin 演变曲线
- 强度分级与等级转换：CMA/SSHWS/泛热带气旋分级对照
- 风场结构分析：最大风速半径(RMW)、34/50/64 kt 风圈半径
- 非对称风场重建：轴对称平均 + 傅里叶分解
- 眼壁与螺旋雨带识别
- 暖心结构诊断
- Dvorak 技术（卫星强度估计）原理与局限性

### 3. 降水分析（`references/precipitation_analysis.md`）

- 卫星降水数据处理：GPM IMERG（Final/Late/Early Run）、TRMM 3B42/3B43
- 降水空间分布：等值线图、填色图
- 降水时间演变：Hovmöller 图、面积平均降水时间序列
- 降水非对称性分析：方位角-半径分布、傅里叶分解
- 地形增强效应诊断
- 极端降水统计：GEV/GPD 拟合、重现期计算
- 降水形态分类：层状/对流性（利用 TRMM PR/GPM DPR）

### 4. 环境场诊断（`references/environment_diagnosis.md`）

- 海表温度(SST)：空间分布、台风冷尾迹(SST cooling)
- 垂直风切变：200-850 hPa 切变计算、深层/浅层切变
- 大气湿度：相对湿度廓线、水汽输送
- 引导气流：深层平均气流计算
- 位涡(PV)：高空 PV 异常与台风发展
- 潜在强度(PI)：Emanuel 公式计算
- 热力学环境：CAPE、CIN、假相当位温

### 5. 气候统计与趋势（`references/climate_statistics.md`）

- 频数气候态：年际/年代际变化、季节分布
- 强度气候态：各级强度频数分布
- 路径气候态：密度分布图、盛行路径
- 长期趋势检测：Mann-Kendall 趋势检验、线性回归
- 年际变率：ENSO/PDO/MODIKI 遥相关
- 生成潜势指数(GPI)：Emanuel-Nolan 公式
- 未来预估：CMIP6/HighResMIP 情景分析

### 6. 数值模拟与预报检验（`references/numerical_modeling.md`**

- WRF 模式配置：微物理、积云、PBL、海面通量方案选择
- WRF 输出分析：wrf-python 处理、诊断量计算
- 涡旋追踪(Bogus)与初始化
- 预报检验标准：逐时绝对误差、相对误差、技巧评分
- 多模式对比：GFS/ECMWF/UM/GRAPES
- 集合预报：概率预报、 dispersedness
- 错涡诊断：初始场误差增长

### 7. 灾害影响评估（`references/disaster_assessment.md`）

- 风灾评估：风场重建 + 脆弱性曲线
- 暴雨灾害：降水阈值 + 历史重现期对比
- 风暴潮：SLOSH/ADCIRC 模型输出分析
- 经济损失统计：历史灾情数据库、归一化方法
- 伤亡分析：与强度的统计关系
- 综合风险评估：多因子叠加、风险等级划分

### 8. 快速增强(RI)分析（`references/rapid_intensification.md`**

- RI 定义与判据：30 kt/24h（Kaplan-DeMaria）、35 kt/24h
- SHIPS 预报因子：环境场因子、持续性因子、内部结构因子
- RI 概率预报：SHIPS-RI、DTFA、深度学习方法
- RI 环境条件：暖SST、弱切变、高湿度、高空辐散
- RI 内部过程：眼壁收缩、对流体耦合、暖心增强
- RI 个例对比分析：RI vs 非 RI 环境场差异
- 近年来 RI 预报能力评估

---

## 数据源速查

| 数据 | 来源 | 格式 | 时间范围 | 详见 |
|------|------|------|---------|------|
| IBTrACS v04 | NOAA NCEI | NetCDF/CSV | 1842-至今 | `references/data_sources.md` |
| CMA Best Track | CMA-TJ | TXT/CSV | 1949-至今 | 同上 |
| JMA Best Track | JMA RSMC Tokyo | TXT | 1951-至今 | 同上 |
| JTWC | JTWC Guam | TXT | 1945-至今 | 同上 |
| HURDAT2 | NHC | TXT | 1851-至今 | 同上 |
| ERA5 | ECMWF CDS | NetCDF/GRIB | 1940-至今 | 同上 |
| GPM IMERG | NASA GES DISC | NetCDF/HDF5 | 2000-至今 | 同上 |
| SHIPS | NOAA AOML | TXT | 1989-至今 | 同上 |

---

## 脚本索引

本 skill 在 `scripts/` 目录下提供五种语言的脚本。每个脚本头部有使用说明注释，可直接运行或按需修改。

### Python 脚本（`scripts/python/`）

Python 是气象科学计算的主语言，以下脚本使用 xarray + cartopy + numpy 技术栈：

| 脚本 | 功能 | 关键依赖 |
|------|------|---------|
| `download_track_data.py` | 下载 IBTrACS/CMA/JMA 最佳路径数据 | requests, pandas |
| `plot_typhoon_track.py` | 绘制台风路径图（彩色强度/时间） | cartopy, matplotlib |
| `intensity_time_series.py` | 强度演变时间序列 | matplotlib, pandas |
| `wind_field_analysis.py` | 风场结构与非对称性分析 | xarray, numpy |
| `precipitation_analysis.py` | GPM 降水数据处理与可视化 | xarray, cartopy |
| `environment_diagnosis.py` | ERA5 环境场诊断（SST/切变/湿度） | xarray, metpy |
| `climate_statistics.py` | 频数/趋势/遥相关统计 | scipy, statsmodels |
| `forecast_verification.py` | 预报误差统计与技巧评分 | pandas, matplotlib |
| `ri_diagnosis.py` | 快速增强诊断与 SHIPS 因子分析 | pandas, sklearn |

### NCL 脚本（`scripts/ncl/`）

NCL（NCAR Command Language）在中国气象界广泛使用：

| 脚本 | 功能 |
|------|------|
| `plot_track.ncl` | 路径图（支持彩色强度、多路径叠加） |
| `environment_fields.ncl` | 环境场填色+等值线图（SST、位势高度等） |

### GrADS 脚本（`scripts/grads/`）

GrADS 擅长格点数据的快速诊断分析：

| 脚本 | 功能 |
|------|------|
| `track_overlay.gs` | 路径叠加在再分析场上 |
| `precipitation_diagnosis.gs` | 降水诊断（Hovmöller、面积平均） |

### MATLAB 脚本（`scripts/matlab/`）

| 脚本 | 功能 |
|------|------|
| `wind_field_analysis.m` | 风场结构与轴对称分解 |

### R 脚本（`scripts/r/`）

R 在统计分析和气候研究中有优势：

| 脚本 | 功能 |
|------|------|
| `climate_trend_analysis.R` | 气候趋势检验（Mann-Kendall、Sen 斜率） |
| `precipitation_stats.R` | 降水极值统计（GEV/GPD 拟合） |

---

## 文献搜索工作流

详见 `references/literature_review.md` 获取完整方法。核心流程：

### 1. 关键词策略

将研究主题拆解为概念组，每组列出同义词：

```
概念组A（现象）：typhoon / tropical cyclone / hurricane / 台风 / 热带气旋
概念组B（维度）：track / intensity / rainfall / rapid intensification / ...
概念组C（方法）：climatology / trend / WRF / SHIPS / ...
概念组D（海域）：Western North Pacific / South China Sea / ...
```

### 2. 搜索执行

- 使用 webfetch 访问 Google Scholar / Semantic Scholar / NASA ADS
- 对中文文献，搜索中国知网(CNKI)的关键词组合
- 优先检索近 5 年高被引论文，再追溯其参考文献

### 3. 摘要生成

对检索到的每篇文献：
- 提取标题、作者、期刊、年份、被引次数
- 用 2-3 句话概括核心发现
- 标注研究方法、数据源、主要结论

### 4. 综述撰写

按主题组织文献摘要，形成结构化综述：
- 研究背景与问题
- 主要方法与技术路线
- 关键发现（按主题分组）
- 研究空白与未来方向

---

## 输出格式指南

根据任务性质灵活选择：

| 场景 | 推荐输出 | 说明 |
|------|---------|------|
| 数据处理/画图 | 可运行代码 + 图表文件 | 代码附 markdown 逐段说明 |
| 个例分析 | 分析报告（结构化文本+图表） | 参见 `assets/report_template.md` |
| 气候统计 | 统计表格 + 图表 + 方法说明 | 含统计检验结果 |
| 文献综述 | 结构化综述文本 | 含引用列表 |
| 多维度综合研究 | 完整研究报告 | 各维度分节，最后综合讨论 |

**报告模板**：`assets/report_template.md` 提供了标准研究报告结构，可按需裁剪。

---

## 代码生成原则

1. **多语言支持**：用户指定语言时按指定语言生成；未指定时默认 Python。所有五种语言（Python/NCL/GrADS/MATLAB/R）的参考脚本均在 `scripts/` 下。
2. **可读性优先**：代码配 markdown 说明——关键步骤解释为什么这样做、参数含义、可能的替代方案。
3. **可复现性**：固定随机种子、标注数据版本和下载日期、注明依赖包版本。
4. **科研规范**：统计检验标注 p 值、图表标注单位和坐标轴、地图投影注明、色标选择考虑色觉友好。
5. **渐进引导**：对于复杂分析，先给骨架代码让用户跑通，再逐步增加诊断量和可选参数。

---

## 使用建议

- 用户的表述可能模糊（如"帮我分析下这个台风"），主动追问：哪个台风/哪个海域/想做什么维度/有没有数据
- 研究维度之间常有交叉——路径+强度+降水是常见组合，环境场诊断可能同时服务于 RI 分析和个例研究
- 若用户是研究生或刚入门，在分析时多解释科学背景和为什么选择某方法；若用户是资深研究者，可更直接地给方法和代码
- 鼓励用户先确定数据是否就绪再开始分析——数据问题是科研中最常见的卡点
