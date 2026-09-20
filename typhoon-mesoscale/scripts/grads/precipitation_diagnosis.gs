'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
' precipitation_diagnosis.gs
'
' 功能：台风降水诊断分析（GrADS版本）
'   - 降水空间分布
'   - Hovmöller 图（半径-时间）
'   - 面积平均降水时间序列
'
' 用法：在GrADS中运行
'   ga-> open precipitation_diagnosis.gs
'   需要先打开 GPM IMERG 数据文件
'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

'=== 面板1: 降水空间分布 ===

'cc'
'set lat 10 35'
'set lon 110 140'
'set mpdset hires'

' 设置降水色标
'set gxout shaded'
'set csmooth on'
'set clevs 0 5 10 25 50 100 200 300'
'set ccols 1 2 3 4 5 6 7 8 9'
'set black 0 0 0 0 0 0 0 0 0'

' 取当前时刻降水率
'set t 1'
'd precipRate'

' 叠加等值线
'set gxout contour'
'set ccolor 1'
'set cthick 3'
'd precipRate'

' 叠加台风中心标记
' 假设 center_lon 和 center_lat 是台风中心坐标
'set ccolor 1'
'set cmark 22'
'draw mark 22 center_lon center_lat 0.2'

'draw title Precipitation Distribution'

'printim precip_spatial.png x1200 y900'

'=== 面板2: 半径-时间 Hovmöller ===

'cc'
' 设置时间范围
'set t 1 48'  ' 48个时间步 (24小时，30分钟间隔)

' 计算方位角平均降水
' 需要将数据转换到极坐标
' 这里用简化的经度方向平均（近似方位角平均）

' 设置 Hovmöller 图
'set lon center_lon-5 center_lon+5'  ' 中心附近5度经度范围
'set lat 0 500'  ' 半径方向 (km，需要预处理)
'set gxout shaded'
'set clevs 0 1 5 10 20 30 50'
'set ccols 1 2 3 4 5 6 7 8'

' 计算方位角平均
'd aave(precipRate, lon=lon-5, lon=lon+5, lat=lat-5, lat=lat+5)'

'set gxout shaded'
'd precipRate'

'draw title Radius-Time Hovmoller'

'printim hovmoller_r.png x1200 y600'

'=== 面板3: 面积平均降水时间序列 ===

'cc'
'set t 1 48'
'set gxout line'
'set ccolor 4'
'set cthick 5'

' 台风影响区域平均降水率
'set lon center_lon-10 center_lon+10'
'set lat center_lat-10 center_lat+10'
'd aave(precipRate, lon=center_lon-10, lon=center_lon+10, lat=center_lat-10, lat_lat+10)'

' 叠加最大降水
'set ccolor 2'
'set cthick 3'
'd amax(precipRate, lon=center_lon-10, lon=center_lon+10, lat=center_lat-10, lat_lat+10)'

'set strsiz 0.15 0.18'
'draw title Area-Averaged Precipitation Time Series'
'draw ylab Precipitation (mm/hr)'
'draw xlab Time (30-min intervals)'

'printim precip_timeseries.png x1200 y600'

'quit'
