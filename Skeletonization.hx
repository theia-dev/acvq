#####################
# change the path to the config tcl here (if not using mkconfig.py)
# provide the pathname without spaces between the curly brackets ('{}')
source [file normalize {path\to\config.tcl}]
#####################

set dim_list [list x_voxel y_voxel z_voxel x_dim y_dim z_dim]
set dim_dict [dict create  x_voxel 0 y_voxel 1 z_voxel 2 x_dim 3 y_dim 4 z_dim 5]
set itemlist [
    concat [
        glob -nocomplain -directory $BinInDir -types hidden *] [
        glob -nocomplain -directory $BinInDir *.tiff]
		]

if {[string trim $BinInID] != ""} {
  set itemlist [lsearch -regexp -all -inline $itemlist .*$BinInID.*]
    }

foreach len $len_list {
  # Make a new output folder per len of ends choice
	set new_dir  [concat $MV3DOutDir/len_$len/]
	if { [file exists $new_dir] == 0} {
		file mkdir $new_dir}
  }
foreach entry $itemlist {
  set output [file tail $entry]
  set output [split $output "/."]
  set outname [lindex $output 0]

  if {[info exists voxel_dir] == 1} {
  set voxel_file [open $voxel_dir]
  set voxel_data [read $voxel_file]
  set measure_dict [dict create]
  close $voxel_file
  foreach row [split [string trim $voxel_data] \n] {
      set row [lassign [split $row ,] key]
      dict set measure_dict [string trim $key] [concat {*}$row]
      set basename [split [string map [list $outname \uffff] $key] \uffff]
  }
  set temp [dict get $measure_dict $basename]
  foreach entr $dim_list {
  	if {[expr $$entr] eq "na"} {
  	set temp_ind [dict get $dim_dict $entr]
  	set $entr [lindex $temp $temp_ind]

  	}
  }

  foreach point [list x_voxel y_voxel z_voxel] {
  	set $point [format "%.2f" [expr $$point]]
  	}
  foreach point [list x_dim y_dim z_dim] {
  	set $point [format "%.0f" [expr $$point]]
  	}
  }
  set islandvoxel [expr $islandsize/($x_voxel*$y_voxel*$z_voxel)]
  set $islandvoxel [format "%.0f" [expr $islandvoxel]]

	remove -all
	set hideNewModules 0

  set input [load -tif +mode 100 +box 0 [expr ($x_dim-1)*$x_voxel] 0 [expr ($y_dim-1)*$y_voxel] 0 [expr ($z_dim-1)*$z_voxel] $entry ]

  set mt [create HxLabelVoxel "Multi-Thresholding"]
  $mt data connect $input
  $mt fire
  $mt boundary01 setValue 0
  $mt options setValue 0 1
  # ToDo: potentially remove
  $mt fire
  set mt_result [$mt create result]

  create HxGiEditor
  gi attach $mt_result
  gi removeIslands $islandvoxel 1 0.25

  set chamfer [create dist557 "Chamfer Distance Map"]
  $chamfer	interpretation setValue $chamferInterpret
  $chamfer inputImage connect $mt_result
  $chamfer fire
  $chamfer doIt hit
  $chamfer fire
  set dm [$chamfer getResult]

  foreach len $len_list {
    set new_dir [concat $MV3DOutDir/len_$len]
    set outfile [concat $new_dir/$outname.mv3D]
    if { [file exists $outfile] == 0} {
    if {[info exists thinner] == 1} {
    remove $thinner }
    if {[info exists thin_result] == 1} {
    remove $thin_result }
    set thinner [create HxExtThinner "Thinner"]
    $thinner data connect $mt_result
    $thinner distmap connect $dm
    $thinner fire
    $thinner extendedOptionsOnOff setValue 1
    $thinner fire
    $thinner lenOfEnds setValue 0 $len
    $thinner maxIterations setValue 0 0
    $thinner fire
    set thin_result [$thinner create result]

    set traceLines [create HxExtTraceLines]
    $traceLines data connect $thin_result
    $traceLines fire
    set traceResult [$traceLines create result]

    set smoothing [create HxSmoothLine ]
    $smoothing lineSet connect $traceResult
    $smoothing fire
    $smoothing coefficients setValue 0 $smooth_coeff
    $smoothing coefficients setValue 1 $smooth_adhere
    $smoothing numberOfIterations setValue 0 $smooth_iter
    $smoothing fire
    set smooth_result [$smoothing create result]

    set eval [create HxExtEvalOnLines]
    $eval data connect $smooth_result
    $eval field connect $dm
    $eval fire
    $eval doIt hit
    $eval fire

    set new_dir  [concat $MV3DOutDir/len_$len/]
    set outfile [concat $new_dir/$outname.mv3d]

    $smooth_result exportData "MicroVisu3D" $outfile
    if { [file exists $new_dir/$outname-skeletonization.hx] == 0} {
      saveProjectAs -packAndGo -forceAutoSave $new_dir/$outname-skeletonization.hx
  }
  }
}
}
echo "finished"
