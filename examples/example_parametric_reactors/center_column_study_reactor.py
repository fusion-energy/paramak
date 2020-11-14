"""
This example creates a center column study reactor using a parametric reactor.
Adds some TF coils to the reactor. By default the script saves stp, stl,
html and svg files.
"""

import paramak


def make_center_column_study_reactor(
    outputs=[
        'stp',
        'neutronics',
        'svg',
        'stl',
        'html']):

    my_reactor = paramak.CenterColumnStudyReactor(
        inner_bore_radial_thickness=20,
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness_mid=50,
        center_column_shield_radial_thickness_upper=100,
        inboard_firstwall_radial_thickness=20,
        divertor_radial_thickness=100,
        inner_plasma_gap_radial_thickness=80,
        plasma_radial_thickness=200,
        outer_plasma_gap_radial_thickness=90,
        elongation=2.3,
        triangularity=0.45,
        plasma_gap_vertical_thickness=40,
        center_column_arc_vertical_thickness=520,
        rotation_angle=180)

    # adding in some TF coils
    tf_magnet = paramak.ToroidalFieldCoilPrincetonD(
        R1=20 + 50,
        R2=20 + 50 + 50 + 80 + 200 + 90 + 100 + 20,
        thickness=50,
        distance=50,
        number_of_coils=12,
        rotation_angle=180
    )

    my_reactor.shapes_and_components.append(tf_magnet)

    if 'stp' in outputs:
        my_reactor.export_stp(output_folder='CenterColumnStudyReactor')
    if 'neutronics' in outputs:
        my_reactor.export_neutronics_description(
            'CenterColumnStudyReactor/manifest.json')
    if 'stl' in outputs:
        my_reactor.export_stl(output_folder='CenterColumnStudyReactor')
    if 'html' in outputs:
        my_reactor.export_html('CenterColumnStudyReactor/reactor.html')


if __name__ == "__main__":
    make_center_column_study_reactor()
