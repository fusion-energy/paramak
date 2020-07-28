
__doc__ = """ Creates a series of images of a ball reactor images and
combines them into gif animations using the command line tool convert,
 part of the imagemagick suite """

import argparse
import os
import uuid

import numpy as np
from tqdm import tqdm

import paramak

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number_of_models", type=int, default=10)
args = parser.parse_args()

for i in tqdm(range(args.number_of_models)):


    my_reactor = paramak.BallReactor(
                                    inner_bore_radial_thickness=50,
                                    inboard_tf_leg_radial_thickness = 200,
                                    center_column_shield_radial_thickness= 50,
                                    divertor_radial_thickness=50,
                                    inner_plasma_gap_radial_thickness = 50,
                                    plasma_radial_thickness = np.random.uniform(20, 200),
                                    outer_plasma_gap_radial_thickness = 50,
                                    firstwall_radial_thickness=5,
                                    blanket_radial_thickness=np.random.uniform(10, 200),
                                    blanket_rear_wall_radial_thickness=10,
                                    elongation=np.random.uniform(1.2, 1.7),
                                    triangularity=np.random.uniform(0.2, 0.4),
                                    number_of_tf_coils=16,
                                    rotation_angle=180
    )

    my_reactor.export_2d_image(filename="output_for_animation_2d/" + str(uuid.uuid4()) + ".png")
    my_reactor.export_svg(filename="output_for_animation_svg/" + str(uuid.uuid4()) + ".svg")
    my_reactor.export_3d_image(filename="output_for_animation_3d/" + str(uuid.uuid4()) + ".png")

    print(str(args.number_of_models), "models made")

os.system("convert -delay 40 output_for_animation_2d/*.png 2d.gif")

os.system("convert -delay 40 output_for_animation_3d/*.png 3d.gif")

os.system("convert -delay 40 output_for_animation_svg/*.svg 3d_svg.gif")

print("animation file made 2d.gif, 3d.gif and 3d_svg.gif")
