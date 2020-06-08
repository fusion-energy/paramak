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


__doc__ = """ Creates a series of images of a ball reactor images and
combines them into gif animations using the command line tool convert,
 part of the imagemagick suite """

import argparse
import os

import numpy as np
from tqdm import tqdm

from make_ball_reactor import make_reactor

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number_of_models", type=int, default=10)
args = parser.parse_args()

for i in tqdm(range(args.number_of_models)):

    myreactor = make_reactor(
        major_radius=np.random.uniform(300, 400),
        minor_radius=np.random.uniform(100, 200),
        triangularity=np.random.uniform(0.2, 0.4),
        blanket_thickness=np.random.uniform(10, 200),
        elongation=np.random.uniform(1.2, 1.7),
    )

    myreactor.export_2d_image(filename="output_for_animation_2d/" + str(i) + ".png")
    myreactor.export_3d_image(filename="output_for_animation_3d/" + str(i) + ".png")

    print(str(args.number_of_models), "models made")

os.system("convert -delay 40 output_for_animation_2d/*.png 2d.gif")
os.system("convert -delay 40 output_for_animation_3d/*.png 3d.gif")

print("animation file made 2d.gif and 3d.gif")
