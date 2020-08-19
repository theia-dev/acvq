from jinja2 import Template, Environment
import os
from pathlib import Path
import sys
import subprocess
import re
import tempfile

env = Environment(variable_start_string='@=', variable_end_string='=@')

tm_deconv = env.from_string('''
set voxel_dir [file normalize {@= voxel_dir =@}]
set x_voxel @= x_voxel =@
set y_voxel @= y_voxel =@
set z_voxel @= z_voxel =@
set x_dim @= x_dim =@
set y_dim @= y_dim =@
set z_dim @= z_dim =@

set tiffInDir [file normalize {@= tiffInDir =@}]
set deconOutDir [file normalize {@= deconOutDir =@}]
set inID @= inID =@
set outID @= outID =@

set median_kernel @= median_kernel =@
set gauss_sigma_x @= gauss_sigma_x =@
set gauss_sigma_y @= gauss_sigma_y =@
set gauss_sigma_z @= gauss_sigma_z =@
set gauss_kernel_x @= gauss_kernel_x =@
set gauss_kernel_y @= gauss_kernel_y =@
set gauss_kernel_z @= gauss_kernel_z =@

set dec_borderW_x @= dec_borderW_x =@
set dec_borderW_y @= dec_borderW_y =@
set dec_borderW_z @= dec_borderW_z =@
set dec_iterations @= dec_iterations =@
set dec_initial @= dec_initial =@
set dec_overrelax @= dec_overrelax =@
set dec_regular @= dec_regular =@
set dec_method @= dec_method =@
set dec_na @= dec_na =@
set dec_lambda @= dec_lambda =@
set dec_n @= dec_n =@
set dec_mode @= dec_mode =@
set saveProj @= saveProj =@
''')

tm_skeleton = env.from_string('''
set voxel_dir [file normalize {@= voxel_dir =@}]
set x_voxel @= x_voxel =@
set y_voxel @= y_voxel =@
set z_voxel @= z_voxel =@
set x_dim @= x_dim =@
set y_dim @= y_dim =@
set z_dim @= z_dim =@

set BinInDir [file normalize {@= BinInDir =@} ]
set MV3DOutDir [file normalize {@= MV3DOutDir =@}]
set BinInID @= BinInID =@
set MV3DOutID @= MV3DOutID =@
set chamferInterpret @= chamferInterpret =@
set smooth_coeff @= smooth_coeff =@
set smooth_adhere @= smooth_adhere =@
set smooth_iter @= smooth_iter =@

set len_list [list @= len_list =@]
set islandsize @= islandsize =@
set saveProj @= saveProj =@
''')


def ask_choice(question, options):
    while True:
        raw_input = None
        print('\n' + question)
        for n, option in enumerate(options):
            print('\t{}: {}'.format(n + 1, option[0]))

        try:
            raw_input = input('Your choice: ')
            value = int(raw_input)
            if len(options) >= value > 0:
                break
            else:
                print('Please try again - {} is not a valid choice. '.format(raw_input))
        except ValueError:
            print('Please try again - {} is not a number. '.format(raw_input))
    return options[value - 1][1]


def check_float(var):
    while True:
        try:
            var = float(var)
            break
        except ValueError:
            var = input("Please provide a number. ")
            continue
    return var


def deconv_config(template):
    voxel_dir = ask_choice('Do you have a file with the voxel sizes?', [
        ['yes', True],
        ['no', False],
    ])

    if voxel_dir:
        x_voxel = y_voxel = z_voxel = x_dim = y_dim = z_dim = 'na'
        voxel_dir = input('Please provide the path to the file with the voxel sizes. ')
        voxel_dir = voxel_dir.replace('"', '')
        while not voxel_dir.endswith(".txt"):
            voxel_dir = input('The filename must end in ".txt". ')
        while not os.path.isfile(voxel_dir):
            voxel_dir = input('This file might not exist or is not readable. Please double check your input. ')
    else:
        voxel_dir = None
        x_voxel = input('Please provide the voxel size in x [µm per voxel]. ')
        check_float(x_voxel)
        y_voxel = input('Please provide the voxel size in y [µm per voxel]. ')
        check_float(y_voxel)
        z_voxel = input('Please provide the voxel size in z [µm per z step size]. ')
        check_float(z_voxel)
        x_dim = input('Please provide the x size of your image in pixel. ')
        check_float(x_dim)
        y_dim = input('Please provide the y size of your image in pixel. ')
        check_float(y_dim)
        z_dim = input('Please provide the z size of your image in steps. ')
        check_float(z_dim)
    tiffInDir = input('Please provide the path to the folder with the tiff files for deconvolution. ')
    tiffInDir = tiffInDir.replace('"', '')
    while not os.path.exists(tiffInDir):
        tiffInDir = input('This path might not exist. Please double check your input. ')
    deconOutDir = input('Please provide the path to the folder where the deconvoluted files will be saved. ')
    deconOutDir = deconOutDir.replace('"', '')
    if not os.path.exists(deconOutDir):
        while True:
            makedir = ask_choice('This path does not exist. Should it be created?', [
                ['yes', True],
                ['no', False],
            ])
            if makedir:
                os.makedirs(deconOutDir)
                break
            else:
                deconOutDir = input(
                    'Please provide the path to the folder where the deconvoluted files will be saved. ')
    inID = input(
        "Please provide a string to identify the input images. Can be empty, then all images in a folder will be processed. ")
    if inID == '':
        inID = '""'
    outID = input(
        'Please provide a string for the output filename. Can be empty, then the filenames will be the same as the input. ')
    if outID == '':
        outID = '""'

    median_kernel = input('Median Filtering. Set the value for the kernel size. ')
    check_float(median_kernel)
    gauss_sigma_x = input('Gaussian Filtering. Set the sigma value in x. ')
    check_float(gauss_sigma_x)
    gauss_sigma_y = input('Gaussian Filtering. Set the sigma value in y. ')
    check_float(gauss_sigma_y)
    gauss_sigma_z = input('Gaussian Filtering. Set the sigma value in z. ')
    check_float(gauss_sigma_z)
    gauss_kernel_x = input('Gaussian Filtering. Set the kernel size in x. ')
    check_float(gauss_kernel_x)
    gauss_kernel_y = input('Gaussian Filtering. Set the kernel size in y. ')
    check_float(gauss_kernel_y)
    gauss_kernel_z = input('Gaussian Filtering. Set the kernel size in z. ')
    check_float(gauss_kernel_z)
    dec_borderW_x = input('Deconvolution. Set the value for the border width in x. ')
    check_float(dec_borderW_x)
    dec_borderW_y = input('Deconvolution. Set the value for the border width in y. ')
    check_float(dec_borderW_y)
    dec_borderW_z = input('Deconvolution. Set the value for the border width in z. ')
    check_float(dec_borderW_z)
    dec_iterations = input('Deconvolution. How many iterations? ')
    check_float(dec_iterations)
    dec_initial = ask_choice('Deconvolution. Please set the inital estimate parameter. ', [
        ['const', 0],
        ['input data', 1],
    ])
    dec_overrelax = ask_choice('Deconvolution. Please set the overrelaxation parameter. ', [
        ['none', 0],
        ['fixed', 1],
        ['optimized', 2],
    ])
    dec_regular = ask_choice('Deconvolution. Please set the regularization parameter. ', [
        ['none', 0],
        ['intensity based', 1],
    ])
    dec_method = ask_choice('Deconvolution. Please set the Deconvolution method. ', [
        ['standard', 0],
        ['blind', 1],
    ])
    dec_na = input('Deconvolution. Please provide the numerical apperture of the objective. ')
    check_float(dec_na)
    dec_lambda = input('Deconvolution. Please provide the emission wavelength in µm. ')
    check_float(dec_lambda)
    while float(dec_lambda) > 1:
        dec_lambda = input('Please use µm. The value should be < 1.')
    dec_n = input("Deconvolution. Please provide the refractive index. ")
    check_float(dec_n)
    dec_mode = ask_choice('Deconvolution. Please set the PSF mode. ', [
        ['widefield', 0],
        ['confocal', 1],
    ])
    saveProj = ask_choice('Would you like to save the Amira project?', [
        ['no', 'n'],
        ['yes', 'y'],
    ])

    conf = template.render(voxel_dir=voxel_dir, x_voxel=x_voxel, y_voxel=y_voxel, z_voxel=z_voxel, x_dim=x_dim,
                           y_dim=y_dim, z_dim=z_dim, tiffInDir=tiffInDir, deconOutDir=deconOutDir, inID=inID,
                           outID=outID, median_kernel=median_kernel, gauss_sigma_x=gauss_sigma_x,
                           gauss_sigma_y=gauss_sigma_y, gauss_sigma_z=gauss_sigma_z,
                           gauss_kernel_x=gauss_kernel_x, gauss_kernel_y=gauss_kernel_y, gauss_kernel_z=gauss_kernel_z,
                           dec_borderW_x=dec_borderW_x, dec_borderW_y=dec_borderW_y, dec_borderW_z=dec_borderW_z,
                           dec_iterations=dec_iterations, dec_initial=dec_initial, dec_overrelax=dec_overrelax,
                           dec_regular=dec_regular, dec_method=dec_method, dec_na=dec_na, dec_lambda=dec_lambda,
                           dec_n=dec_n, dec_mode=dec_mode, saveProj=saveProj
                           )
    return conf


def skeleton_config(template):
    voxel_dir = ask_choice('Do you have a file with the voxel sizes?', [
        ['yes', True],
        ['no', False],
    ])

    if voxel_dir:
        x_voxel = y_voxel = z_voxel = x_dim = y_dim = z_dim = 'na'
        voxel_dir = input('Please provide the path to the file with the voxel sizes. ')
        voxel_dir = voxel_dir.replace('"', '')
        while not voxel_dir.endswith(".txt"):
            voxel_dir = input('The filename must end in ".txt". ')
        while not os.path.isfile(voxel_dir):
            voxel_dir = input('This file might not exist or is not readable. Please double check your input. ')
    else:
        voxel_dir = None
        x_voxel = input('Please provide the voxel size in x [µm per voxel]. ')
        check_float(x_voxel)
        y_voxel = input('Please provide the voxel size in y [µm per voxel]. ')
        check_float(y_voxel)
        z_voxel = input('Please provide the voxel size in z [µm per z step size]. ')
        check_float(z_voxel)
        x_dim = input('Please provide the x size of your image in pixel. ')
        check_float(x_dim)
        y_dim = input('Please provide the y size of your image in pixel. ')
        check_float(y_dim)
        z_dim = input('Please provide the z size of your image in steps. ')
        check_float(z_dim)

    BinInDir = input('Please provide the path to the folder with the binarized files for skeletonization. ')
    BinInDir = BinInDir.replace('"', '')
    while not os.path.exists(BinInDir):
        BinInDir = input('This path might not exist. Please double check your input. ')
    MV3DOutDir = input('Please provide the path to the folder where the MV3D files will be saved. ')
    MV3DOutDir = MV3DOutDir.replace('"', '')
    if not os.path.exists(MV3DOutDir):
        while True:
            makedir = ask_choice('This path does not exist. Would you like to create it?', [
                ['yes', True],
                ['no', False],
            ])
            if makedir:
                os.makedirs(MV3DOutDir)
                break
            else:
                MV3DOutDir = input('Please provide the path to the folder where the deconvoluted files will be saved. ')
    BinInID = input(
        "Please provide a string to identify the input images. Can be empty, then all images in a folder are processed. ")
    if BinInID == '':
        BinInID = '""'
    MV3DOutID = input(
        'Please provide a string for the output filename. Can be empty, then the filenames will be the same as the input. ')
    if MV3DOutID == '':
        MV3DOutID = '""'
    chamferInterpret = ask_choice('Please set chamfer interpretation', [
        ['3D', 0],
        ['XY planes', 1],
    ])
    smooth_coeff = input('Smooth Lines. Set the value for the coefficient. ')
    check_float(smooth_coeff)
    smooth_adhere = input('Smooth Lines. Set the value for adhere to original data. ')
    check_float(smooth_adhere)
    smooth_iter = input('Smooth Lines. How many iterations? ')
    check_float(smooth_iter)
    len_list = input('Len of ends. Enter a value. If you would like to try multiple, separate by space. ')
    len_list = len_list.replace(",", " ")
    len_list = len_list.replace(";", " ")
    islandsize = input('Please provide the size of "islands" in µm^3. ')
    check_float(islandsize)
    saveProj = ask_choice('Would you like to save the Amira project?', [
        ['no', 'n'],
        ['yes', 'y'],
    ])

    conf = template.render(voxel_dir=voxel_dir, x_voxel=x_voxel, y_voxel=y_voxel, z_voxel=z_voxel,
                           x_dim=x_dim, y_dim=y_dim, z_dim=z_dim, BinInDir=BinInDir, MV3DOutDir=MV3DOutDir,
                           BinInID=BinInID, MV3DOutID=MV3DOutID, chamferInterpret=chamferInterpret,
                           smooth_coeff=smooth_coeff, smooth_adhere=smooth_adhere, smooth_iter=smooth_iter,
                           len_list=len_list, islandsize=islandsize, saveProj=saveProj
                           )
    return conf


if len(sys.argv) < 2:
    sys.exit("Please provide at least one argument.")

config_choice = ask_choice('Which Amira script would you create a config file for? ', [
    ['Deconvolution', 0],
    ['Skeletonization', 1],
])

if config_choice == 0:
    conf = deconv_config(tm_deconv)
    conf_name = "deconv_config.tcl"
elif config_choice == 1:
    conf = skeleton_config(tm_skeleton)
    conf_name = "skeleton_config.tcl"
else:
    conf = None

conf_dir = input("Please provide the directory to store config file. ")
conf_dir = conf_dir.replace('"', '')
if not conf_dir.endswith(".tcl"):
    conf_dir = os.path.join(conf_dir, "deconv_config.tcl")

with open(str(conf_dir), 'w') as out:
    out.write(conf)

if sys.argv[1] == '-r' or sys.argv[1] == '--run':
    py_path = Path(sys.executable)
    while True:
        print("Searching for Amira executable...")
        try:
            if not [i for i in py_path.parent.rglob("Amira.exe")]:
                py_path = py_path.parent
            else:
                amira_exe = [i for i in py_path.parent.rglob("Amira.exe")][0]
                break
        except FileNotFoundError:
            amira_exe = input("Please provide the path to the Amira executable file. ")
            amira_exe = amira_exe.replace('"', '')
            amira_exe = Path(amira_exe)
    if not amira_exe or not os.access(str(amira_exe), os.X_OK):
        amira_exe = input("Please provide the path to the Amira executable file. ")
        amira_exe = amira_exe.replace('"', '')
        amira_exe = Path(amira_exe)
    else:
        print('amira.exe found')
    if config_choice == 0:
        hx_name = "Deconvolution.hx"
    elif config_choice == 1:
        hx_name = "Skeletonization.hx"
    hx_path = os.path.abspath(os.path.join(__file__, os.pardir, hx_name))
    if not os.path.exists(hx_path):
        hx_path = input("Please provide the path to the template {}. ".format(hx_path))
        hx_path = hx_path.replace('"', '')

    if sys.argv[2] == '-s' or sys.argv[2] == '--save':
        out_file = input("Please provide the path for saving the script file which will be used in Amira. ")
        out_file = out_file.replace('"', '')
        if not out_file.endswith(".hx"):
            out_file = os.path.join(out_file, hx_name)
    else:
        fd, path = tempfile.mkstemp()
        out_file = os.path.join(path, hx_name)
    with open(str(hx_path), 'r') as d:
        with open(str(out_file), 'w') as o:
            conf_dir = conf_dir.replace('\\', '/')
            lines = d.readlines()
            for l in lines:
                l = re.sub(r"source \[file normalize \{.*\}\]",
                           r"source [file normalize {" + str(conf_dir) + "}]", l)
                o.write(l)

    p = subprocess.Popen([str(amira_exe), "-no_gui", "-tclcmd", "source", str(out_file)],
                         stdout=subprocess.PIPE, universal_newlines=True)

    for stdout_line in iter(p.stdout.readline, ""):
        print(stdout_line)
    p.stdout.close()
    return_code = p.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code)

elif sys.argv[1] == '-mk' or sys.argv[1] == '--make':
    pass
