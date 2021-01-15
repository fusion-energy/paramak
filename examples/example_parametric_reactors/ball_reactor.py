"""
This example creates a ball reactor using the BallReactor parametric reactor.
By default the script saves stp, stl, html and svg files.
"""

from pathlib import Path

import paramak


def make_ball_reactor(outputs=('stp', 'neutronics', 'svg', 'stl', 'html'),
                      output_folder='BallReactor'):

    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=10,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=150,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=30,
        blanket_radial_thickness=50,
        blanket_rear_wall_radial_thickness=30,
        elongation=2,
        triangularity=0.55,
        number_of_tf_coils=16,
        rotation_angle=180,
        pf_coil_radial_thicknesses=[50, 50, 50, 50],
        pf_coil_vertical_thicknesses=[50, 50, 50, 50],
        pf_coil_to_rear_blanket_radial_gap=50,
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=100,
        outboard_tf_coil_poloidal_thickness=50
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
    make_ball_reactor(('stp', 'neutronics', 'svg', 'stl', 'html'))
