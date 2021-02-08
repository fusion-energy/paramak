__doc__ = """ Creates a series of images of a ball reactor images and combines
them into gif animations using the command line tool convert, you will need to
have imagemagick installed to convert the svg images to a gif animation """

import os

import numpy as np
import paramak
from scipy.interpolate import interp1d


def rotate_single_reactor(number_of_images=100):
    """Makes a single reactor and exports and svg image with different view
    angles. Combines the svg images into a gif animation."""

    # allows the projection angle for the svg to be found via interpolation
    angle_finder = interp1d([0, number_of_images], [2.4021, 6.])

    my_reactor = paramak.SubmersionTokamak(
        inner_bore_radial_thickness=30,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=30,
        divertor_radial_thickness=80,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=200,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=30,
        blanket_rear_wall_radial_thickness=30,
        number_of_tf_coils=16,
        rotation_angle=180,
        support_radial_thickness=90,
        inboard_blanket_radial_thickness=30,
        outboard_blanket_radial_thickness=30,
        elongation=2.00,
        triangularity=0.50,
        pf_coil_radial_thicknesses=[30, 30, 30, 30],
        pf_coil_vertical_thicknesses=[30, 30, 30, 30],
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=30,
        outboard_tf_coil_poloidal_thickness=30,
        tf_coil_to_rear_blanket_radial_gap=20,
    )

    for i in range(number_of_images):

        # uses the rotation angle (in radians) to find new x, y points
        x_vec, y_vec = paramak.utils.rotate([0, 0], [1, 0], angle_finder(i))
        projectionDir = (x_vec, y_vec, 0)

        my_reactor.export_svg(
            filename="rotation_" + str(i).zfill(4) + ".svg",
            projectionDir=projectionDir,
            showHidden=False,
            height=200,
            width=300,
            marginTop=27,
            marginLeft=35,
            strokeWidth=3.5
        )

        print("made", str(i + 1), "models out of", str(number_of_images))

    os.system("convert -delay 15 rotation_*.svg rotated.gif")

    print("animation file made as saved as rotated.gif")


def make_random_reactors(number_of_images=11):
    """Makes a series of random sized reactors and exports an svg image for
    each one. Combines the svg images into a gif animation."""

    # makes a series of reactor models
    for i in range(number_of_images):

        my_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=np.random.uniform(20, 50),
            center_column_shield_radial_thickness=np.random.uniform(20, 60),
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=50,
            plasma_radial_thickness=np.random.uniform(20, 200),
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=5,
            blanket_radial_thickness=np.random.uniform(10, 200),
            blanket_rear_wall_radial_thickness=10,
            elongation=np.random.uniform(1.3, 1.7),
            triangularity=np.random.uniform(0.3, 0.55),
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[30, 30, 30, 30],
            pf_coil_to_rear_blanket_radial_gap=20,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
        )

        my_reactor.export_svg(
            filename="random_" + str(i).zfill(4) + ".svg",
            showHidden=False
        )

        print("made", str(i + 1), "models out of", str(number_of_images))

    os.system("convert -delay 40 random_*.svg randoms.gif")

    print("animation file made as saved as randoms.gif")


if __name__ == "__main__":
    rotate_single_reactor()
    # make_random_reactors()
