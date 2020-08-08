import os
import psutil
import subprocess
import time
import pyautogui
from pathlib import Path
from sys import argv
import logging

pyautogui.PAUSE = 2
pyautogui.FAILSAFE = True


def ask_choice(question, options):
    while True:
        raw_input = None
        print('\n' + question)
        for n, option in enumerate(options):
            print('\t{}: {}'.format(n+1, option[0]))

        try:
            raw_input = input('Your choice: ')
            value = int(raw_input)
            if len(options) >= value > 0:
                break
            else:
                print('Please try again - {} is not a valid choice. '.format(raw_input))
        except ValueError:
            print('Please try again - {} is not a number. '.format(raw_input))
    return options[value-1][1]


def checkIfProcessRunning(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def isresponding(name):
    os.system('tasklist /FI "IMAGENAME eq %s" /FI "STATUS eq running" > tmp.txt' % name)
    tmp = open('tmp.txt', 'r')
    a = tmp.readlines()
    tmp.close()
    if a[-1].split()[0] == name:
        return True
    else:
        return False


def WinFiberOpen(input_name):
    pyautogui.hotkey('ctrl', 'o')
    pyautogui.typewrite(input_name)
    pyautogui.press('enter')


def WinFiberZoom():
    pyautogui.moveTo(800, 150)
    pyautogui.drag(0, 5, 1, button='right')


def WinFiberZoom2():
    pyautogui.moveTo(800, 150)
    pyautogui.drag(0, 750, 3, button='right')


def WinFiberScreenshot(output_name):
    img = pyautogui.screenshot()
    try:
        img.save(output_name)
    except (IOError, PermissionError):
        time.sleep(120)
        pass


def WinFiberMoveZ():
    pyautogui.moveTo(450, 815)
    pyautogui.dragTo(500, 675, 3, button="left")


def WinFiberSetup():
    pyautogui.click(1694, 720)  # untick shadows
    pyautogui.click(1780, 639)  # color vessels
    pyautogui.click(1828, 690)  # color vessels


def WinFiberExport(out):
    pyautogui.hotkey('ctrl', 's')
    pyautogui.typewrite(out)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('space')
    pyautogui.press('tab')
    pyautogui.press('space')
    pyautogui.press('tab')
    pyautogui.press('space')
    pyautogui.press('enter')


def WinFiberRemoveLoops(output_name):
    pyautogui.click(80, 76)
    pyautogui.click(93, 107)
    time.sleep(30)
    img = pyautogui.screenshot()
    try:
        img.save(output_name)
    except(IOError, PermissionError):
        time.sleep(120)
        pass
    time.sleep(5)
    pyautogui.press('enter')


def checkDir(direct):
    try:
        if not os.path.isdir(direct):
            os.makedirs(direct)
    except PermissionError:
        time.sleep(120)
        pass


def open_program(path_name):
    return subprocess.Popen(path_name)


def close_program(p):
    p.terminate()


try:
    winfiber_path = Path(sys.argv[1])
except IndexError:
    winfiber_path = input('Please provide the path to the WinFiber3D executable. ')
    winfiber_path = Path(winfiber_path)

try:
    input_path = Path(sys.argv[2])
except IndexError:
    input_path = input('Please provide the path to the mv3d files. ')
    input_path = Path(input_path)

try:
    output_path = Path(sys.argv[3])
except IndexError:
    output_path = input('Please provide the path where the exported files will be saved. ')
    output_path = Path(output_path)

log_file = os.path.join(output_path, "Log.txt")
logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s >> %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

logging.info('Start binarization script')
logging.info('Preferences')
logging.info('    WinFiber3D dir: %s', winfiber_path)
logging.info('    Input dir: %s', input_path)
logging.info('    Output dir: %s', output_path)


problem_list = []
with open(log_file, 'r') as f:
    temp = [line.strip() for line in f.readlines()]
    for n in temp:
        if n.startswith('    File not processed:'):
            problem_list.append(n.split(":")[1])

p = open_program(winfiber_path)
time.sleep(10)
pyautogui.hotkey('win', 'up')
x = 0
for root, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith(".mv3d"):
            input_file = os.path.join(root, file)
            try:
                base_name = file.split("_skeletonize")[0]
            except IndexError:
                base_name = input_file
            len_no = int(root.split("len_")[1])

            export_dir_out = os.path.join(base_dir_output, "len_" + str(len_no))
            checkDir(export_dir_out)
            screenshot_dir_out = os.path.join(export_dir_out, "len_" + str(len_no), "screenshots")
            checkDir(screenshot_dir_out)
            loopremoval_dir_out = os.path.join(screenshot_dir_out, "loop-removal")
            checkDir(loopremoval_dir_out)

            screenshot_file_xy = base_name + "-len_" + str(len_no) + "_XY.png"
            screenshot_file_z = base_name + "-len_" + str(len_no) + "_Z.png"
            screenshot_file_loop = base_name + "-len_" + str(len_no) + "_looprem.png"
            export_file_wloops = base_name + "-len_" + str(len_no) + ".xls"
            export_file_loops_removed = base_name + "-len_" + str(len_no) + "_loops_removed.xls"
            if not os.path.exists(os.path.join(export_dir_out, export_file_loops_removed)):
                if input_file not in problem_list:
                    try:
                        WinFiberOpen(input_file)
                        time.sleep(30)
                        x += 1
                        if isresponding("WinFiber.exe"):
                            if x == 1:
                                WinFiberSetup()
                            else:
                                time.sleep(1)
                            if len_no == 2:
                                WinFiberZoom2()
                            else:
                                WinFiberZoom()
                            WinFiberScreenshot(os.path.join(screenshot_dir_out, screenshot_file_xy))  # XY screenshot
                            WinFiberMoveZ()
                            WinFiberScreenshot(os.path.join(screenshot_dir_out, screenshot_file_z))  # z screenshot
                            WinFiberExport(os.path.join(export_dir_out, export_file_wloops))
                            WinFiberRemoveLoops(os.path.join(loopremoval_dir_out, screenshot_file_loop))
                            WinFiberExport(os.path.join(export_dir_out, export_file_loops_removed))
                        else:
                            time.sleep(10)
                            logging.info('    File not processed', input_file)
                            problem_list.append(input_file)
                            time.sleep(3)
                            p.kill()
                            time.sleep(20)
                            p = open_program(winfiber_path)
                            time.sleep(15)
                            pyautogui.hotkey('win', 'up')
                            x = 0
                            continue
                    except:
                        time.sleep(120)
                        pass

time.sleep(60)
close_program(p)
