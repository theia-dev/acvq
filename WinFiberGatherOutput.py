import os
import re
import numpy
import csv
import sys
from pathlib import Path


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


def ask_dir(dir, str):
    if not os.path.isdir(dir):
        while True:
            makedir = ask_choice('This path does not exist. Would you like to create it?', [
                ['yes', True],
                ['no', False],
            ])
            if makedir:
                os.makedirs(dir)
                break
            else:
                dir = input(str)


try:
    input_path = Path(sys.argv[1])
except IndexError:
    input_path = input('Please provide the path to the xlsx files which where exported from WinFiber3D. ')
    input_path = input_path.replace('"', '')
    input_path = Path(input_path)
if not os.path.isdir(input_path):
    while True:
        input_path = input(
            "This dir doesn't seem to exist. Please check your input. ")
        input_path = input_path.replace('"', '')
        input_path = Path(input_path)

try:
    output_path = Path(sys.argv[2])
except IndexError:
    output_path = input('Please provide the path where the exported files will be saved. ')
    output_path = output_path.replace('"', '')
    output_path = Path(output_path)
ask_dir(output_path, 'Please provide the path where the exported files will be saved. ')

data_dict = {}
keyword_dict = {
    'range_min': '# Range min',
    'range_max': '# Range max',
    'total_vessel_no': '# Total vessels',
    'total_branch_points': '# Total branch points',
    'total_end_points': '# Total end points',
    'average_branch_points_per_vessel': '# Avg branch points per vessel',
    'average_end_points_per_vessel': '# Avg end points per vessel',
    'total_volume_of_box': '# Total volume of box',
    'total_vessel_volume': '# Total vessel volume',
    'volume_ratio': '# Volume ratio',
    'total_vessel_length': '# Total vessel length',
    'average_vessel_length': '# Average vessel length'}

for root, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith(".xls"):
            loops_match = re.findall(r'loops_(\w*)', file, re.IGNORECASE)
            try:
                len_of_ends = re.findall(r'len_(\d*)', file, re.IGNORECASE)[0]
            except IndexError:
                len_of_ends = None
            if not loops_match:
                loops = "not removed"
            else:
                loops = "removed"
            if len_of_ends:
                data_dict.update(
                    {
                        "sample": file,
                        "loops": loops,
                        "len_of_ends": len_of_ends
                    }
                )
                field_names = [
                    'sample', 'loops', 'len_of_ends',
                    'range_min', 'range_max',
                    'total_vessel_no', 'total_branch_points', 'total_end_points',
                    'average_branch_points_per_vessel', 'average_end_points_per_vessel',
                    'total_volume_of_box', 'total_vessel_volume', 'volume_ratio',
                    'total_vessel_length', 'average_vessel_length', 'average_diameter',
                    'segment_count']
            else:
                data_dict.update(
                    {
                        "sample": file,
                        "loops": loops
                    }
                )
                field_names = [
                    'sample', 'loops',
                    'range_min', 'range_max',
                    'total_vessel_no', 'total_branch_points', 'total_end_points',
                    'average_branch_points_per_vessel', 'average_end_points_per_vessel',
                    'total_volume_of_box', 'total_vessel_volume', 'volume_ratio',
                    'total_vessel_length', 'average_vessel_length', 'average_diameter',
                    'segment_count']

            with open(os.path.join(root, file), 'r', encoding="utf-8") as f:  # open the actual input file (xls)
                average_diam = []
                segment_count = []
                content = f.read()
                for line in content.splitlines():  # read input file line by line
                    for key, value in keyword_dict.items():
                        if line.startswith(value):
                            data_dict.update({
                                key: float(line.rpartition(":")[2])
                            })
                    splitter = line.split()  # split each entry line
                    if len(splitter) == 6:  # if there are 6 items per line, read average diameter and segment count
                        if not line.startswith('#'):
                            average_diam.append(splitter[5])
                            segment_count.append(splitter[0])
                        else:
                            continue
                average_diam = [float(entry) for entry in average_diam]
                average_vess_diameter = numpy.mean(average_diam)
                data_dict.update({
                    'average_diameter': average_vess_diameter,
                    'segment_count': len(segment_count)
                })
        with open(os.path.join(output_path, "WinFiber_data.csv"), 'w', newline='') as out:  # open output file
            writer = csv.DictWriter(out, delimiter=',', fieldnames=field_names)
            writer.writeheader()
            writer.writerow(data_dict)  # write dict to output file

print("\n Gathering WinFiber data finished.")
