"""
This example creates a submersion reactor using the SubmersionTokamak
parametric reactor. By default the script saves stp, stl, html and svg files.
"""

import paramak


def make_submersion(outputs=['stp', 'neutronics', 'svg', 'stl', 'html']):

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
        elongation=2.01,
        triangularity=0.51,
        pf_coil_radial_thicknesses=[30, 30, 30, 30],
        pf_coil_vertical_thicknesses=[30, 30, 30, 30],
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=30,
        outboard_tf_coil_poloidal_thickness=30,
        tf_coil_to_rear_blanket_radial_gap=20,
    )

    if 'stp' in outputs:
        my_reactor.export_stp(output_folder='SubmersionTokamak')
    if 'neutronics' in outputs:
        my_reactor.export_neutronics_description(
            'SubmersionTokamak/manifest.json')
    if 'svg' in outputs:
        my_reactor.export_svg('SubmersionTokamak/reactor.svg')
    if 'stl' in outputs:
        my_reactor.export_stl(output_folder='SubmersionTokamak')
    if 'html' in outputs:
        my_reactor.export_html('SubmersionTokamak/reactor.html')


if __name__ == "__main__":
    make_submersion(['stp', 'neutronics', 'svg', 'stl', 'html'])
