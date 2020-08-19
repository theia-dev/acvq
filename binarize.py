from ij import IJ, ImagePlus, ImageStack
from ij.io import Opener
from ij.io import FileSaver
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from loci.formats import ImageReader
from loci.formats import MetadataTools
from ome.units import UNITS
from ij.plugin import ZProjector
from ij.plugin import Duplicator
from ij.gui import GenericDialog
import os
import re
import time
import logging

outDirChoices = ["New Directory, no subfolders", "New Directory, keep input subfolders",
                 "Within (subfolders of) input directory"]
thresholdChoices = ["Otsu, white objects, stack, histogram of each slice",
                    "Otsu, white objects, stack, stack histogram",
                    "Otsu, white objects, try both methods"]
overwriteChoices = ["NO overwrite existing files", "Overwrite existing files"]
mipChoices = ["yes: tiff", "yes: jpg"]
overwriteList = []
startTime = time.time()
imageCount = 0

gd = GenericDialog("Set binarization.py Options")
gd.addStringField("String to identify your input images", "_deconv")
gd.addRadioButtonGroup("Output", outDirChoices, 3, 1, outDirChoices[0])
gd.addRadioButtonGroup("Threshold Settings", thresholdChoices, 3, 1, thresholdChoices[0])
gd.addRadioButtonGroup("Overwrite", overwriteChoices, 2, 1, overwriteChoices[0])
gd.addCheckboxGroup(2, 1, mipChoices, [False, False], ["Do you want maximum intensity projections of your images?"])
gd.showDialog()
if gd.wasCanceled():
    exit()

fileID = gd.getNextString()
outDirPref = gd.getNextRadioButton()
thresholdPref = gd.getNextRadioButton()
overwritePref = gd.getNextRadioButton()
mipPrefTIFF = gd.getNextBoolean()
mipPrefJPG = gd.getNextBoolean()
IJ.redirectErrorMessages(True)

inDir = IJ.getDirectory("Choose Directory Containing Input Files")
if inDir is None:
    exit('No input directory selected!')

if outDirPref == outDirChoices[2]:
    outDir = inDir
else:
    outDir = IJ.getDirectory("Choose Directory For Output")
    if outDir is None:
        exit('No output directory selected!')
    if outDirPref == outDirChoices[1]:
        for dirpath, dirnames, filenames in os.walk(inDir):
            if any([fileExt in f for f in filenames]):
                structure = os.path.join(outDir, dirpath[len(inDir):])
                if not os.path.isdir(structure):
                    os.makedirs(structure)

logging.basicConfig(filename=os.path.join(outDir, "Log.txt"), filemode='w', level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s >> %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

logging.info('Start binarization script')
logging.info('Preferences')
logging.info('    Input dir: %s', inDir)
logging.info('    Output dir: %s', outDir)
logging.info('    Output format: %s', outDirPref)
logging.info('    %s', overwritePref)
logging.info('    File ID string %s', fileID)
logging.info('    Threshold Option %s', thresholdPref)


def checkDirs(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def saveImage(imp, out_file):
    if overwritePref == overwriteChoices[0]:
        if not os.path.exists(out_file):
            FileSaver(imp).saveAsTiff(out_file)
        else:
            overwriteList.append(out_file)
    elif overwritePref == overwriteChoices[1]:
        if not os.path.exists(out_file):
            FileSaver(imp).saveAsTiff(out_file)

        else:
            overwriteList.append(out_file)
            FileSaver(imp).saveAsTiff(out_file)


def maxZprojection(stackimp):
    zp = ZProjector(stackimp)
    zp.setMethod(ZProjector.MAX_METHOD)
    zp.doProjection()
    zpimp = zp.getProjection()
    return zpimp


def saveMip(img, file):
    if mipPrefTIFF:
        FileSaver(img).saveAsTiff(file + ".tiff")
    if mipPrefJPG:
        FileSaver(img).saveAsJpeg(file + ".jpg")


def getThresholdOptions(thresholdPref):
    if thresholdPref == thresholdChoices[0]:
        method = 'Otsu white stack'
        fileN = 'each_slice'
    elif thresholdPref == thresholdChoices[1]:
        method = 'Otsu white stack use_stack_histogram'
        fileN = 'stack_histogram'
    return method, fileN


def setThreshold(img, outDir, out_name, thresholdPref):
    if thresholdPref == thresholdChoices[2]:
        img2 = img.duplicate()
        m, f = getThresholdOptions(thresholdChoices[0])
        IJ.run(img, "Auto Threshold", "method=" + m)
        out_file = os.path.join(outDir, f, out_name)
        checkDirs(os.path.join(outDir, f))
        saveImage(img, out_file)
        m, f = getThresholdOptions(thresholdChoices[1])
        IJ.run(img2, "Auto Threshold", "method=" + m)
        out_file = os.path.join(outDir, f, out_name)
        checkDirs(os.path.join(outDir, f))
        saveImage(img2, out_file)
    else:
        m, f = getThresholdOptions(thresholdPref)
        IJ.run(img, "Auto Threshold", "method=" + m)
        out_file = os.path.join(outDir, out_name)
        saveImage(img, out_file)

# ToDo: check the naming of the output images
for root, dirs, files in os.walk(inDir):
    for file in files:
        find = re.findall(fileID, file)
        if find:
            if file.endswith(".tiff") | file.endswith(".tif"):
                out_name = re.sub("\.tiff?$", "_binary.tiff", file)
                out_file = os.path.join(outDir, out_name)
                imp = IJ.openImage(os.path.join(root, file))
                imageCount += 1
                setThreshold(imp, outDir, out_name, thresholdPref)
                if any([mipPrefJPG, mipPrefTIFF]):
                    if thresholdPref != thresholdChoices[2]:
                        mipOutFile = os.path.join(outDir, "MIP", out_name.replace(".tiff", ""))
                        checkDirs(os.path.join(outDir, "MIP"))
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)
                    else:
                        imp2 = imp.duplicate()
                        thresholdPref = thresholdChoices[0]
                        m, f = getThresholdOptions(thresholdPref)
                        mipOutFile = os.path.join(outDir, f, "MIP", out_name.replace(".tiff", ""))
                        outimp = maxZprojection(imp)
                        checkDirs(os.path.join(outDir, f, "MIP"))
                        saveMip(outimp, mipOutFile)
                        thresholdPref = thresholdChoices[1]
                        m, f = getThresholdOptions(thresholdPref)
                        mipOutFile = os.path.join(outDir, f, "MIP", out_name.replace(".tiff", ""))
                        checkDirs(os.path.join(outDir, f, "MIP"))
                        outimp2 = maxZprojection(imp2)
                        saveMip(outimp2, mipOutFile)
                        thresholdPref = thresholdChoices[2]


duration = time.time() - startTime

logging.info('Processing finished')

duration_h, rest = divmod(duration, 3600)
duration_min, rest = divmod(rest, 60)
duration_s = int(round(rest))
if duration_h > 0:
    logging.info('%i files procced in %i h, %i min and %i s', imageCount, duration_h, duration_min,
                 duration_s)
elif duration_min > 0:
    logging.info('%i files procced in %i min and %i s', imageCount, duration_min, duration_s)
else:
    logging.info('%i files procced in %i s', imageCount, duration_s)

if overwriteList:
    logging.info('Existing Files:')
    for item in overwriteList:
        logging.info('    %s', item)

IJ.log("\\Clear")
IJ.log("Finished")
