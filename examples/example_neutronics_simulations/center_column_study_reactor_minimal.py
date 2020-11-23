"""This is a minimal example that obtains the center column heating for a
parametric reactor."""

import paramak


def make_model_and_simulate():
    """Makes a neutronics Reactor model and simulates the heat deposition"""

    # makes the 3d geometry
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
        plasma_high_point=(245, 240),
        plasma_gap_vertical_thickness=40,
        center_column_arc_vertical_thickness=520,
        rotation_angle=360
    )

    # creates a neutronics model from the geometry and assigned materials
    neutronics_model = paramak.NeutronicsModelFromReactor(
        reactor=my_reactor,
        materials={
            'inboard_tf_coils_mat': 'eurofer',
            'center_column_shield_mat': 'eurofer',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_mat': 'Li4SiO4'},
        cell_tallies=['heating'],
        simulation_batches=5,
        simulation_particles_per_batch=1e4,
    )

    # starts the neutronics simulation
    neutronics_model.simulate(method='trelis')

    # prints the results
    print(neutronics_model.results)


if __name__ == "__main__":
    make_model_and_simulate()
