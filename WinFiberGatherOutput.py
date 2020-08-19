import os
import re
import numpy
import csv
from sys import argv
from pathlib import Path

try:
    input_path = Path(sys.argv[1])
except IndexError:
    input_path = input('Please provide the path to the xlsx files which where exported from WinFiber3D. ')
    input_path = input_path.replace('"', '')
    input_path = Path(input_path)

try:
    output_path = Path(sys.argv[2])
except IndexError:
    output_path = input('Please provide the path where the exported files will be saved. ')
    output_path = input_path.replace('"', '')
    output_path = Path(output_path)

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
field_names = [
    'sample', 'loops', 'len_of_ends',
    'range_min', 'range_max',
    'total_vessel_no', 'total_branch_points', 'total_end_points',
    'average_branch_points_per_vessel', 'average_end_points_per_vessel',
    'total_volume_of_box', 'total_vessel_volume', 'volume_ratio',
    'total_vessel_length', 'average_vessel_length', 'average_diameter',
    'segment_count']

with open(os.path.join(output_path, "WinFiber_data.csv"), 'w', newline='') as out:  # open output file
    writer = csv.DictWriter(out, delimiter=',', fieldnames=field_names)
    writer.writeheader()
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith(".xls"):
                loops_match = re.findall(r'loops_(\w*)', file, re.IGNORECASE)
                len_of_ends = re.findall(r'len_(\d*)', file, re.IGNORECASE)[0]
                if not loops_match:
                    loops = "not removed"
                else:
                    loops = "removed"
                data_dict.update(
                    {
                        "sample": file,
                        "loops": loops,
                        "len_of_ends": len_of_ends
                    }
                )
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
                writer.writerow(data_dict)  # write dict to output file
