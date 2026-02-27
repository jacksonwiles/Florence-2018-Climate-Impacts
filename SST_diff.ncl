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
  wrfout = systemfunc("ls ../../../../../../../../CTRL_Excellent/wrfout_d01_2018-09-14_00:00:00") ;../../../../../../../../../TEST_4_CTRL_3domains/wrfout_d01_2018-09-1*")  
  filnum = dimsizes(wrfout) 
  data   = addfiles(wrfout, "r") 
  wrflat = data[0]->XLAT    
  wrflon = data[0]->XLONG
  dims   = dimsizes(wrflat)
  ;; get the dimension size of wrf
  nt     = dims(0)
  nlat   = dims(1)
  nlon   = dims(2)

  wrfout_climate = systemfunc("ls ../../../../../wrfout_d01_2018-09-14_00:00:00")
  filnum_climate = dimsizes(wrfout_climate)
  data_climate   = addfiles(wrfout_climate, "r")



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
  res@mpProjection           = "mercator"  ;
;  res@mpLambertParallel1F    = 36.101
;  res@mpLambertParallel2F    = 36.101
;  res@mpLambertMeridianF     = -80.711
  res@mpUSStateLineColor     = "black"
  res@mpNationalLineColor    = "black"
  res@mpLimitMode            = "Corners"
  res@mpLeftCornerLatF = wrflat(0,5,5)              ;-- min latitude
  res@mpLeftCornerLonF = wrflon(0,5,5)              ;-- min longitude
  res@mpRightCornerLatF = wrflat(0,nlat-5,nlon-5)   ;-- max latitude
  res@mpRightCornerLonF = wrflon(0,nlat-5,nlon-5)   ;-- max longitude
;  res@mpOutlineBoundarySets  = "AllBoundaries"


  res@lbLabelBarOn     = True
  res@lbLabelFontHeightF = 0.015
  res@lbTitlePosition = "bottom"
  res@lbTitleFontHeightF = 0.02
  res@lbTitleOffsetF = 0.0
  res@lbTitleString = ""

;  res@vcRefMagnitudeF = 15.0
;  res@vcRefLengthF = 0.05
;  res@vcLineArrowColor = "black"
;  res@vcMinDistanceF = 0.020
;  res@vcRefAnnoOrthogonalPosF = -0.1
;  res@vcRefAnnoFontHeightF = 0.01



  res@cnLevelSelectionMode = "ManualLevels" ;temp. contours
  res@cnMinLevelValF       = -4.
  res@cnMaxLevelValF       = 4.
  res@cnLevelSpacingF      = 0.5
  res@cnFillPalette        = "cmocean_balance" ;MPL_seismic" ;"matlab_jet"
  res@cnSpanFillPalette    = True
  res@cnFillOn              = True
  res@cnLinesOn             = False
  res@cnLineLabelsOn        = False
  res@cnInfoLabelOn         = False
  res@cnMissingValFillColor = "white"


;  resp@cnLevelSelectionMode =  "ManualLevels" ;slp countours
;  resp@cnMinLevelValF       = 950.
;  resp@cnMaxLevelValF       = 1050.
;  resp@cnLevelSpacingF      = 1.
;  resp@cnFillOn             = False
;  resp@cnLinesOn            = True           ;-- draw contour lines

  do i = 0, filnum-1

    sst_climate = wrf_user_getvar(data_climate[i], "SST", -1)

    sst    = wrf_user_getvar(data[i], "SST", -1) 
      
    sst_diff = sst_climate  - sst
 



    oro   = wrf_user_getvar(data[i], "HGT", -1)

ocean_only = sst_diff

 ocean_only = mask(sst_diff,oro,False)


  Time  = wrf_user_getvar(data[i], "times", -1) ;-- get variable : Times in file (return strings)

;  slp@t2 = t2

   do j = 0, dimsizes(Time)-1

    print(Time(j))

type = "png"
type@wkWidth = 3000
type@wkHeight = 3000


;    wks=gsn_open_wks("x11", "slp_temp_wind"+Time(j)) 
    wks=gsn_open_wks(type, "SST_diff") ;+Time(j)) 
    res@gsnLeftString  = "SST Diff. WRF-RCP8.5_2068 - CTRL"
    res@gsnRightString  = ""  ;Time(j)
    plot1 = gsn_csm_contour_map(wks,ocean_only(j,5:nlat-5,5:nlon-5),res)
;    plot1 = gsn_csm_vector_scalar_map(wks,u(j,5:nlat-5,5:nlon-5),v(j,5:nlat-5,5:nlon-5),tf2(j,5:nlat-5,5:nlon-5),res)
;    plot2 = gsn_csm_contour(wks,slp(j,5:nlat-5,5:nlon-5),resp)    
;    overlay(plot1,plot2)
draw(plot1)
    frame(wks)
   end do
;    delete(slp)
;    delete(Time)
;    delete(plot1)
;    delete(t2)
;    delete(t2_climate)
;    delete(t2_diff)
;    delete(u)
;    delete(v)
;    delete(plot2)


  end do

end
