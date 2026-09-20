# 快速增强 (RI) 分析方法

## 目录

1. [RI 定义与判据](#1-ri-定义与判据)
2. [SHIPS 预报因子](#2-ships-预报因子)
3. [RI 概率预报](#3-ri-概率预报)
4. [RI 环境条件诊断](#4-ri-环境条件诊断)
5. [RI 内部过程分析](#5-ri-内部过程分析)
6. [RI vs 非 RI 对比分析](#6-ri-vs-非-ri-对比分析)
7. [RI 预报能力评估](#7-ri-预报能力评估)

---

## 1. RI 定义与判据

### 标准定义

快速增强(Rapid Intensification, RI)是台风预报中最具挑战性的过程：

| 定义来源 | 判据 | 说明 |
|---------|------|------|
| Kaplan & DeMaria (2006) | 30 kt/24h | 最常用，SHIPS-RI 标准 |
| Kaplan et al. (2010) | 35 kt/24h | 更高阈值 |
| Xu & Wang (2015) | 20 m/s/24h | CMA 研究 |
|极端增强 | 40+ kt/24h | 极端事件 |

### 代码实现

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

### RI 发生频率

- 全球热带气旋中 RI 发生率约 20-30%
- 西北太平洋 RI 发生率较高（约 25-35%）
- 大西洋约 15-25%
- RI 多发生在 60 kt 以下的发展阶段——已经很强的台风 RI 概率降低

---

## 2. SHIPS 预报因子

SHIPS (Statistical Hurricane Intensity Prediction Scheme) 提供了系统化的强度预报因子体系：

### 主要因子分类

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

### SHIPS 数据读取

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

---

## 3. RI 概率预报

### SHIPS-RI

SHIPS-RI 是基于逻辑回归的 RI 概率预报模型：

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

### 深度学习方法

近年来深度学习在 RI 预报中展现了潜力：

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

---

## 4. RI 环境条件诊断

### RI 有利条件综合判据

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

### 环境因子阈值参考

| 因子 | RI 有利 | RI 不利 | 来源 |
|------|---------|---------|------|
| SST | > 28.5°C | < 27°C | Kaplan & DeMaria (2006) |
| 深层切变 | < 8 m/s | > 15 m/s | Kaplan & DeMaria (2006) |
| 中层RH (700-500) | > 60% | < 50% | Kaplan & DeMaria (2006) |
| 高空散度 (200hPa) | > 2 × 10⁻⁶ s⁻¹ | < 0 | |
| OHC | > 50 kJ/cm² | < 20 kJ/cm² | Lin et al. (2013) |
| 初始强度 | 30-65 kt | > 100 kt | 已强的台风RI概率低 |
| 移速 | < 5 m/s | > 10 m/s | |

**科学提示**：单因子阈值判断 RI 的效果有限——RI 往往需要多个条件同时满足。Kaplan & DeMaria 发现满足 5 个以上条件时 RI 概率约 40%，但仅满足 2-3 个条件时 RI 概率仍可达 10-15%（假阳性率高）。多因子的"非线性组合"效应是 RI 预报的核心难点。

---

## 5. RI 内部过程分析

### 眼壁收缩

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

### 内部过程关键指标

| 指标 | RI 中典型变化 | 检测方法 |
|------|-------------|---------|
| 眼壁半径 | 缩小（50→30 km） | 卫星微波、雷达 |
| 眼直径 | 减小 | 红外/可见光卫星 |
| 对流深度 | 增加（CTT降低） | 红外亮温 |
| 雷暴频数 | 增加 | 红外/微波 |
| 暖心强度 | 增强 | AMSU/MHS |
| 轴对称化 | 提高 | 旋转对称度 |
| 涡旋罗斯贝波 | 向内传播 | 波数分析 |

---

## 6. RI vs 非 RI 对比分析

### 合成(Composite)分析

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

### 对比分析要点

在对比 RI 和非 RI 事件时，需注意：
1. **匹配初始强度**：RI 更多发生在中等强度（40-65 kt），直接对比不同初始强度的事件会引入偏差。建议按初始强度区间做匹配。
2. **匹配海域和季节**：不同海域的 RI 概率不同。
3. **样本量**：RI 是相对稀有事件（约 20%），合成分析需要足够的样本（通常 >50 例）。
4. **时间对齐**：合成分析需要以 RI 发生时刻为时间原点（t=0），前后各取若干时段。

---

## 7. RI 预报能力评估

### 常用指标

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

### 当前预报水平参考

| 方法 | POD | FAR | 说明 |
|------|-----|-----|------|
| SHIPS-RI | ~30-40% | ~30-40% | 命中率低，虚警率高 |
| 深度学习 | ~50-60% | ~25-35% | 近年改善明显 |
| 人类预报员 | ~40-50% | ~30-40% | 综合多源信息 |

**科学提示**：RI 预报是台风强度预报的核心难点。目前业务预报的 POD 普遍低于 50%，意味着超过一半的 RI 事件无法提前预报。这主要是因为 RI 的物理机制——内部对流的组织化过程——在当前观测分辨率下难以充分捕捉。

---

## 注意事项

1. **RI 的定义敏感性**：30 kt/24h vs 35 kt/24h 的判定结果可能有 20% 的差异。研究中需注明使用的具体定义。
2. **时间分辨率影响**：6 小时间隔的最佳路径数据可能平滑掉短时峰值增强。理想情况下应使用逐时或 3 小时间隔数据。
3. **RI 的季节性**：西北太平洋 RI 多发生在 7-10 月（SST 高、切变弱），冬季几乎不发生。
4. **RI 和眼壁置换的关系**：眼壁置换过程中的暂时减弱可能被误判为 RI 的"反面"，而置换完成后的再次增强可能触发 RI。两者需区分。
5. **模式模拟 RI 的限制**：粗网格（>5 km）模式难以模拟 RI——对流组织化、眼壁形成等过程需要高分辨率。做 RI 机理研究建议用 ≤2 km 的对流分辨模拟。
