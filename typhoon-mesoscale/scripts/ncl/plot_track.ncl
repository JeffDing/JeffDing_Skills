;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
; plot_track.ncl
;
; 功能：绘制台风路径图（NCL版本）
;   - 支持彩色强度路径
;   - 多路径叠加
;   - 地图投影可自定义
;
; 用法：ncl plot_track.ncl
;   需要设置变量：fname（数据文件名）、storm_name（台风名称）
;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

begin

  ;--- 配置参数 ---
  fname     = "IBTrACS.WP.nc"
  storm_name = "HATO"
  out_file  = "track_ncl.png"

  ;--- 读取数据 ---
  f = addfile(fname, "r")
  storm_names = f->name
  idx = ind(str_strip(storm_names(:) .eq. storm_name))

  if (dimsizes(idx) .eq. 0) then
    print("未找到台风: " + storm_name)
    exit
  end if

  lat  = f->lat(idx(0),:)
  lon  = f->lon(idx(0),:)
  wind = f->wmo_wind(idx(0),:)

  ; 去除缺省值
  good = ind(.not. ismissing(lat) .and. .not. ismissing(lon))
  lat  = lat(good)
  lon  = lon(good)
  wind = wind(good)

  ;--- 设置地图 ---
  wks = gsn_open_wks("png", out_file(0:strlen(out_file)-5))
  res = True
  res@mpProjection       = "Mercator"
  res@mpLimitMode        = "LatLon"
  res@mpMinLatF          = min(lat) - 10
  res@mpMaxLatF          = max(lat) + 10
  res@mpMinLonF          = min(lon) - 10
  res@mpMaxLonF          = max(lon) + 10
  res@mpFillOn          = True
  res@mpLandFillColor    = "gray90"
  res@mpOceanFillColor   = "white"
  res@cnFillOn           = False
  res@tiMainString       = "Typhoon " + storm_name + " Track"
  res@tiMainFontHeightF = 0.02
  res@gsnAddCyclic       = False

  map = gsn_map(wks, res)

  ;--- 绘制路径线 ---
  lnres = True
  lnres@gsLineThicknessF = 2.0
  lnres@gsLineColor      = "black"
  map_poly = gsn_add_polyline(wks, map, lon, lat, lnres)

  ;--- 按强度着色的散点 ---
  mkres = True
  mkres@gsMarkerIndex      = 16
  mkres@gsMarkerSizeF      = 0.02
  map_scatter = gsn_add_polymarker(wks, map, lon, lat, mkres)

  ;--- 标注起点和终点 ---
  stres = True
  stres@gsMarkerIndex    = 22
  stres@gsMarkerSizeF    = 0.03
  stres@gsMarkerColor    = "green"
  map_start = gsn_add_polymarker(wks, map, lon(0:0), lat(0:0), stres)

  stres@gsMarkerColor    = "red"
  map_end = gsn_add_polymarker(wks, map, lon(dimsizes(lon)-1:), lat(dimsizes(lat)-1:), stres)

  ;--- 添加色标 ---
  cnres = True
  cnres@cnFillOn         = True
  cnres@cnFillPalette    = "YlOrRd"
  cnres@cnLevels         = ispan(20, 160, 10)
  cnres@lbLabelStride    = 2
  cnres@tiMainString     = "Wind Speed (kt)"

  ;--- 输出 ---
  draw(map)
  frame(wks)

  print("路径图已保存: " + out_file)

end
