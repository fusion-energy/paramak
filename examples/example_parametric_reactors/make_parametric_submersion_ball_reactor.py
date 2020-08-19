"""
This example creates a submersion ball reactor using the SubmersionBallReactor
parametric shape
"""

import paramak


def main():

    my_reactor = paramak.SubmersionBallReactor(
        major_radius=300,
        minor_radius=100,
        offset_from_plasma=20,
        blanket_thickness=150,
        firstwall_thickness=10,
        center_column_shield_outer_radius=160,
        center_column_shield_inner_radius=100,
        number_of_tf_coils=16,
        casing_thickness=10,
    )

    my_reactor.export_stp()

    my_reactor.export_neutronics_description()


if __name__ == "__main__":
    main()
