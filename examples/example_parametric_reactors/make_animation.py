__doc__ = """ Creates a series of images of a ball reactor images and combines
them into gif animations using the command line tool convert, you will need to
have imagemagick installed to convert the svg images to a gif animation """

import os

import numpy as np
import paramak
from scipy.interpolate import interp1d


def rotate_single_reactor(number_of_images=10):
    """Makes a single reactor and exports and svg image with different view
    angles. Combines the svg images into a gif animation."""

    # allows the projection angle for the svg to be found via interpolation
    z_angle_finder = interp1d([0, number_of_images], [2, 15])
    x_angle_finder = interp1d([0, number_of_images], [-2, -3])

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

        # finds the z angle to use for the roation
        z_angle = z_angle_finder(i)
        x_angle = x_angle_finder(i)
        print('projectionDir=', x_angle, 1.1, z_angle)

        my_reactor.export_svg(
            filename="rotation_" + str(i).zfill(4) + ".svg",
            projectionDir=(x_angle, 1.1, z_angle)
        )

        print("made", str(i + 1), "models out of", str(number_of_images))

    os.system("convert -delay 40 output_for_rotated_svg/*.svg rotated.gif")

    print("animation file made as saved as rotated.gif")


def make_random_reactors(number_of_images=10):
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
            elongation=np.random.uniform(1.2, 1.7),
            triangularity=np.random.uniform(0.3, 0.55),
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
        )

        my_reactor.export_svg(
            filename="random_" + str(i).zfill(4) + ".svg",
            strokeWidth=6  # slightly thicker strokewidth than the default
        )

        print("made", str(i + 1), "models out of", str(number_of_images))

    os.system("convert -delay 40 output_for_random_svg/*.svg randoms.gif")

    print("animation file made as saved as randoms.gif")


if __name__ == "__main__":
    rotate_single_reactor()
    make_random_reactors()
