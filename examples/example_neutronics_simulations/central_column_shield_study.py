
"""
Example which creates a simple neutronics model using the CenterColumnStudyReactor
and finds the neutron spectra and current for different configurations
"""

import os

import openmc
from neutronics_material_maker import Material

import paramak
import uuid
from skopt import dummy_minimize  # available via pip install scikit-optimize


def make_cad_model_with_paramak(params):

    inner_bore_radial_thickness = params[0]
    inboard_tf_leg_radial_thickness = params[1]
    center_column_shield_radial_thickness_mid = params[2]
    center_column_shield_radial_thickness_upper = params[3] * params[2]
    inboard_firstwall_radial_thickness = params[4]
    inner_plasma_gap_radial_thickness = params[5]
    divertor_radial_thickness = params[6]
    plasma_radial_thickness = params[7]
    outer_plasma_gap_radial_thickness = params[8]
    plasma_gap_vertical_thickness= params[9]
    center_column_arc_vertical_thickness= params[10]

    plasma_high_point_y = params[11]
    
    # plasma_high_point_x_factor is param[12]
    plasma_high_point_x = (params[7] * params[12]) + sum(params[0:6])
    plasma_high_point=(plasma_high_point_x, plasma_high_point_y) 

    print(params)

    test_reactor = paramak.CenterColumnStudyReactor(
        inner_bore_radial_thickness=inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness_mid=center_column_shield_radial_thickness_mid,
        center_column_shield_radial_thickness_upper=center_column_shield_radial_thickness_upper,
        inboard_firstwall_radial_thickness=inboard_firstwall_radial_thickness,
        inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
        divertor_radial_thickness=divertor_radial_thickness,
        plasma_radial_thickness=plasma_radial_thickness,
        outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
        plasma_gap_vertical_thickness=plasma_gap_vertical_thickness,
        center_column_arc_vertical_thickness=center_column_arc_vertical_thickness,
        plasma_high_point=plasma_high_point,
        rotation_angle=180)
    test_reactor.export_svg(str(uuid.uuid4()) +'.png')
    test_reactor.export_stp(output_folder= str(uuid.uuid4()))

    return 1.



if __name__ == "__main__":
    res = dummy_minimize(make_cad_model_with_paramak,
                    [
                        (10., 50.),  # inner_bore_radial_thickness 
                        (50., 100.),  # inboard_tf_leg_radial_thickness 
                        (10., 150.),  # center_column_shield_radial_thickness_mid 
                        (1., 1.5),  # center_column_shield_radial_thickness_upper 
                        (2., 10.),  # inboard_firstwall_radial_thickness 
                        (2., 20.),  # inner_plasma_gap_radial_thickness 
                        (20., 50.),  # divertor_radial_thickness 
                        (100., 300.),  # plasma_radial_thickness 
                        (2., 20.),  # outer_plasma_gap_radial_thickness 
                        (2., 20.),  # plasma_gap_vertical_thickness
                        (200., 500.),  # center_column_arc_vertical_thickness
                        (200., 500.),  # plasma_high_point_y
                        (0.,1.),  # plasma_high_point_x_factor
                    ],
                    n_calls = 20 # this can be increased to perform more samples
                    )
