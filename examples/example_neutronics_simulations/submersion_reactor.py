"""This is a example that obtains the tritium breeding ratio (TBR)
for a parametric submersion reactor and specified the faceting and merge
tolerance when creating the dagmc model"""

import matplotlib.pyplot as plt
import neutronics_material_maker as nmm
import paramak


def make_model_and_simulate(temperature):
    """Makes a neutronics Reactor model and simulates the flux"""

    # makes the 3d geometry from input parameters
    my_reactor = paramak.SubmersionTokamak(
        inner_bore_radial_thickness=30,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=30,
        divertor_radial_thickness=80,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=200,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=30,
        blanket_rear_wall_radial_thickness=30,
        rotation_angle=180,
        support_radial_thickness=50,
        inboard_blanket_radial_thickness=30,
        outboard_blanket_radial_thickness=30,
        elongation=2.75,
        triangularity=0.5,
    )

    # this can just be set as a string as temperature is needed for this
    # material
    flibe = nmm.Material('FLiBe', temperature_in_C=temperature)

    source = openmc.Source()
    # sets the location of the source to x=0 y=0 z=0
    source.space = openmc.stats.Point((my_reactor.major_radius, 0, 0))
    # sets the direction to isotropic
    source.angle = openmc.stats.Isotropic()
    # sets the energy distribution to 100% 14MeV neutrons
    source.energy = openmc.stats.Discrete([14e6], [1])

    # makes the neutronics model from the geometry and material allocations
    neutronics_model = paramak.NeutronicsModelFromReactor(
        reactor=my_reactor,
        source=source,
        materials={
            'inboard_tf_coils_mat': 'eurofer',
            'center_column_shield_mat': 'eurofer',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_rear_wall_mat': 'eurofer',
            'blanket_mat': flibe,
            'supports_mat': 'eurofer'},
        cell_tallies=['TBR'],
        simulation_batches=5,
        simulation_particles_per_batch=1e4,
        faceting_tolerance=1e-4,
        merge_tolerance=1e-4
    )

    # simulate the neutronics model
    neutronics_model.simulate(method='trelis')
    return neutronics_model.results['TBR']


if __name__ == "__main__":
    tbr_values = []
    temperature_values = [32, 100, 200, 300, 400, 500]
    for temperature in temperature_values:
        tbr = make_model_and_simulate(temperature)
        tbr_values.append(tbr)

    # plots the results
    plt.scatter(temperature_values, tbr_values)
    plt.xlabel('FLiBe Temperature (degrees C)')
    plt.ylabel('TBR')
    plt.show()
