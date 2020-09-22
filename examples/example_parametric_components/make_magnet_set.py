
"""
This script makes a blanket and then segments it in a similar
manner to the EU DEMO segmentation for remote maintainance.
"""

import math
import numpy as np
import paramak


def main():

    number_of_toroidal_field_coils = 5
    angle_offset = (360 / number_of_toroidal_field_coils) / 2.
    inner_tf = paramak.InnerTfCoilsFlat(
        height=1800,
        inner_radius=330,
        outer_radius=430,
        number_of_coils=number_of_toroidal_field_coils,
        gap_size=5,
    )

    outer_tf = paramak.ToroidalFieldCoilPrincetonD(
        R1=410,
        R2=1500,  # height
        thickness=50,
        distance=130,
        number_of_coils=number_of_toroidal_field_coils,
        azimuth_placement_angle=np.linspace(
            0 + angle_offset, 360 + angle_offset,
            number_of_toroidal_field_coils,
            endpoint=False
        )
    )

    pf_coil1 = paramak.PoloidalFieldCoil(
        height=120,
        width=120,
        center_point=(530, 930),
        rotation_angle=180
    )

    pf_coil2 = paramak.PoloidalFieldCoil(
        height=140,
        width=140,
        center_point=(1370, 790),
        rotation_angle=180
    )

    pf_coil3 = paramak.PoloidalFieldCoil(
        height=100,
        width=100,
        center_point=(1740, 250),
        rotation_angle=180
    )

    pf_coil4 = paramak.PoloidalFieldCoil(
        height=100,
        width=100,
        center_point=(1750, -250),
        rotation_angle=180
    )

    pf_coil5 = paramak.PoloidalFieldCoil(
        height=140,
        width=140,
        center_point=(1360, -780),
        rotation_angle=180
    )

    pf_coil6 = paramak.PoloidalFieldCoil(
        height=200,
        width=200,
        center_point=(680, -1000),
        rotation_angle=180
    )

    pf_coil1.export_stp('pf_coil1.stp')
    pf_coil2.export_stp('pf_coil2.stp')
    pf_coil3.export_stp('pf_coil3.stp')
    pf_coil4.export_stp('pf_coil4.stp')
    pf_coil5.export_stp('pf_coil5.stp')
    pf_coil6.export_stp('pf_coil6.stp')
    outer_tf.export_stp('outer_tf.stp')
    inner_tf.export_stp('inner_tf.stp')


if __name__ == "__main__":
    main()
