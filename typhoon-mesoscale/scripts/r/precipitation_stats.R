#############################################################################
# precipitation_stats.R
#
# 功能：台风降水极值统计分析（R语言版本）
#   - 年最大值序列(AMS)构建
#   - GEV 分布拟合
#   - GPD 超阈值法拟合
#   - 重现期计算与可视化
#   - 降水阈值超越频率分析
#
# 依赖：extRemes, ggplot2, ismev
# 安装：install.packages(c("extRemes", "ggplot2", "ismev"))
#############################################################################

library(extRemes)
library(ggplot2)
library(ismev)

# ============================================================
# 1. 年最大值序列(AMS)构建
# ============================================================

build_ams <- function(daily_precip, dates) {
  """
  从日降水序列构建年最大值序列

  参数：
    daily_precip: 日降水向量
    dates: 对应日期向量

  返回：data.frame(year, max_precip)
  """
  df <- data.frame(date = as.Date(dates), precip = daily_precip)
  df$year <- format(df$date, "%Y")

  ams <- aggregate(precip ~ year, data = df, FUN = max)
  names(ams) <- c("year", "max_precip")
  ams$year <- as.numeric(ams$year)

  cat(sprintf("AMS 构建: %d 年 (%d-%d)\n", nrow(ams),
              min(ams$year), max(ams$year)))
  cat(sprintf("最大值: %.1f mm, 均值: %.1f mm, 中位数: %.1f mm\n",
              max(ams$max_precip), mean(ams$max_precip), median(ams$max_precip)))

  return(ams)
}

# ============================================================
# 2. GEV 分布拟合
# ============================================================

fit_gev <- function(ams) {
  """
  拟合广义极值(GEV)分布

  参数：
    ams: 年最大值序列

  返回：fit 对象和参数估计
  """
  fit <- fevd(ams$max_precip, type = "GEV", method = "MLE")

  cat("\n=== GEV 分布拟合 ===\n")
  print(fit)

  # 参数
  loc <- fit$results$par["location"]
  scale <- fit$results$par["scale"]
  shape <- fit$results$par["shape"]

  cat(sprintf("\n参数估计:\n"))
  cat(sprintf("  位置(loc): %.2f\n", loc))
  cat(sprintf("  尺度(scale): %.2f\n", scale))
  cat(sprintf("  形状(shape): %.4f (%s)\n", shape,
              ifelse(shape < 0, "Weibull型(有上界)",
              ifelse(shape > 0, "Frechet型(重尾)", "Gumbel型"))))

  return(fit)
}

# ============================================================
# 3. GPD 超阈值拟合
# ============================================================

fit_gpd <- function(precip_series, threshold_quantile = 0.95) {
  """
  超阈值法(POT)拟合广义帕累托(GPD)分布

  参数：
    precip_series: 降水序列
    threshold_quantile: 阈值分位数
  """
  threshold <- quantile(precip_series, threshold_quantile, na.rm = TRUE)
  exceedances <- precip_series[precip_series > threshold] - threshold

  fit <- fevd(exceedances, threshold = 0, type = "GP", method = "MLE")

  cat("\n=== GPD 拟合 ===\n")
  cat(sprintf("阈值: %.1f mm (第%.0f百分位)\n", threshold, threshold_quantile * 100))
  cat(sprintf("超阈值次数: %d\n", length(exceedances)))
  print(fit)

  return(list(fit = fit, threshold = threshold))
}

# ============================================================
# 4. 重现期计算
# ============================================================

calc_return_periods <- function(gev_fit, periods = c(10, 20, 50, 100, 200)) {
  """
  基于 GEV 拟合计算重现期降水

  参数：
    gev_fit: fevd 拟合对象
    periods: 重现期向量

  返回：data.frame(return_period, return_level, lower, upper)
  """
  levels <- sapply(periods, function(rp) {
    rl <- return.level(gev_fit, return.period = rp, do.ci = TRUE)
    return(rl)
  })

  result <- data.frame(
    return_period = periods,
    return_level = levels["rl", ],
    lower = levels["lower", ],
    upper = levels["upper", ]
  )

  cat("\n=== 重现期降水 ===\n")
  cat(sprintf("%-15s %-15s %-15s %-15s\n", "重现期(年)", "重现水平(mm)",
              "下界(mm)", "上界(mm)"))
  for (i in 1:nrow(result)) {
    cat(sprintf("%-15d %-15.1f %-15.1f %-15.1f\n",
                result$return_period[i], result$return_level[i],
                result$lower[i], result$upper[i]))
  }

  return(result)
}

# ============================================================
# 5. 可视化
# ============================================================

plot_return_levels <- function(gev_fit, ams, output = "return_levels_r.png") {
  """
  绘制重现期-降水关系图
  """
  # 用 extRemes 的内置函数
  png(output, width = 1200, height = 800, res = 150)
  plot(gev_fit, type = "rl")
  dev.off()
  cat(sprintf("重现期图已保存: %s\n", output))
}

plot_ams_histogram <- function(ams, gev_fit, output = "ams_hist_r.png") {
  """
  绘制 AMS 直方图 + GEV 拟合曲线
  """
  df <- data.frame(x = ams$max_precip)

  p <- ggplot(df, aes(x = x)) +
    geom_histogram(aes(y = ..density..), bins = 15,
                   fill = "steelblue", alpha = 0.6, color = "black") +
    stat_function(fun = dgev,
                 args = list(loc = gev_fit$results$par["location"],
                             scale = gev_fit$results$par["scale"],
                             shape = gev_fit$results$par["shape"]),
                 color = "red", linewidth = 1.2) +
    labs(title = "Annual Maximum Precipitation Distribution",
         subtitle = "Histogram with GEV Fit",
         x = "Annual Max Precipitation (mm)",
         y = "Density") +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))

  ggsave(output, p, width = 10, height = 6, dpi = 150)
  cat(sprintf("AMS 直方图已保存: %s\n", output))
}

# ============================================================
# 6. 主函数
# ============================================================

main <- function() {
  cat("========================================\n")
  cat("  台风降水极值统计分析 (R)\n")
  cat("========================================\n\n")

  # 示例数据（实际使用时替换为真实数据）
  set.seed(42)
  dates <- seq(as.Date("1980-01-01"), as.Date("2023-12-31"), by = "day")
  daily_precip <- rgamma(length(dates), shape = 0.5, rate = 0.02)
  # 加入台风极端事件
  typhoon_days <- sample(1:length(dates), 200)
  daily_precip[typhoon_days] <- daily_precip[typhoon_days] +
    rgamma(200, shape = 2, rate = 0.01)

  # 构建 AMS
  ams <- build_ams(daily_precip, dates)

  # GEV 拟合
  gev_fit <- fit_gev(ams)

  # GPD 拟合
  gpd_result <- fit_gpd(daily_precip)

  # 重现期计算
  rp_result <- calc_return_periods(gev_fit)

  # 可视化
  plot_return_levels(gev_fit, ams, "return_levels_r.png")
  plot_ams_histogram(ams, gev_fit, "ams_hist_r.png")

  cat("\n分析完成。\n")
}

# 执行
main()
