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
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness=50,
        divertor_radial_thickness=100,
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
    )
    my_reactor.name = "BallReactor"
    all_reactors.append(my_reactor)

    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=50,
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness=50,
        divertor_radial_thickness=100,
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
        tf_coil_poloidal_thickness=50,
    )
    my_reactor.name = "BallReactor_with_pf_tf_coils"
    all_reactors.append(my_reactor)

    my_reactor = paramak.SubmersionTokamak(
        inner_bore_radial_thickness=25,
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness=50,
        inboard_blanket_radial_thickness=50,
        firstwall_radial_thickness=50,
        inner_plasma_gap_radial_thickness=70,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=70,
        outboard_blanket_radial_thickness=200,
        blanket_rear_wall_radial_thickness=50,
        divertor_radial_thickness=50,
        plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
        rotation_angle=180,
        support_radial_thickness=150,
        outboard_tf_coil_radial_thickness=50,
    )

    my_reactor.name = "SubmersionTokamak"
    all_reactors.append(my_reactor)

    my_reactor = paramak.SubmersionTokamak(
        inner_bore_radial_thickness=25,
        inboard_tf_leg_radial_thickness=50,
        center_column_shield_radial_thickness=50,
        inboard_blanket_radial_thickness=50,
        firstwall_radial_thickness=50,
        inner_plasma_gap_radial_thickness=70,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=70,
        outboard_blanket_radial_thickness=200,
        blanket_rear_wall_radial_thickness=50,
        divertor_radial_thickness=50,
        plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
        rotation_angle=180,
        support_radial_thickness=150,
        outboard_tf_coil_radial_thickness=50,
        tf_coil_to_rear_blanket_radial_gap=50,
        tf_coil_poloidal_thickness=70,
        pf_coil_vertical_thicknesses=[50, 50, 50, 50, 50],
        pf_coil_radial_thicknesses=[40, 40, 40, 40, 40],
        pf_coil_to_tf_coil_radial_gap=50,
        number_of_tf_coils=16,
    )

    my_reactor.name = "SubmersionTokamak_with_pf_tf_coils"
    all_reactors.append(my_reactor)

    my_reactor = paramak.SingleNullSubmersionTokamak(
        inner_bore_radial_thickness=10,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=30,
        blanket_rear_wall_radial_thickness=30,
        number_of_tf_coils=16,
        rotation_angle=180,
        support_radial_thickness=20,
        inboard_blanket_radial_thickness=20,
        outboard_blanket_radial_thickness=20,
        plasma_high_point=(200, 200),
        divertor_position="upper",
        support_position="upper"
    )

    my_reactor.name = "SingleNullSubmersionTokamak"
    all_reactors.append(my_reactor)

    my_reactor = paramak.SingleNullSubmersionTokamak(
        inner_bore_radial_thickness=10,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=30,
        blanket_rear_wall_radial_thickness=30,
        number_of_tf_coils=16,
        rotation_angle=180,
        support_radial_thickness=20,
        inboard_blanket_radial_thickness=20,
        outboard_blanket_radial_thickness=20,
        plasma_high_point=(200, 200),
        pf_coil_radial_thicknesses=[50, 50, 50, 50],
        pf_coil_vertical_thicknesses=[50, 50, 50, 50],
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=100,
        tf_coil_poloidal_thickness=50,
        tf_coil_to_rear_blanket_radial_gap=20,
        divertor_position="upper",
        support_position="upper"
    )

    my_reactor.name = "SingleNullSubmersionTokamak_with_pf_tf_coils"
    all_reactors.append(my_reactor)

    return all_reactors


if __name__ == "__main__":
    all_reactors = main()
    for reactors in all_reactors:

        reactors.export_stp(reactors.name)
        reactors.export_stl(reactors.name)
        reactors.export_neutronics_description()
