'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
' track_overlay.gs
'
' 功能：在再分析场上叠加台风路径（GrADS版本）
'   - 路径叠加在位势高度+风场上
'   - 按强度着色路径点
'
' 用法：在GrADS中运行
'   ga-> open track_overlay.gs
'   需要先打开 ERA5 数据文件 (era5.ctl)
'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

' 设置图形输出
'set display off'
'set grads off'
'set vpage 0 11 0 8.5'
'set page off'
'set display on'

'cc'
'set gxout shaded'
'set csmooth on'

' 设置地图投影和范围
'set lat 5 45'
'set lon 100 160'
'set mpdset hires'
'set map_scaled on'

' 绘制 850hPa 位势高度填色
'set lev 850'
'set t 1'
'set gxout shaded'
'set clevs 1400 1420 1440 1460 1480 1500 1520 1540 1560'
'set ccols 1 2 3 4 5 6 7 8 9 10'
'd z'

' 叠加等值线
'set gxout contour'
'set ccolor 0'
'set cthick 5'
'd z'

' 绘制风矢量
'set gxout vector'
'set ccolor 4'
'set cint 200'
'd u;v'

' 叠加台风路径
' 注意：路径数据需要先转换为GrADS可读格式
' 这里假设有一个路径数据文件 track.dat
' 格式: lat lon wind(kt)

' 绘制路径线
'set gxout line'
'set line 1 1 3'
'd track_lat;track_lon'

' 绘制路径点（按强度着色）
' 需要分段绘制不同强度的路径段
' TD (wind < 34)
'set line 2 1 6'
'd maskout(track_lat, (track_wind.lt.34));track_lon'

' TS (34 <= wind < 64)
'set line 3 1 6'
'd maskout(track_lat, (track_wind.ge.34).and.(track_wind.lt.64));track_lon'

' TY (wind >= 64)
'set line 4 1 6'
'd maskout(track_lat, (track_wind.ge.64));track_lon'

' 标注起点
'set mark 22 0.15'
'set ccolor 3'
'draw mark 22 track_lon(1) track_lat(1) 0.15'

' 标注终点
'set ccolor 2'
'draw mark 22 track_lon(last) track_lat(last) 0.15'

' 添加标题
'draw title Typhoon Track Overlay on 850hPa Analysis'

' 添加色标
'run cbar

' 输出图片
'printim track_overlay.png x1200 y900'

'quit'
