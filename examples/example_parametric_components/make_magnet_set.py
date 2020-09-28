
"""
This script makes a blanket and then segments it in a similar
manner to the EU DEMO segmentation for remote maintainance.
"""

import math
import numpy as np
import paramak


def main():

    number_of_toroidal_field_coils = 8
    angle_offset = (360 / number_of_toroidal_field_coils) / 2.
    tf_coil_thickness = 50
    tf_coil_distance = 130

    inner_tf_case = paramak.InnerTfCoilsFlat(
        height=1800,
        inner_radius=330,
        outer_radius=430,
        number_of_coils=number_of_toroidal_field_coils,
        gap_size=5,
        rotation_angle=180,
        azimuth_start_angle=angle_offset
    )

    tf_coils = paramak.ToroidalFieldCoilPrincetonD(
        R1=400,
        R2=1500,  # height
        thickness=tf_coil_thickness,
        distance=tf_coil_distance,
        number_of_coils=number_of_toroidal_field_coils,
        rotation_angle=180,
    )

    pf_coils = paramak.PoloidalFieldCoilSet(
        heights=[100, 120, 80, 80, 120, 180],
        widths=[100, 120, 80, 80, 120, 180],
        center_points=[(530, 930), (1370, 790), (1740, 250), (1750, -250), (1360, -780), (680, -1000)],
        rotation_angle=180
    )

    pf_coils_casing = paramak.PoloidalFieldCoilCaseSetFC(
        pf_coils=pf_coils,
        casing_thicknesses=[10] * 6,
        rotation_angle=180
    )

    pf_coils.export_stp('pf_coils.stp')
    pf_coils_casing.export_stp('pf_coils_case.stp')

    tf_coils.export_stp('tf_coil.stp')
    inner_tf_case.export_stp('inner_tf_case.stp')


if __name__ == "__main__":
    main()
