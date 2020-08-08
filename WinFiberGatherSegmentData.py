import os
import re
import csv

from sys import argv
from pathlib import Path

try:
    input_path = Path(sys.argv[1])
except IndexError:
    input_path = input('Please provide the path to the xlsx files which where exported from WinFiber3D. ')
    input_path = Path(input_path)

try:
    output_path = Path(sys.argv[2])
except IndexError:
    output_path = input('Please provide the path where the exported files will be saved. ')
    output_path = Path(output_path)


out_xy = os.path.join(output_path, "SegmentData_angle_prx.csv")
data_xy = []
out_xy_3D = os.path.join(output_path, "SegmentData_angle_x.csv")
data_xy_3D = []
out_z = os.path.join(output_path, "SegmentData_angle_z.csv")
data_z = []
out_length = os.path.join(output_path, "SegmentData_length.csv")
data_length = []
out_diameter = os.path.join(output_path, "SegmentData_diameter.csv")
data_diameter = []


i = 0
for root, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith(".xls"):
            loops_match = re.findall(r'loops_(\w*)', file, re.IGNORECASE)
            len_of_ends = re.findall(r'len_(\d*)', file, re.IGNORECASE)[0]
            if not loops_match:
                loops = "not removed"
            else:
                loops = "removed"
            with open(os.path.join(root, file), 'r', encoding = "utf-8") as f:
                segment_count = []
                orient_xy = []
                orient_xy_3D = []
                orient_z_3D = []
                length = []
                segment_diameter = []
                content = f.read()
                for line in content.splitlines():
                    splitter = line.split()
                    if len(splitter) == 6:
                        if not line.startswith('#'):
                            segment_count.append(splitter[0])
                            orient_xy.append(splitter[1])
                            orient_xy_3D.append(splitter[2])
                            orient_z_3D.append(splitter[3])
                            length.append(splitter[4])
                            segment_diameter.append(splitter[5])
                        else:
                            continue
                data_xy.append([file, loops,len_of_ends])
                data_xy_3D.append([file, loops,len_of_ends])
                data_z.append([file, loops,len_of_ends])
                data_length.append([file, loops,len_of_ends])
                data_diameter.append([file, loops,len_of_ends])

                data_xy[i].extend([no for no in orient_xy])
                data_xy_3D[i].extend([no for no in orient_xy_3D])
                data_z[i].extend([no for no in orient_z_3D])
                data_length[i].extend([no for no in length])
                data_diameter[i].extend([no for no in segment_diameter])
                i += 1

collect = []
for entry in data_xy:
    collect.append(len(entry))
fieldnames = ["sample", "loops", "len_of_ends"]
for x in range(1, max(collect)+1):
    fieldnames.append(x)

with open(out_xy, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data_xy:
        for e in entry:
            out.write("%s," % e)
        out.write("\n")

collect = []
for entry in data_xy_3D:
    collect.append(len(entry))
for x in range(1, max(collect)+1):
    fieldnames.append(x)

with open(out_xy_3D, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data_xy_3D:
        for e in entry:
            out.write("%s," % e)
        out.write("\n")

collect = []
for entry in data_z:
    collect.append(len(entry))
for x in range(1, max(collect)+1):
    fieldnames.append(x)

with open(out_z, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data_z:
        for e in entry:
            out.write("%s," % e)
        out.write("\n")

collect = []
for entry in data_length:
    collect.append(len(entry))
for x in range(1, max(collect)+1):
    fieldnames.append(x)

with open(out_length, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data_length:
        for e in entry:
            out.write("%s," % e)
        out.write("\n")

collect = []
for entry in data_diameter:
    collect.append(len(entry))
for x in range(1, max(collect)+1):
    fieldnames.append(x)

with open(out_diameter, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data_diameter:
        for e in entry:
            out.write("%s," % e)
        out.write("\n")
