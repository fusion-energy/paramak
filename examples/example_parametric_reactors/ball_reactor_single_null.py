"""
This example creates a single null ball reactor using the SingleNullBallReactor
parametric reactor. By default the script saves stp, stl, html and svg files.
"""

import paramak


def make_ball_reactor_sn(outputs=['stp', 'neutronics', 'svg', 'stl', 'html']):

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
        pf_coil_to_rear_blanket_radial_gap=50,
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=100,
        outboard_tf_coil_poloidal_thickness=50,
        divertor_position="lower"
    )

    if 'stp' in outputs:
        my_reactor.export_stp(output_folder='BallReactor_sn')
    if 'neutronics' in outputs:
        my_reactor.export_neutronics_description(
            'BallReactor_sn/manifest.json')
    if 'stl' in outputs:
        my_reactor.export_stl(output_folder='BallReactor_sn')
    if 'html' in outputs:
        my_reactor.export_html('BallReactor_sn/reactor.html')


if __name__ == "__main__":
    make_ball_reactor_sn(['stp', 'neutronics', 'svg', 'stl', 'html'])
