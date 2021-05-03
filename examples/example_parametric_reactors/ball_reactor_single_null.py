"""
This example creates a single null ball reactor using the SingleNullBallReactor
parametric reactor. By default the script saves stp, stl, html and svg files.
"""

from pathlib import Path

import paramak


def make_ball_reactor_sn(outputs=['stp', 'neutronics', 'svg', 'stl', 'html'],
                         output_folder='BallReactor_sn'):

    my_reactor = paramak.SingleNullBallReactor(
        inner_bore_radial_thickness=50,
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness=50,
        divertor_radial_thickness=90,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=200,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=50,
        blanket_radial_thickness=100,
        blanket_rear_wall_radial_thickness=50,
        elongation=2,
        triangularity=0.55,
        number_of_tf_coils=16,
        rotation_angle=180,
        pf_coil_radial_thicknesses=[50, 50, 50, 50],
        pf_coil_vertical_thicknesses=[50, 50, 50, 50],
        rear_blanket_to_tf_gap=50,
        outboard_tf_coil_radial_thickness=100,
        outboard_tf_coil_poloidal_thickness=50,
        divertor_position="lower"
    )

    if 'stp' in outputs:
        my_reactor.export_stp(output_folder=output_folder)
    if 'neutronics' in outputs:
        my_reactor.export_neutronics_description(
            Path(output_folder) / 'manifest.json')
    if 'svg' in outputs:
        my_reactor.export_svg(Path(output_folder) / 'reactor.svg')
    if 'stl' in outputs:
        my_reactor.export_stl(output_folder=output_folder)
    if 'html' in outputs:
        my_reactor.export_html(Path(output_folder) / 'reactor.html')


if __name__ == "__main__":
    make_ball_reactor_sn(['stp', 'neutronics', 'svg', 'stl', 'html'])
