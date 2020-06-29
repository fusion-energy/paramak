
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
# convert -coalesce -repage 0x0 -gravity Center -crop 300x250+0+0 +repage -delay 40 output_for_animation_3d/*.png 3d.gif

os.system("convert 3d.gif -coalesce -repage 0x0 -gravity Center -crop 300x250+0+0 +repage -delay 40 output_for_animation_3d/*.png 3d.gif")

print("animation file made 2d.gif and 3d.gif")
