source [file normalize {A:\rds\Batch-Processing-Scripts\3DQuantVascularStructures\Config.tcl}]
#  Subfolders??
#####################
set dim_list [list x_voxel y_voxel z_voxel x_dim y_dim z_dim]
set dim_dict [dict create  x_voxel 0 y_voxel 1 z_voxel 2 x_dim 3 y_dim 4 z_dim 5]
set itemlist [
    concat [
        glob -nocomplain -directory $tiffInDir -types hidden *] [
        glob -nocomplain -directory $tiffInDir *.tiff]
		]

if {[string trim $inID] != ""} {
  set itemlist [lsearch -regexp -all -inline $itemlist .*$inID*.]
    }


foreach entry $itemlist {
set output [file tail $entry]
set output [split $output "/."]
set outname [lindex $output 0]
set outfile [concat $deconOutDir/$outname$outID.tiff]

if {[info exists voxel_dir] == 1} {
set voxel_file [open $voxel_dir]
set voxel_data [read $voxel_file]
set measure_dict [dict create]
close $voxel_file
foreach row [split [string trim $voxel_data] \n] {
    set row [lassign [split $row ,] key]
    dict set measure_dict [string trim $key] [concat {*}$row]
}
set temp [dict get $measure_dict $outname]
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
if { [file exists $outfile] == 0} {

remove -all
set hideNewModules 0
set input [ load -tif +mode 100 +box 0 [expr ($x_dim-1)*$x_voxel] 0 [expr ($y_dim-1)*$y_voxel] 0 [expr ($z_dim-1)*$z_voxel] $entry ]

set cd [create HxCorrectZDrop]
$cd data connect $input
$cd fire
$cd mode setValue 0
$cd fire
set cd_result [$cd create result]

set imf [create HxImageFilters]
$imf setFilter median
$imf setFilterOrientation 3
$imf fire
$imf kernel setValue 0 $median_kernel
$imf data connect $cd_result
$imf fire
$imf doIt hit
$imf fire
set imf_result [$imf getResult]

set imf_g [create HxImageFilters]
$imf_g setFilter gaussian
$imf_g setFilterOrientation 3
$imf_g fire
$imf_g data connect $imf_result
$imf_g fire
$imf_g sigma setValue 0 $gauss_sigma_x
$imf_g sigma setValue 1 $gauss_sigma_y
$imf_g sigma setValue 2 $gauss_sigma_z
$imf_g fire
$imf_g kernel setValue 0 $gauss_kernel_x
$imf_g kernel setValue 1 $gauss_kernel_x
$imf_g kernel setValue 2 $gauss_kernel_x
$imf_g fire
$imf_g doIt hit
$imf_g fire
set imf_g_result [$imf_g getResult]

set deconv [create HxDeconvolution]
$deconv data connect $imf_g_result
$deconv fire
$deconv borderWidth setValue 0 $dec_borderW_x
$deconv borderWidth setValue 1 $dec_borderW_y
$deconv borderWidth setValue 2 $dec_borderW_z
$deconv fire
$deconv iterations setValue $dec_iterations
$deconv fire
$deconv initialEstimate setValue $dec_initial
$deconv overrelaxation setValue $dec_overrelax
$deconv regularization setValue $dec_regular
$deconv method setValue $dec_method
$deconv fire
$deconv parameters setValue 0 $dec_na
$deconv parameters setValue 1 $dec_lambda
$deconv parameters setValue 2 $dec_n
$deconv  mode setValue $dec_mode
$deconv fire
set deconv_result [$deconv create result]
set deconv_psf [$deconv create result1]

$deconv_result exportData "3D Tiff" $outfile
if {$saveProj eq "y"} {
saveProjectAs -packAndGo -forceAutoSave $deconOutDir/$outname-$outID.hx
}
}
}
echo "finished"
