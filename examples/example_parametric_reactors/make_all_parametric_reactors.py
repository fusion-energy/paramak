"""
This python script demonstrates the creation of all parametric reactors available
in the paramak tool
"""

import paramak

def main():

    rot_angle = 180
    all_reactors = []

    my_reactor = paramak.BallReactor(
                                    inner_bore_radial_thickness=50,
                                    inboard_tf_leg_radial_thickness = 50,
                                    center_column_shield_radial_thickness= 50,
                                    divertor_radial_thickness = 100,
                                    inner_plasma_gap_radial_thickness = 50,
                                    plasma_radial_thickness = 200,
                                    outer_plasma_gap_radial_thickness = 50,
                                    firstwall_radial_thickness=50,
                                    blanket_radial_thickness=100,
                                    blanket_rear_wall_radial_thickness=50,
                                    elongation=2,
                                    triangularity=0.55,
                                    number_of_tf_coils=16,
                                    rotation_angle=180
    )
    my_reactor.name = 'BallReactor'
    all_reactors.append(my_reactor)

    return all_reactors

if __name__ == "__main__":
    all_reactors = main()
    for reactors in all_reactors:
        reactors.export_stp()
