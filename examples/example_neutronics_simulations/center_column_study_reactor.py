"""This example makes a reactor geometry and a neutronics model, the addition
of a Python for loop allow a parameter sweep of the neutronics results for
different geometries. The distance between the plasma and center column is
varried while simulating the impact on the heat depositied in the center
column."""

import matplotlib.pyplot as plt
import openmc
import paramak


def make_model_and_simulate():
    """Makes a neutronics Reactor model and simulates the TBR"""

    total_heats_in_MW = []
    plasma_to_center_column_gaps = []

    # this will take a few mins to perform 3 simulations at
    for plasma_to_center_column_gap in [50, 100, 150]:

        # makes the 3d geometry
        my_reactor = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=20,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=2,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=plasma_to_center_column_gap,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=90,
            elongation=2.75,
            triangularity=0.5,
            plasma_gap_vertical_thickness=40,
            center_column_arc_vertical_thickness=520,
            rotation_angle=360
        )

        source = openmc.Source()
        # sets the location of the source to x=0 y=0 z=0
        source.space = openmc.stats.Point((my_reactor.major_radius, 0, 0))
        # sets the direction to isotropic
        source.angle = openmc.stats.Isotropic()
        # sets the energy distribution to 100% 14MeV neutrons
        source.energy = openmc.stats.Discrete([14e6], [1])

        # makes the neutronics model and assigns basic materials to each
        # component
        neutronics_model = paramak.NeutronicsModel(
            geometry=my_reactor,
            source=source,
            materials={
                'DT_plasma': 'DT_plasma',
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
        neutronics_model.simulate()

        # converts the results to mega watts
        total_heat_in_MW = neutronics_model.results['firstwall_mat_heating']['Watts']['result'] / 1e6

        # adds the results and inputs to a list
        total_heats_in_MW.append(total_heat_in_MW)
        plasma_to_center_column_gaps.append(plasma_to_center_column_gap)

    # plots the results
    plt.scatter(plasma_to_center_column_gaps, total_heats_in_MW)
    plt.xlabel('plasma_to_center_column_gap (cm)')
    plt.ylabel('Heat on the inboard (MW)')
    plt.show()


if __name__ == "__main__":
    make_model_and_simulate()
