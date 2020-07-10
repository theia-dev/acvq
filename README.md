# Script toolbox for 3D image processing

These are the scripts to automate the steps used in the protocol '3D Quantification of vascular structures in stack confocal images' submitted to starProtocols.
This protocol utilizes [Fiji](https://imagej.net/Fiji) [[1]](#1), [Amira, ThermoFisher](https://www.fei-software-center.com/forms/amira-trial/) [[2]](#2) and [WinFiber3D](https://mrl.sci.utah.edu/software/winfiber3d/ ) for the quantitative analysis of z-stack vascular images.

Following the protocol, the scripts are to be used in the following order:
1. ToTiff.py
1. pass
1. binarization.py
1. pass

However, they can be used as single instances as well.

## Short protocol

1. Use the ToTiff.py to convert image files from a proprietary file format to tiff files and read out the voxel size. By default, use the following options:
  * Output: New directory, no subfolders
  * Overwrite: user's choice
  * Save channels in different subfolders: yes
  * Maximum intensity projections: yes (tiff or jpg)
1.
1. Use the binarize.py script to binarize the image in Fiji. Following options:
  * Output: New directory, no subfolders
  * Overwrite: user's choice
  * Threshold: each slice or stack histogram, depending on the image. In doubt, try both. See also Troubleshooting.
  * Maximum intensity projections: yes (tiff or jpg)



## ToTiff.py

This script uses the bioformats plugin to read proprietary microscopy image formats into ImageJ.
If the input image contains several channels, they will be split into several files and the channel name will be added to the filename.
Eventually, the images will be saved as tiff files.
Additionally, a txt file with the voxel sizes for each output image is created.
This voxel size file is used subsequently in the Tcl scripts for Amira.
The script can be opened from within ImageJ: *Plugins->Macros->Run* or using the command line.

![](docs/screenshots/ToTiff.jpg?raw=True)

First, set the extension of the image files from the microscopy software, e.g. 'nd2'.
The output can be in a new folder without subfolders (*recommended for the protocol*) or the input directory tree can be recreated in the output folder.
Be aware, that if the filenames between subfolders are equal, the images will get overwritten or not processed, depending on the next option. **Best practice is to use unique filenames!**
Alternatively, the tiff files can be written within the subfolders of the input directory.  
The channels of the input image are split into single files which can be separated in subfolders (*recommended for the protocol*).  
Additionally, maximum intensity projections of the z-stack images can be saved (*recommended for the protocol*).
Those files will be saved in a subfolder named "MIP".
The channel option applies.


## binarize.py

This script binarizes the input image using the AutoThreshold module in Fiji with the Otsu method.

![](docs/screenshots/binarization.png?raw=True)

The script processes tif(f) input files.
If there are tiff files which are not of interest for the binarize, a string can be provided to identify the relevant images.
If the string is empty all tif(f) files will be processed.  
The output settings are similar to the [ToTiff.py](#ToTiff.py) script.  
There is a choice of whether the histogram of each slice is computed or if the histogram of the complete stack is computed (see also Troubleshooting Step 1 in the protocol).
Moreover, both methods can be applied and the output can be compared manually.  
Additionally, maximum intensity projections of the binarized z-stack images can be saved (*recommended for the protocol*).



# References

<a id="1">[1]</a>
> Schindelin, Johannes, Ignacio Arganda-Carreras, Erwin Frise, Verena Kaynig, Mark Longair, Tobias Pietzsch, Stephan Preibisch, et al.
> “Fiji: An Open-Source Platform for Biological-Image Analysis.”
> *Nature Methods* **9**, 7 (2012)
> doi: [10.1038/nmeth.2019](https://doi.org/10.1038/nmeth.2019)

<a id="2">[2]</a>
> Stalling, Detlev, Malte Westerhoff, and Hans-Christian Hege.
> “Amira: A Highly Interactive System for Visual Data Analysis.”
> In *Visualization Handbook*, **749–67**. Elsevier, 2005
> doi: [10.1016/B978-012387582-2/50040-X](https://doi.org/10.1016/B978-012387582-2/50040-X)
