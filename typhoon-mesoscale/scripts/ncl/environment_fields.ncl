;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
; environment_fields.ncl
;
; 功能：绘制台风环境场诊断图（NCL版本）
;   - SST 空间分布
;   - 位势高度+风场叠加
;   - 多层切片
;
; 用法：ncl environment_fields.ncl
;   需要设置：era5_file（ERA5 NetCDF文件路径）
;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

begin

  ;--- 配置 ---
  era5_file = "era5_env.nc"
  storm_lat = 22.0
  storm_lon = 130.0
  out_file  = "env_ncl"

  ;--- 读取ERA5数据 ---
  f = addfile(era5_file, "r")

  ;--- 面板1: SST ---
  wks = gsn_open_wks("png", out_file)

  res_sst = True
  res_sst@cnFillOn        = True
  res_sst@cnFillPalette   = "BlueWhiteOrangeRed"
  res_sst@cnLevelSelectionMode = "ManualLevels"
  res_sst@cnMinLevelValF  = 20
  res_sst@cnMaxLevelValF  = 32
  res_sst@cnLevelSpacingF = 1.0
  res_sst@tiMainString    = "SST Distribution"
  res_sst@tiMainFontHeightF = 0.02
  res_sst@mpProjection    = "CylindricalEquidistant"
  res_sst@mpLimitMode    = "LatLon"
  res_sst@mpMinLatF       = storm_lat - 15
  res_sst@mpMaxLatF       = storm_lat + 15
  res_sst@mpMinLonF       = storm_lon - 15
  res_sst@mpMaxLonF       = storm_lon + 15
  res_sst@mpFillOn        = True

  sst = f->sst(0,:,:)
  plot_sst = gsn_csm_contour_map(wks, sst, res_sst)

  ; 标注台风中心
  mkres = True
  mkres@gsMarkerIndex    = 15
  mkres@gsMarkerSizeF    = 0.03
  mkres@gsMarkerColor    = "black"
  gsn_add_polymarker(wks, plot_sst, (/storm_lon/), (/storm_lat/), mkres)

  ; 26.5°C 等值线
  res_line = True
  res_line@cnLineLabelInterval = 1
  res_line@cnInfoLabelOn       = False

  ;--- 面板2: 850hPa 风场+涡度 ---
  res_850 = True
  res_850@mpProjection     = "CylindricalEquidistant"
  res_850@mpLimitMode      = "LatLon"
  res_850@mpMinLatF        = storm_lat - 15
  res_850@mpMaxLatF        = storm_lat + 15
  res_850@mpMinLonF        = storm_lon - 15
  res_850@mpMaxLonF        = storm_lon + 15
  res_850@tiMainString     = "850 hPa Wind + Vorticity"
  res_850@tiMainFontHeightF = 0.02

  ; 风矢量
  u850 = f->u(0,{850},:,:)
  v850 = f->v(0,{850},:,:)

  plot_850 = gsn_csm_vector_map(wks, u850, v850, res_850)

  ;--- 面板3: 200hPa 风场（高空辐散） ---
  res_200 = True
  res_200@mpProjection     = "CylindricalEquidistant"
  res_200@mpLimitMode      = "LatLon"
  res_200@mpMinLatF        = storm_lat - 15
  res_200@mpMaxLatF        = storm_lat + 15
  res_200@mpMinLonF        = storm_lon - 15
  res_200@mpMaxLonF        = storm_lon + 15
  res_200@tiMainString     = "200 hPa Wind (Upper-level Divergence)"
  res_200@tiMainFontHeightF = 0.02

  u200 = f->u(0,{200},:,:)
  v200 = f->v(0,{200},:,:)

  plot_200 = gsn_csm_vector_map(wks, u200, v200, res_200)

  ;--- 面板4: 700hPa 相对湿度 ---
  res_rh = True
  res_rh@cnFillOn         = True
  res_rh@cnFillPalette    = "WhiteBlueGreenYellowRed"
  res_rh@cnLevelSelectionMode = "ManualLevels"
  res_rh@cnMinLevelValF   = 20
  res_rh@cnMaxLevelValF   = 100
  res_rh@cnLevelSpacingF  = 10
  res_rh@mpProjection     = "CylindricalEquidistant"
  res_rh@mpLimitMode      = "LatLon"
  res_rh@mpMinLatF        = storm_lat - 15
  res_rh@mpMaxLatF        = storm_lat + 15
  res_rh@mpMinLonF        = storm_lon - 15
  res_rh@mpMaxLonF        = storm_lon + 15
  res_rh@tiMainString     = "700 hPa Relative Humidity"
  res_rh@tiMainFontHeightF = 0.02

  rh700 = f->r(0,{700},:,:)
  plot_rh = gsn_csm_contour_map(wks, rh700, res_rh)

  ;--- 四面板组合输出 ---
  plots = new(4, graphic)
  plots(0) = plot_sst
  plots(1) = plot_850
  plots(2) = plot_200
  plots(3) = plot_rh

  pres = True
  pres@gsnFrame           = False
  pres@gsnPanelYWhiteSpacePercent = 3.0
  pres@gsnPanelXWhiteSpacePercent = 3.0
  pres@txString           = "Typhoon Environment Diagnosis"
  pres@txFontHeightF     = 0.02

  gsn_panel(wks, plots, (/2, 2/), pres)

  print("环境场诊断图已保存: " + out_file + ".png")

end
