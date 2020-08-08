### Provide directory paths without quotes ("") but between curly brackets ({}) ###

# Voxel Size options for both *.hx Scripts
  # either select the voxelsize file from the ToTiff.py scripts (leave the variables below as 'na')
  set voxel_dir [file normalize {path\to\VoxelSize.txt}]
  # set voxel_dir None
  # or set the voxel sizes here manually and set vozel-dir None
  set x_voxel na
  set y_voxel na
  set z_voxel na
  set x_dim na
  set y_dim na
  set z_dim na

# Options for the Deconvolution.hx script
  # directory where the tiff files (converted from the raw format) are located
set tiffInDir [file normalize {path\to\inputdir}]
  # directory where the deconvoluted files should be saved
set deconOutDir [file normalize {path\to\output\dir}]
  # provide a string to identify the input images, can be empty
set inID ""
  # provide a string for the output filename, can be empty ("")
set outID "_deconv"
  # set Kernel for Median filter, default 3
set median_kernel 3
  # Gaussian Filtering, sigma
set gauss_sigma_x 1
set gauss_sigma_y 1
set gauss_sigma_z 1
  # Gaussian Filtering, kernel
set gauss_kernel_x 3
set gauss_kernel_y 3
set gauss_kernel_z 3
  # Deconvolution
set dec_borderW_x 0
set dec_borderW_y 0
set dec_borderW_z 8
set dec_iterations 20
set dec_initial 0
set dec_overrelax 1
set dec_regular 0
set dec_method 0
set dec_na 0.45
set dec_lambda 0.52
set dec_n 1.333
set dec_mode 1
  # save project y or n
set saveProj y
