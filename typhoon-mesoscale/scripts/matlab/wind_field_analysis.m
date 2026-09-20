%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% wind_field_analysis.m
%
% 功能：台风风场结构与轴对称分解（MATLAB版本）
%   - Holland (1980) 梯度风模型重建风场
%   - 风场极坐标转换
%   - 轴对称与非对称分量分解
%   - 风场可视化
%
% 用法：直接运行，修改参数后执行
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear; clc; close all;

%% ========== 参数设置 ==========
pmin = 935;       % 中心最低气压 (hPa)
pn   = 1010;      % 环境气压 (hPa)
vmax = 65;        % 最大风速 (m/s)
rmax = 25;        % 最大风速半径 (km)
lat0 = 22.0;      % 台风中心纬度

%% ========== Holland (1980) 梯度风模型 ==========

r = 5:5:500;      % 半径数组 (km)
rho = 1.15;       % 空气密度 (kg/m^3)
f = 2 * 7.292e-5 * sin(deg2rad(abs(lat0)));  % 科氏参数

% Holland B 参数 (Willoughby & Rahn 2004)
B = (vmax^2 * rho * exp(1)) / (100 * (pn - pmin));
B = max(1.0, min(2.5, B));

% 梯度风方程
r_m = r * 1000;       % 转为 m
rmax_m = rmax * 1000;
dp_Pa = (pn - pmin) * 100;  % 转为 Pa

term1 = (B / rho) * (rmax_m ./ r_m).^B * dp_Pa .* ...
        exp(-(rmax_m ./ r_m).^B);
term2 = (r_m * f / 2).^2;
vg = sqrt(term1 + term2) - r_m * f / 2;

fprintf('Holland B 参数: %.2f\n', B);
fprintf('最大风速半径(RMW): %.0f km\n', r(find(vg == max(vg), 1)));

%% ========== 极坐标风场 ==========

daz = 5;
az = 0:daz:360-daz;
[R, AZ] = meshgrid(r, az);

% 添加移动方向非对称（简化：假设台风向北移动，移速5 m/s）
ts_speed = 5;  % m/s
move_dir = 0;  % 度 (0=北)

% 移动方向右侧风增强（北半球）
az_rad = deg2rad(az);
move_az_rad = deg2rad(move_dir);
% 移动速度在切向方向的投影
ts_tangential = ts_speed * cos(az_rad - move_az_rad);

wind_field = repmat(vg', 1, length(az)) + repmat(ts_tangential, size(R,1), 1);

%% ========== 傅里叶分解 ==========

% 方位角方向的傅里叶分解
fft_coeffs = fft(wind_field, [], 2);
n_az = length(az);

symmetric = real(fft_coeffs(:, 1)) / n_az;  % 波数0（轴对称）
wave1_amp = abs(fft_coeffs(:, 2)) / n_az * 2; % 波数1振幅
wave1_dir = mod(rad2deg(angle(fft_coeffs(:, 2))), 360); % 波数1方向
wave2_amp = abs(fft_coeffs(:, 3)) / n_az * 2; % 波数2振幅

fprintf('\n非对称性分析:\n');
fprintf('  波数0(轴对称): %.1f m/s\n', max(symmetric));
fprintf('  波数1振幅: %.1f m/s, 方向: %.0f°\n', max(wave1_amp), wave1_dir(find(wave1_amp == max(wave1_amp), 1)));
fprintf('  波数2振幅: %.1f m/s\n', max(wave2_amp));

%% ========== 绘图 ==========

figure('Position', [100 100 1600 700]);

% --- 面板1: 极坐标风场 ---
subplot(1, 2, 1);
[TH, RR] = pol2cart(deg2rad(az), R);
TH_display = deg2rad(90 - az);  % 转为数学坐标（北=上）
[X, Y] = pol2cart(TH_display, RR);
contourf(X, Y, wind_field', 20, 'LineColor', 'none');
colormap jet;
colorbar;
axis equal;
title('Wind Field (Polar)', 'FontSize', 12, 'FontWeight', 'bold');
xlabel('X (km)');
ylabel('Y (km)');
set(gca, 'FontSize', 10);

% --- 面板2: 方位角平均廓线 ---
subplot(1, 2, 2);
plot(r, vg, 'b-', 'LineWidth', 2);
hold on;
plot(r, symmetric, 'g--', 'LineWidth', 1.5);
rmax_idx = find(vg == max(vg), 1);
xline(r(rmax_idx), 'r--', 'LineWidth', 1.5);
text(r(rmax_idx), max(vg)+1, sprintf('RMW = %.0f km', r(rmax_idx)), ...
    'Color', 'r', 'FontSize', 10);
xlabel('Radius (km)', 'FontSize', 12);
ylabel('Wind Speed (m/s)', 'FontSize', 12);
title('Azimuthal Mean Wind Profile', 'FontSize', 12, 'FontWeight', 'bold');
legend('Total', 'Symmetric (k=0)', 'Location', 'northeast');
grid on;
set(gca, 'FontSize', 10);

% 全局标题
sgtitle('Typhoon Wind Field Reconstruction (Holland Model)', ...
    'FontSize', 14, 'FontWeight', 'bold');

% 保存图片
saveas(gcf, 'wind_field_matlab.png');
fprintf('\n风场图已保存: wind_field_matlab.png\n');

%% ========== 波数分量可视化（额外面板） ==========

figure('Position', [100 100 1200 400]);

% 重建各波数分量
subplot(1, 3, 1);
w0 = real(fft_coeffs(:, 1)) / n_az;
plot(r, w0, 'g-', 'LineWidth', 2);
xlabel('Radius (km)');
ylabel('Wind Speed (m/s)');
title('Wavenumber 0 (Symmetric)');
grid on;

subplot(1, 3, 2);
w1 = real(ifft(fft_coeffs .* [zeros(size(fft_coeffs,1),1), ...
    [1, zeros(1, n_az-1)] + [1, zeros(1, n_az-1)], ...
    zeros(size(fft_coeffs,1), n_az-2)], n_az, 2));
% 简化：直接画波数1振幅
plot(r, wave1_amp, 'r-', 'LineWidth', 2);
xlabel('Radius (km)');
ylabel('Amplitude (m/s)');
title('Wavenumber 1 Amplitude');
grid on;

subplot(1, 3, 3);
plot(r, wave2_amp, 'b-', 'LineWidth', 2);
xlabel('Radius (km)');
ylabel('Amplitude (m/s)');
title('Wavenumber 2 Amplitude');
grid on;

sgtitle('Fourier Decomposition of Wind Field', ...
    'FontSize', 14, 'FontWeight', 'bold');

saveas(gcf, 'wind_decomposition_matlab.png');
fprintf('波数分解图已保存: wind_decomposition_matlab.png\n');
