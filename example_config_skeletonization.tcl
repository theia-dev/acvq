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

# Options for the SMT.hx script
  # directory where the binarized tiffs are located
set BinInDir [file normalize {path\to\binarized_images}]
  # directory where the mv3D files should be saved
set MV3DOutDir [file normalize {path\to\out_put}]
  # provide a string to identify the input images, can be empty
set BinInID ""
  # provide a string for the output filename, can be empty ("")
set MV3DOutID "_mv3D"
  # set Chamfer interpretation (0 - 3D, 1 "XY planes"; default 1)
set chamferInterpret 1
  # set smoothing coefficients (default smoothin 0.5 and adhere to original data 0.25, # of iterations 10)
set smooth_coeff 0.5
set smooth_adhere 0.25
set smooth_iter 10

set len_list [list 2 5 7 10]

  # set islandsize in um
set islandsize 600
  # save project y or n
set saveProj y
