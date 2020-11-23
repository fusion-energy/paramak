"""This is a minimal example that obtains the TBR (Tritium Breeding Ratio)
for a parametric ball reactor"""

import paramak


def make_model_and_simulate():
    """Makes a neutronics Reactor model and simulates the TBR"""

    # makes the 3d geometry from input parameters
    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=50,
        inboard_tf_leg_radial_thickness=200,
        center_column_shield_radial_thickness=50,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=100,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=1,
        blanket_radial_thickness=100,
        blanket_rear_wall_radial_thickness=10,
        elongation=2,
        triangularity=0.55,
        number_of_tf_coils=16,
        rotation_angle=360,
    )

    # makes the neutronics model from the geometry and material allocations
    neutronics_model = paramak.NeutronicsModelFromReactor(
        reactor=my_reactor,
        materials={
            'inboard_tf_coils_mat': 'eurofer',
            'center_column_shield_mat': 'eurofer',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_rear_wall_mat': 'eurofer',
            'blanket_mat': 'Li4SiO4'},
        cell_tallies=['TBR', 'heating'],
        simulation_batches=5,
        simulation_particles_per_batch=1e4,
    )

    # simulate the neutronics model
    neutronics_model.simulate(method='trelis')
    print(neutronics_model.results)


if __name__ == "__main__":
    make_model_and_simulate()
