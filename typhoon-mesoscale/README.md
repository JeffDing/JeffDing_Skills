# typhoon-mesoscale：台风（热带气旋）科研研究

## 技能简介

`typhoon-mesoscale` 是一个面向气象科研人员的台风/热带气旋系统性研究技能，提供从数据获取、分析可视化到文献综述的完整工作流。覆盖路径研究、强度与风场、降水分析、环境场诊断、气候统计与趋势、数值模拟与预报检验、灾害影响评估、快速增强（RI）分析等核心研究维度。

## 核心功能

1. **海域识别**：自动适配西北太平洋、北大西洋、东北太平洋、北印度洋、南半球/全球等海域的数据源与机构预报
2. **维度引导**：根据用户需求精准识别 8 大研究维度，并引导至对应方法学文档
3. **数据获取**：提供 IBTrACS、CMA-STI、HURDAT2、ERA5、GPM IMERG、SHIPS 等核心数据的下载与处理方案
4. **分析与可视化**：内置 Python、NCL、GrADS、MATLAB、R 五种语言的参考脚本，支持路径、强度、降水、环境场等分析
5. **文献搜索与综述**：提供标准化的关键词策略、搜索执行、摘要生成与综述撰写工作流
6. **报告输出**：支持个例分析报告、气候统计表格、文献综述、多维度综合研究报告等多种输出格式

## 使用场景

- 用户提到“台风路径分析”“强度变化”“降水分布”“气候趋势”“WRF 模拟”“快速增强”“灾害评估”等研究需求
- 用户需要进行台风个例研究、对比研究、气候统计分析或文献综述
- 用户提到西北太平洋、南海、北大西洋、北印度洋等海域的台风数据分析
- 用户提到 IBTrACS、ERA5、GPM、CMA 最佳路径、SHIPS 等数据源

## 研究维度

| # | 研究维度 | 关键内容 |
|---|---------|---------|
| 1 | 路径研究 | 最佳路径解析、DTW 相似性、K-means 聚类、移速移向、预报误差评估 |
| 2 | 强度与风场 | Vmax/Pmin 演变、RMW 与风圈、非对称风场重建、Dvorak 技术 |
| 3 | 降水分析 | GPM/TRMM 降水、方位角-半径分布、Hovmöller 图、GEV/GPD 极值统计 |
| 4 | 环境场诊断 | SST、垂直风切变、引导气流、位涡(PV)、潜在强度(PI)、CAPE/CIN |
| 5 | 气候统计与趋势 | 频数/强度/路径气候态、Mann-Kendall 趋势、ENSO/PDO 遥相关、GPI、CMIP6 |
| 6 | 数值模拟与预报检验 | WRF 配置、wrf-python 诊断、预报技巧评分、多模式对比、集合预报 |
| 7 | 灾害影响评估 | 风灾评估、暴雨阈值、风暴潮、经济损失、综合风险评估 |
| 8 | 快速增强(RI) | RI 判据、SHIPS 因子、RI 概率预报、暖 SST/弱切变等环境条件诊断 |

## 文件结构

```
typhoon-mesoscale/
├── SKILL.md                 # 技能核心文件，包含完整工作流与方法学指导
├── README.md                # 技能说明文档
├── assets/
│   └── report_template.md   # 研究报告模板
├── evals/
│   └── evals.json           # 测试用例
├── references/
│   ├── data_sources.md          # 数据源速查与下载指南
│   ├── track_analysis.md        # 路径研究方法学
│   ├── intensity_wind_analysis.md  # 强度与风场研究方法学
│   ├── precipitation_analysis.md    # 降水分析方法学
│   ├── environment_diagnosis.md     # 环境场诊断方法学
│   ├── climate_statistics.md        # 气候统计与趋势方法学
│   ├── numerical_modeling.md        # 数值模拟与预报检验方法学
│   ├── disaster_assessment.md       # 灾害影响评估方法学
│   ├── rapid_intensification.md     # 快速增强(RI)分析方法学
│   └── literature_review.md         # 文献搜索与综述方法学
└── scripts/
    ├── python/   # Python 脚本（xarray + cartopy + numpy 技术栈）
    ├── ncl/      # NCL 脚本
    ├── grads/    # GrADS 脚本
    ├── matlab/   # MATLAB 脚本
    └── r/        # R 脚本
```

## 使用示例

**示例 1：路径与降水分析**
```
用户：分析台风 Hato 的路径和降水特征
技能：读取 references/track_analysis.md 和 references/precipitation_analysis.md，
      引导用户确认海域与数据源，选择对应脚本进行分析
```

**示例 2：气候趋势研究**
```
用户：研究西北太平洋台风频数的长期趋势
技能：读取 references/climate_statistics.md，
      指导用户使用 IBTrACS 数据，进行 Mann-Kendall 趋势检验与 ENSO 遥相关分析
```

**示例 3：WRF 模拟检验**
```
用户：检验 WRF 模式对台风路径的预报效果
技能：读取 references/numerical_modeling.md，
      指导用户计算逐时/逐 24h 预报误差与技巧评分
```

## 技能触发关键词

- 台风研究、热带气旋分析、飓风分析、气旋科研
- 台风路径、轨迹分析、路径聚类、路径相似性
- 强度分析、最大风速、风场结构、眼壁、快速增强、RI
- 降水分析、暴雨、GPM、TRMM、降水非对称性
- 环境场诊断、SST、垂直切变、引导气流、位势高度
- 气候统计、长期趋势、ENSO、CMIP6、生成潜势
- WRF 模拟、数值模式、预报检验、技巧评分
- 灾害评估、风暴潮、经济损失、风险评估
- 文献综述、台风报告、个例分析、对比研究

## 安装方法

```
从 https://gitcode.com/JeffDing/JeffDing_Skills/tree/main/typhoon-mesoscale 安装 skills 到 ~/.codeartsdoer/skills/
```

## 版本信息

- 版本：1.0.0
- 创建日期：2026-04-06
- 作者：CodeArts Agent
- 更新内容：
  - v1.0.0：初始版本，覆盖 8 大研究维度，支持 5 种编程语言脚本
