"""
This example creates a ball reactor using the BallReactor parametric shape
"""

import paramak

def main():
    
    my_reactor = paramak.BallReactor(major_radius=300,
                                    minor_radius=100,
                                    offset_from_plasma=20,
                                    blanket_thickness=100,
                                    center_column_shield_outer_radius=180,
                                    center_column_shield_inner_radius=120,
                                    number_of_tf_coils=16,
                                    number_of_pf_coils=5,
                                    pf_coil_height=20,
                                    pf_coil_width=20,
                                    pf_case_thickness=10,
                                    )

    my_reactor.export_stp()

    my_reactor.export_neutronics_description()


if __name__ == "__main__":
    main()
