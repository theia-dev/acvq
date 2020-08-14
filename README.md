# Script toolbox for 3D image processing

This toolbox provides scripts to automate the steps outlines in the manuscript '3D quantification of vascular-like structures in z-stack confocal images' submitted to starProtocols.
This protocol utilizes [Fiji](https://imagej.net/Fiji) [[1]](#1), [Amira, ThermoFisher](https://www.fei-software-center.com/forms/amira-trial/) [[2]](#2) and [WinFiber3D](https://mrl.sci.utah.edu/software/winfiber3d/ ) to skeletonize and reconstruct vascular structures in z-stack confocal images.
Eventually, morphometrical parameters, such as vessel number, length, diameter as well as branching are determined.

Following the protocol, the scripts are to be used in the following order:
1. `ToTiff.py`
1. `Deconvolution.hx`
1. `Binarize.py`
1. `Skeletonization.hx`
1. `WinFiber.py`*
1. `WinFiberGatherOutput.py`*
1. `WinFiberGatherSegmentData.py`*

However, they can be used as single instances as well.

`ToTiff.py` and `Binarize.py` are written in python for ImageJ/Fiji and can be directly used from within ImageJ.
`Deconvolution.hx` and `Skeletonization.hx` are Tcl scripts which can be started from within Amira.
However, they rely on a configuration file.
Please refer to [Scripts for Amira](#scripts-for-amira) for details.
The WinFiber scripts (\*) rely on [`Python` 3.7 or higher](https://www.python.org/).
Please refer to the [Python website](https://www.python.org/about/gettingstarted/) to get started with python.

## Short protocol

1. Use the `ToTiff.py` to convert image files from a proprietary file format to tiff files and read out the voxel size. By default, use the following options:
  * Output: New directory, no subfolders
  * Overwrite: user's choice
  * Save channels in different subfolders: yes
  * Maximum intensity projections: yes (tiff or jpg)
1. Deconvolute the images with `Deconvolution.hx`
  * either use `mkconfig.py` to create the config file and run Amira
  * or create the config file manually, change the path in `Deconvolution.hx` and run
1. Use the `binarize.py` script to binarize the image in Fiji. Following options:
  * Output: New directory, no subfolders
  * Overwrite: user's choice
  * Threshold: each slice or stack histogram, depending on the image. In doubt, try both. See also Troubleshooting.
  * Maximum intensity projections: yes (tiff or jpg)
1. Skeletonize and save \*.mv3D files with `Skeletonization.hx`
    * either use `mkconfig.py` to create the config file and run Amira
    * or create the config file manually
1. WinFiber.py
    * adapt the pyautogui position parameters
1. WinFiberGatherOutput.py*
1. WinFiberGatherSegmentData.py



## ImageJ scripts

The scripts can be opened from within ImageJ/FiJi: *Plugins->Macros->Run* or using the command line.

### `ToTiff.py`

This script uses the [Bioformats](https://www.openmicroscopy.org/bio-formats/) plugin to read proprietary microscopy image formats into ImageJ.
If the input image contains several channels, they will be split into several files and the channel name will be added to the filename.
Eventually, the images will be saved as tiff files.
Additionally, a txt file with the voxel sizes for each output image is created.
This voxel size file is used subsequently in the \*.hx scripts for Amira.

![](docs/screenshots/ToTiff.png?raw=True)

First, set the extension of the image files from the microscopy software, e.g. 'nd2'.
The output can be in a new folder without subfolders (*recommended for the protocol*) or the input directory tree can be recreated in the output folder.
Be aware, that if the filenames between subfolders are equal, the images will get overwritten or not processed, depending on the next option. **Best practice is to use unique filenames!**
Alternatively, the tiff files can be written within the subfolders of the input directory.  
The channels of the input image are split into single files which can be separated in subfolders (*recommended for the protocol*).  
Additionally, maximum intensity projections of the z-stack images can be saved (*recommended for the protocol*).
Those files will be saved in a subfolder named "MIP".
The channel option applies.

### binarize.py

This script binarizes the input image using the [AutoThreshold] (https://imagej.net/Auto_Threshold) module in Fiji with the Otsu method.

![](docs/screenshots/binarization.png?raw=True)

The script processes tif(f) input files.
If there are tiff files which are not of interest for the binarization step, a string can be provided to identify the relevant images.
If the string is empty, all tiff files will be processed.  
The output settings are similar to the [ToTiff.py](#ToTiff.py) script.  
There is a choice of whether the histogram of each slice is computed or if the histogram of the complete stack is computed (see also Troubleshooting Step 1 in the submitted manuscript).
Moreover, both methods can be applied and the output can be compared later.  
Additionally, maximum intensity projections of the binarized z-stack images can be saved (*recommended for the protocol*).

## Scripts for Amira

The scripts for Amira are written in Tcl and use the Amira script interface.
There are two scripts, one for deconvolution of the confocal image, the other one for the skeletonization of the binarised structures.
Both scripts rely on a configuration file which provides the path to the input images as well as the output and also the various settings of the Amira modules.
There are two ways to create the configuration file.

### mkconfig.py

mkconfig.py uses the user input to write the config file.
Each parameters which needs to be set, will be queried.
The script needs and argument which is either `--make` (`-mk`) or `--run` (`-r`).
* `--make` will only create and save the config file. The user will need to provide this file to the \*.hx script manually
* `--run` will create and save the config file but also provide it to the \*.hx file. It will then attempt to open Amira and run the \*.hx script.
The `--save` (`-s`) argument will save the altered \*.hx file which was used in Amira.
Note,  Amira.exe is started with the `-no_gui` option.

`mkconfig.py` can be run from a locally installed python or using the python which is shipped with Amira.
It can usually be found in the Amira install folder /python/python.exe.

### Example configs
Alternatively, the example configs (example_config_deconvolution.tcl and example_config_skeletonization.tcl) can be adapted accordingly.
Refer to the comments in the example files for details.
The path to the adapted config files might need to be adapted in the \*.hx files.

## Winfiber3D

The scripts for automating the WinFiber3D output relies on a local python install.
Some experience with python might be helpful.

### WinFiber.py

WinFiber.py relies heavily on the [pyautogui](https://pyautogui.readthedocs.io/en/latest/) package which controls mouse and keyboard movements.
Although, it was aimed for as little mouse movements as possible, some were inevitable.
Hence, the pyautogui parameters need to be adapted for the screen resolution and screen size.
The WinFiber data is exported to a \*.xls file, one file per input image.
Moreover, screenshots of the WinFiber window will be saved.
For further information on the output of WinFiber3D, refer to the WinFiber3D manual.

### WinFiberGatherOutput.py

This script gathers the information of various \*.xls files into one csv file.

Th following information is collected from the Winfiber3D export:

* \# Range min
* \# Range max
* \# Total vessels
* \# Total branch points
* \# Total end points
* \# Avg branch points per vessel
* \# Avg end points per vessel
* \# Total volume of box
* \# Total vessel volume
* \# Volume ratio
* \# Total vessel length
* \# Average vessel length

Additionally, the number of segments is collected and the overall average diameter is calculated using the average diameter of each segment.

### WinFiberGatherSegmentData.py

In addition to the data of the vessels, WinFiber3D provides data of the segments.
This script reads out the angles (Pr(x), x, and z) as well as length and diameter information for each segment.
The output is written in 5 different files.
For further information on the angles calculated by WinFiber3D, refer to the WinFiber3D manual.

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
