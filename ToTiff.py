from ij import IJ, ImagePlus, ImageStack
from ij.io import Opener
from ij.io import FileSaver
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from loci.formats import ImageReader
from loci.formats import MetadataTools
from ome.units import UNITS
from ij.plugin import ZProjector
from ij.gui import GenericDialog
import os
import re
import time
import logging


outDirChoices = ["New Directory, no subfolders", "New Directory, keep input subfolders",
                 "Within (subfolders of) input directory"]
overwriteChoices = ["NO overwrite existing files", "Overwrite existing files"]
channelSubfolderChoices = ["yes", "no"]
mipChoices = ["yes: tiff", "yes: jpg"]
overwriteList = []
startTime = time.time()
imageCount = 0
voxel_info = str()

gd = GenericDialog("Set ToTiff Options")
gd.addStringField("File extension to be processed", ".nd2")
gd.addRadioButtonGroup("Output", outDirChoices, 3, 1, outDirChoices[0])
gd.addRadioButtonGroup("Overwrite", overwriteChoices, 2, 1, overwriteChoices[0])
gd.addRadioButtonGroup("Save channels in different subfolders", channelSubfolderChoices, 1, 1,
                       channelSubfolderChoices[0])
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

logging.info('Start ToTiff script')
logging.info('Preferences')
logging.info('    Input dir: %s', inDir)
logging.info('    Output dir: %s', outDir)
logging.info('    Output format: %s', outDirPref)
logging.info('    %s', overwritePref)
logging.info('    Save channels in different subfolders: %s', channelSubfolderPref)


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


def saveMip(img, file_path):
    if mipPrefTIFF:
        FileSaver(img).saveAsTiff(file_path + ".tiff")
    if mipPrefJPG:
        FileSaver(img).saveAsJpeg(file_path + ".jpg")


for root, dirs, files in os.walk(inDir):
    for file in files:
        if file.endswith(fileExt):
            logging.info('Starting image #%i (%s)', imageCount, str(file))
            options = ImporterOptions()
            options.setAutoscale(True)
            options.setId(os.path.join(root, file))
            options.setSplitChannels(True)
            imps = BF.openImagePlus(options)
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
                out_name = out_name.split(fileExt)[0] + "_" + str(channel_name)
                out_name = out_name.replace(" ", "")

                physSizeX = omeMeta.getPixelsPhysicalSizeX(0)
                physSizeY = omeMeta.getPixelsPhysicalSizeY(0)
                physSizeZ = omeMeta.getPixelsPhysicalSizeZ(0)
                stackSizeX = omeMeta.getPixelsSizeX(0).getValue()
                stackSizeY = omeMeta.getPixelsSizeY(0).getValue()
                stackSizeZ = omeMeta.getPixelsSizeZ(0).getValue()
                logging.info('    Saving under: %s', out_name)
                logging.info('        Size in micrometer: %.4f, %.4f, %.4f', physSizeX.value(), physSizeY.value(), physSizeZ.value())
                logging.info('        Size in pixel: %i, %i, %i', stackSizeX, stackSizeY, stackSizeZ)
                voxel_info += ','.join([str(entry) for entry in (out_name, physSizeX.value(), physSizeY.value(), physSizeZ.value(),
                                                 stackSizeX, stackSizeY, stackSizeZ)]) + '\n'
                if outDirPref == outDirChoices[0] and channelSubfolderPref == "no":
                    out_file = os.path.join(outDir, out_name + ".tiff")
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = os.path.join(outDir, "MIP", out_name)
                        if not os.path.isdir(os.path.join(outDir, "MIP")):
                            os.mkdir(os.path.join(outDir, "MIP"))
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[0] and channelSubfolderPref == "yes":
                    out_file = os.path.join(outDir, channel_name, out_name + ".tiff")
                    if not os.path.isdir(os.path.join(outDir, channel_name)):
                        os.mkdir(os.path.join(outDir, channel_name))
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = os.path.join(outDir, channel_name, "MIP", out_name)
                        if not os.path.isdir(os.path.join(outDir, channel_name, "MIP")):
                            os.mkdir(os.path.join(outDir, channel_name, "MIP"))
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[1] and channelSubfolderPref == "no":
                    outSubDir = root.replace(inDir, outDir)
                    out_file = os.path.join(outSubDir, out_name + ".tiff")
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[1] and channelSubfolderPref == "yes":
                    outSubDir = root.replace(inDir, outDir)
                    if not os.path.isdir(os.path.join(outSubDir, channel_name)):
                        os.mkdir(os.path.join(outSubDir, channel_name))
                    out_file = os.path.join(outSubDir, channel_name, out_name + ".tiff")
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[2] and channelSubfolderPref == "no":
                    out_file = os.path.join(root, out_name + ".tiff")
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

                elif outDirPref == outDirChoices[2] and channelSubfolderPref == "yes":
                    out_file = os.path.join(root, channel_name, out_name + ".tiff")
                    if not os.path.isdir(os.path.join(root, channel_name)):
                        os.mkdir(os.path.join(root, channel_name))
                    saveImage(imp, out_file)
                    if any([mipPrefJPG, mipPrefTIFF]):
                        mipOutFile = out_file.replace(".tiff", "_mip")
                        outimp = maxZprojection(imp)
                        saveMip(outimp, mipOutFile)

with open(os.path.join(outDir, "VoxelSize.txt"), 'w') as output:
    output.write(voxel_info)

duration = time.time()- startTime
logging.info('Processing finished')

duration_h, rest = divmod(duration, 3600)
duration_min, rest = divmod(rest, 60)
duration_s = int(round(rest))
if duration_h > 0:
    logging.info('%i files procced in %i h, %i min and %i s', imageCount, duration_h, duration_min, duration_s)
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
