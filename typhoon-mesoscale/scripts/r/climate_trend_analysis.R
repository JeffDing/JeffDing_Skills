#############################################################################
# climate_trend_analysis.R
#
# 功能：台风气候趋势分析（R语言版本）
#   - Mann-Kendall 趋势检验
#   - Sen 斜率估计
#   - Pettitt 变点检验
#   - ENSO 遥相关分析
#   - 趋势可视化
#
# 依赖：trend, Kendall, ggplot2
# 安装：install.packages(c("trend", "Kendall", "ggplot2"))
#############################################################################

# 加载包
library(trend)
library(Kendall)
library(ggplot2)

# ============================================================
# 1. Mann-Kendall 趋势检验
# ============================================================

mk_test <- function(series) {
  """
  Mann-Kendall 趋势检验

  参数：
    series: 时间序列数值向量

  返回：列表含 Z, p, Sen 斜率
  """
  result <- mk.test(series)

  # Sen 斜率
  sen <- sens.slope(series)

  cat("=== Mann-Kendall 趋势检验 ===\n")
  cat(sprintf("Z 统计量: %.3f\n", result$statistic))
  cat(sprintf("p 值: %.4f\n", result$p.value))
  cat(sprintf("Sen 斜率: %.4f/年 (%.2f/十年)\n", sen$estimates, sen$estimates * 10))

  if (result$p.value < 0.05) {
    if (result$statistic > 0) {
      cat("结论: 显著上升趋势\n")
    } else {
      cat("结论: 显著下降趋势\n")
    }
  } else {
    cat("结论: 趋势不显著\n")
  }

  return(list(
    Z = result$statistic,
    p = result$p.value,
    sen_slope = sen$estimates,
    trend = ifelse(result$p.value < 0.05,
                  ifelse(result$statistic > 0, "increasing", "decreasing"),
                  "not significant")
  ))
}

# ============================================================
# 2. Pettitt 变点检验
# ============================================================

pettitt_test <- function(series, years) {
  """
  Pettitt 变点检验——检测时间序列中的突变点

  参数：
    series: 时间序列数值向量
    years: 对应年份

  返回：变点位置和显著性
  """
  result <- pettitt.test(series)

  if (result$p.value < 0.05) {
    change_year <- years[result$estimate]
    cat(sprintf("\n=== Pettitt 变点检验 ===\n"))
    cat(sprintf("变点年份: %d\n", change_year))
    cat(sprintf("p 值: %.4f (显著)\n", result$p.value))

    before <- series[1:result$estimate]
    after <- series[(result$estimate + 1):length(series)]
    cat(sprintf("变点前均值: %.1f\n", mean(before)))
    cat(sprintf("变点后均值: %.1f\n", mean(after)))
  } else {
    cat(sprintf("\n变点不显著 (p = %.4f)\n", result$p.value))
  }

  return(result)
}

# ============================================================
# 3. ENSO 遥相关分析
# ============================================================

enso_correlation <- function(tc_freq, nino34, years) {
  """
  台风频数与 ENSO 的相关分析

  参数：
    tc_freq: 年台风频数向量
    nino34: Niño3.4 指数向量
    years: 年份向量
  """
  # Pearson 相关
  r_pearson <- cor(tc_freq, nino34, method = "pearson")
  # Spearman 秩相关
  r_spearman <- cor(tc_freq, nino34, method = "spearman")

  # 显著性检验
  test <- cor.test(tc_freq, nino34)

  cat("\n=== ENSO 相关分析 ===\n")
  cat(sprintf("Pearson r = %.3f (p = %.4f)\n", r_pearson, test$p.value))
  cat(sprintf("Spearman r = %.3f\n", r_spearman))

  # El Niño vs La Niña 对比
  el_nino <- tc_freq[nino34 > 0.5]
  la_nina <- tc_freq[nino34 < -0.5]
  neutral <- tc_freq[nino34 >= -0.5 & nino34 <= 0.5]

  cat(sprintf("\nEl Niño 年均频数: %.1f (n=%d)\n", mean(el_nino), length(el_nino)))
  cat(sprintf("La Niña 年均频数: %.1f (n=%d)\n", mean(la_nina), length(la_nina)))
  cat(sprintf("中性年均频数: %.1f (n=%d)\n", mean(neutral), length(neutral)))

  return(list(r = r_pearson, p = test$p.value,
              el_nino_mean = mean(el_nina), la_nina_mean = mean(la_nina)))
}

# ============================================================
# 4. 趋势可视化
# ============================================================

plot_trend <- function(years, series, title = "TC Frequency Trend",
                       output = "trend_r.png") {
  """
  绘制趋势分析图（含线性趋势和5年滑动平均）
  """
  df <- data.frame(year = years, value = series)
  df$rolling <- stats::filter(df$value, filter = rep(1/5, 5), sides = 2)

  # 线性回归
  lm_fit <- lm(value ~ year, data = df)
  df$trend <- predict(lm_fit)

  p <- ggplot(df, aes(x = year, y = value)) +
    geom_col(fill = "steelblue", alpha = 0.5) +
    geom_line(aes(y = rolling), color = "red", linewidth = 1.2) +
    geom_line(aes(y = trend), color = "darkred", linewidth = 1, linetype = "dashed") +
    geom_hline(yintercept = mean(series), color = "gray50", linetype = "dotted") +
    labs(title = title,
         x = "Year", y = "Number of TCs") +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))

  ggsave(output, p, width = 12, height = 5, dpi = 150)
  cat(sprintf("趋势图已保存: %s\n", output))

  # 输出回归统计
  s <- summary(lm_fit)
  cat(sprintf("线性趋势: %.3f/年 (%.2f/十年), R² = %.3f, p = %.4f\n",
              s$coefficients[2, 1], s$coefficients[2, 1] * 10,
              s$r.squared, s$coefficients[2, 4]))

  return(lm_fit)
}

# ============================================================
# 5. 主函数
# ============================================================

main <- function() {
  cat("========================================\n")
  cat("  台风气候趋势分析 (R)\n")
  cat("========================================\n\n")

  # 示例数据（实际使用时替换为真实数据）
  # 读取 IBTrACS 年频数数据
  # years <- 1970:2023
  # tc_freq <- read.csv("annual_freq.csv")$count

  # 使用示例数据演示
  set.seed(42)
  years <- 1970:2023
  tc_freq <- round(20 + 0.1 * (years - 1970) + rnorm(length(years), 0, 5))
  nino34 <- rnorm(length(years), 0, 0.8)

  # 趋势检验
  mk_result <- mk_test(tc_freq)

  # 变点检验
  pettitt_result <- pettitt_test(tc_freq, years)

  # ENSO 相关
  enso_result <- enso_correlation(tc_freq, nino34, years)

  # 可视化
  plot_trend(years, tc_freq, "Western North Pacific TC Frequency Trend",
             "trend_r.png")

  cat("\n分析完成。\n")
}

# 执行
main()
