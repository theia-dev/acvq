from ij import IJ, ImagePlus, ImageStack
from ij.io import Opener
from ij.io import FileSaver
from loci.plugins import BF
from loci.plugins. in import ImporterOptions
from loci.formats import ImageReader
from loci.formats import MetadataTools
from ome.units import UNITS
from ij.plugin import ZProjector
from ij.gui import GenericDialog
import os
import re
import time

outDirChoices = ["New Directory; no subfolders", "New Directory; keep input subfolders",
                 "Within (subfolders of) input directory"]
overwriteChoices = ["Time save: no overwrite existing files", "Overwrite existing files"]
channelSubfolderChoices = ["yes", "no"]
mipChoices = ["yes: tiff", "yes: jpg"]
overwriteList = []
startTime = [time.strftime("%a, %d %b %Y %H:%M:%S"), time.time()]
imageCount = 0
ecnt_max = 500  # max number of tries

gd = GenericDialog("Set Script Parameters")
gd.addStringField("File extension to be processed", ".nd2")
gd.addRadioButtonGroup("Output", outDirChoices, 3, 1, outDirChoices[0])
gd.addRadioButtonGroup("Overwrite", overwriteChoices, 2, 1, overwriteChoices[0])
gd.addRadioButtonGroup("Save channels in different subfolders", channelSubfolderChoices, 2, 1,
                       channelSubfolderChoices[1])
gd.addCheckboxGroup(2, 1, mipChoices, [False, False], ["Do you want maximum intensity projections of your images?"])
gd.showDialog()
if gd.wasCanceled():
    exit()

fileExt = gd.getNextString()
outDirPref = gd.getNextRadioButton()
overwritePref = gd.getNextRadioButton()
channelSubfolderPref = gd.getNextRadioButton()
mipPrefTIFF = gd.getNextBoolean()
mipPrefJPG = gd.getNextBoolean()

if not fileExt.startswith('.'):
    fileExt = '.' + fileExt

inDir = IJ.getDirectory("Choose Directory Containing Input Files")

if outDirPref == outDirChoices[2]:
    outDir = inDir
else:
    outDir = IJ.getDirectory("Choose Directory For Output")
    if outDirPref == outDirChoices[1]:
        for dirpath, dirnames, filenames in os.walk(inDir):
            if any([fileExt in f for f in filenames]):
                '''
                Checks if the input subfolder contain an input file.
                '''
                structure = os.path.join(outDir, dirpath[len(inDir):])
                if not os.path.isdir(structure):
                    os.makedirs(structure)


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


def waitFor(cmd, ecnt_max):
    '''
    Tries to open or save a file. If (network) storage is not reachable it will
    try for a max number of times before
    '''
    ecnt = 0
    while True:
        try:
            return cmd
        except IOError:
            ecnt += 1
            if ecnt <= ecnt_max:
                time.sleep(30)
            else:
                raise IOError("Maximum Number of tries reached.")


for root, dirs, files in os.walk(inDir):
    for file in files:
        if file.endswith(".nd2"):
            options = ImporterOptions()
            options.setAutoscale(True)
            options.setId(os.path.join(root, file))
            options.setSplitChannels(True)
            imps = waitFor(BF.openImagePlus(options), ecnt_max)
            imageCount += 1
            for imp in imps:
                reader = ImageReader()
                omeMeta = MetadataTools.createOMEXMLMetadata()
                reader.setMetadataStore(omeMeta)
                reader.setId(os.path.join(root, file))

                filename = str(imp)
                channel_id = int(re.findall("C=(\d)", filename)[0])
                channel_name = omeMeta.getChannelName(0, channel_id)
                out_name = filename.split('"')[1]
                out_name = out_name.split(".nd2")[0] + "_" + str(channel_name)
                out_name = out_name.replace(" ", "")

                physSizeX = omeMeta.getPixelsPhysicalSizeX(0)
                physSizeY = omeMeta.getPixelsPhysicalSizeY(0)
                physSizeZ = omeMeta.getPixelsPhysicalSizeZ(0)
                stackSizeX = omeMeta.getPixelsSizeX(0).getValue()
                stackSizeY = omeMeta.getPixelsSizeY(0).getValue()
                stackSizeZ = omeMeta.getPixelsSizeZ(0).getValue()
                IJ.log(out_name + "," + str(physSizeX.value()) + "," + str(physSizeY.value()) + "," + str(
                    physSizeZ.value()) + "," + str(stackSizeX) + "," + str(stackSizeY) + "," + str(stackSizeZ))
                if outDirPref == outDirChoices[0] and channelSubfolderPref == "no":
                    out_file = os.path.join(outDir, out_name + ".tiff")
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = os.path.join(outDir, "MIP", out_name)
                        if not os.path.isdir(os.path.join(outDir, "MIP")):
                            os.mkdir(os.path.join(outDir, "MIP"))
                        outimp = maxZprojection(imp)
                        waitFor(saveMip(outimp, mipOutFile), ecnt_max)

                elif outDirPref == outDirChoices[0] and channelSubfolderPref == "yes":
                    out_file = os.path.join(outDir, channel_name, out_name + ".tiff")
                    if not os.path.isdir(os.path.join(outDir, channel_name)):
                        os.mkdir(os.path.join(outDir, channel_name))
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = os.path.join(outDir, channel_name, "MIP", out_name)
                        if not os.path.isdir(os.path.join(outDir, channel_name, "MIP")):
                            os.mkdir(os.path.join(outDir, channel_name, "MIP"))
                        outimp = maxZprojection(imp)
                        waitFor(saveMip(outimp, mipOutFile), ecnt_max)

                elif outDirPref == outDirChoices[1] and channelSubfolderPref == "no":
                    outSubDir = root.replace(inDir, outDir)
                    out_file = os.path.join(outSubDir, out_name + ".tiff")
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        waitFor(saveMip(outimp, mipOutFile), ecnt_max)

                elif outDirPref == outDirChoices[1] and channelSubfolderPref == "yes":
                    outSubDir = root.replace(inDir, outDir)
                    if not os.path.isdir(os.path.join(outSubDir, channel_name)):
                        os.mkdir(os.path.join(outSubDir, channel_name))
                    out_file = os.path.join(outSubDir, channel_name, out_name + ".tiff")
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[2] and channelSubfolderPref == "no":
                    out_file = os.path.join(root, out_name + ".tiff")
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        waitFor(saveMip(outimp, mipOutFile), ecnt_max)

                elif outDirPref == outDirChoices[2] and channelSubfolderPref == "yes":
                    out_file = os.path.join(root, channel_name, out_name + ".tiff")
                    if not os.path.isdir(os.path.join(root, channel_name)):
                        os.mkdir(os.path.join(root, channel_name))
                    waitFor(saveImage(imp, out_file), ecnt_max)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        waitFor(saveMip(outimp, mipOutFile), ecnt_max)

info = IJ.getLog()
with open(os.path.join(outDir, "VoxelSize.txt"), 'w') as output:
    output.write(info)

IJ.log("\\Clear")
IJ.log("Finished")
endTime = [time.strftime("%a, %d %b %Y %H:%M:%S"), time.time()]

if overwriteList:
    with open(os.path.join(outDir, "Existing-Files.txt"), 'w') as f:
        for item in overwriteList:
            f.write("%s\n" % item)

with open(os.path.join(outDir, "Log.txt"), 'w') as L:
    L.write("Time started: " + str(startTime[0]) + "\n" +
            "Time finished: " + str(endTime[0]) + "\n" +
            "Preferences: \n" + outDirPref + "\n" +
            overwritePref + "\n" +
            channelSubfolderPref + "\n" +
            "\n" +
            str(imageCount) + " nd2 files processed in " +
            str((endTime[1] - startTime[1]) / 60) + " min \n")
    if overwriteList:
        L.write("Existing Files: \n")
        for item in overwriteList:
            L.write("%s\n" % item)
