"""
This file is part of PARAMAK which is a design tool capable 
of creating 3D CAD models compatible with automated neutronics 
analysis.

PARAMAK is released under GNU General Public License v3.0. 
Go to https://github.com/Shimwell/paramak/blob/master/LICENSE 
for full license details.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Copyright (C) 2019  UKAEA

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""

" This file creates a collarge of paramak images on a grid"

import argparse
import math
import os

import numpy as np

from make_ball_reactor import make_reactor

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number_of_models", type=int, default=10)
args = parser.parse_args()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


def write_file(n):
    list_of_image_rows = list(divide_chunks(files_found, n))

    all_lines = []
    for entry in list_of_image_rows:
        all_lines.append(" ".join(entry))

    file_lines = []
    for i in range(n):
        file_lines.append(all_lines[i])

    file_lines[0] = "convert &( " + file_lines[0] + " +append  &) &"
    for i in range(1, n):
        file_lines[i] = "          &( " + file_lines[i] + " +append  &) &"

    file_lines.append("           &( -size 32x32 xc:none   +append &) &")
    file_lines.append(
        "           -background none -append   paramak_array" + str(n) + ".svg"
    )

    with open("output_collarge/combine_images" + str(n) + ".sh", "w") as f:
        for item in file_lines:
            item = item.replace("&", "\\")
            f.write("%s\n" % item)
    cwd = os.getcwd()
    os.chdir("output_collarge")
    os.system("bash combine_images" + str(n) + ".sh")
    os.chdir(cwd)


# generates n random reactors
for i in range(args.number_of_models):

    my_reactor = make_reactor(
        major_radius=np.random.uniform(300, 400),
        minor_radius=np.random.uniform(100, 200),
        triangularity=np.random.uniform(0.2, 0.4),
        blanket_thickness=np.random.uniform(10, 200),
        elongation=np.random.uniform(1.2, 1.7),
    )
    my_reactor.export_3d_image("output_collarge/" + str(i) + str(".png"))


files_found = [
    pos_json for pos_json in os.listdir("output_collarge") if pos_json.endswith(".png")
]

for i in range(1, math.floor(math.sqrt(len(files_found)))):
    print("making grid of ", i * i, "images")
    write_file(i)
