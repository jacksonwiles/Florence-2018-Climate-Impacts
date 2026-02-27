load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRF_contributed.ncl"
begin
  ;; read data
  ;; systemfunc: Executes a shell command and returns the output.
  ;; Retrieve a list of files from one directory
  wrfout = systemfunc("ls ../../wrfout_d03_2018-09-14_00:00:00*")  
  filnum = dimsizes(wrfout) 
  data   = addfiles(wrfout, "r") 
  wrflat = data[0]->XLAT    
  wrflon = data[0]->XLONG
  dims   = dimsizes(wrflat)
  ;; get the dimension size of wrf
  nt     = dims(0)
  nlat   = dims(1)
  nlon   = dims(2)

  res=True
  res@gsnDraw=False               ;-- don't draw plot yet
  res@gsnFrame=False              ;-- don't advance frame
  res@gsnMaximize=True            ;-- don't maximized the workstation
  res@gsnLeftString=""
  res@gsnRightString=""
  res@gsnScalarContour=True


  res@pmTickMarkDisplayMode="Conditional"         ;-- displays TickMark object

  res@tfDoNDCOverlay = True

  res@tmXTOn=False    ;-- turns off top tick marks
  res@tmYROn=False    ;-- turns off right tick marks


  res@cnInfoLabelOn  = False               ;-- not draw an informational label
  res@cnLineLabelBackgroundColor = "Transparent"       ;-- draw lines background color
  res@cnLineThicknessF = 3                 ;-- thickness for all contour lines
  res@cnLineLabelPlacementMode = "constant"   ;-- draws line labels as an integral part of the line dash pattern
  res@cnLineLabelInterval  = 1   ;-- set label intervals on contours
  res@cnLineLabelDensityF  = 2   ;-- set number of labels along a contour line

  resp = res



  res@mpOutlineBoundarySets       = "GeophysicalAndUSStates"
  res@mpOutlineOn                 = True  ;-- outline land (default: False)
  res@mpGeophysicalLineThicknessF = 6
  res@mpNationalLineThicknessF    = 6
  res@mpUSStateLineThicknessF     = 6
  res@mpFillOn                    = False ;-- no map fill
;  res@mpProjection           = "LambertConformal"  ;
;  res@mpLambertParallel1F    = 43.427
;  res@mpLambertParallel2F    = 43.427
;  res@mpLambertMeridianF     = -112.185
  res@mpUSStateLineColor     = "black"
  res@mpNationalLineColor    = "black"
  res@mpLimitMode            = "Corners"
  res@mpLeftCornerLatF = wrflat(0,5,5)              ;-- min latitude
  res@mpLeftCornerLonF = wrflon(0,5,5)              ;-- min longitude
  res@mpRightCornerLatF = wrflat(0,nlat-5,nlon-5)   ;-- max latitude
  res@mpRightCornerLonF = wrflon(0,nlat-5,nlon-5)   ;-- max longitude

  res@lbLabelBarOn     = True
  res@lbLabelFontHeightF = 0.015
  res@lbTitlePosition = "bottom"
  res@lbTitleFontHeightF = 0.02
  res@lbTitleOffsetF = 0.0
  res@lbTitleString = ""

  res@vcRefMagnitudeF = 10.0
  res@vcRefLengthF = 0.025
  res@vcLineArrowColor = "black"
  res@vcMinDistanceF = 0.025
  res@vcRefAnnoOrthogonalPosF = -0.168
  res@vcRefAnnoFontHeightF = 0.01
  res@vcGlyphStyle            = "WindBarb"         ; select wind barbs 

  resp@cnLevelSelectionMode =  "ManualLevels" ;slp countours
  resp@cnMinLevelValF       = 910.
  resp@cnMaxLevelValF       = 1050.
  resp@cnLevelSpacingF      = 2.
  resp@cnFillOn             = False
  resp@cnLinesOn            = True           ;-- draw contour lines

  do i = 0, filnum-1
    slp   = wrf_user_getvar(data[i], "slp", -1)   ;-- get variable : Sea level pressure [hPa]
    wrf_smooth_2d(slp,10)
    u = wrf_user_getvar(data[i], "U10", -1)
;    u = u*2.23694
    v = wrf_user_getvar(data[i], "V10", -1)
;    v = v*2.23694
   Time  = wrf_user_getvar(data[i], "times", -1) ;-- get variable : Times in file (return strings)

     min_slp = min(slp)
     print(min_slp)


;  slp@t2 = t2

   do j = 0, dimsizes(Time)-1

    print(Time(j))
type = "png"
type@wkWidth = 3000
type@wkHeight = 3000

;    wks=gsn_open_wks("x11", "slp_temp_wind"+Time(j)) 
    wks=gsn_open_wks(type, "slp_wind_barb_D03"+Time(j)) 
    res@gsnLeftString  = "SLP(hPa) & Min SLP=" + min_slp + "~C~Wind(m/s) "
    res@gsnRightString  = Time(j)
    plot1 = gsn_csm_vector_map(wks,u(j,5:nlat-5,5:nlon-5),v(j,5:nlat-5,5:nlon-5),res)
    plot2 = gsn_csm_contour(wks,slp(j,5:nlat-5,5:nlon-5),resp)    
    overlay(plot1,plot2)
draw(plot1)
    frame(wks)
   end do
    delete(slp)
    delete(Time)
    delete(plot1)
    delete(u)
    delete(v)
    delete(plot2)


  end do

end



