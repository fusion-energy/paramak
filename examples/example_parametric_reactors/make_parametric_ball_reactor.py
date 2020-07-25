"""
This example creates a ball reactor using the BallReactor parametric shape
"""

import paramak

def main():


    for blanket_radial_thickness in [10, 75, 150, 300]:

        my_reactor = paramak.BallReactor(
                                            inner_bore_radial_thickness=1,
                                            inboard_tf_leg_radial_thickness = 30,
                                            center_column_shield_radial_thickness= 60,
                                            divertor_radial_thickness=50,
                                            inner_plasma_gap_radial_thickness = 30,
                                            plasma_radial_thickness = 300,
                                            outer_plasma_gap_radial_thickness = 30,
                                            firstwall_radial_thickness=3,
                                            blanket_radial_thickness=blanket_radial_thickness,
                                            blanket_rear_wall_radial_thickness=3,
                                            elongation=2.75,
                                            triangularity=0.5,
                                            number_of_tf_coils=16,
                                            rotation_angle=180)

        my_reactor.export_stp(str(blanket_radial_thickness))

        # my_reactor.export_neutronics_description()


if __name__ == "__main__":
    main()
