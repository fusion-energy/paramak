__doc__ = " This file creates a collarge of paramak images on a grid"

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
