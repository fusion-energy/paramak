"""this is a minimal example that obtains the tbr for a parametric reactor"""

import paramak

my_reactor = paramak.BallReactor(
    inner_bore_radial_thickness=50,
    inboard_tf_leg_radial_thickness=200,
    center_column_shield_radial_thickness=50,
    divertor_radial_thickness=50,
    inner_plasma_gap_radial_thickness=50,
    plasma_radial_thickness=100,
    outer_plasma_gap_radial_thickness=50,
    firstwall_radial_thickness=5,
    blanket_radial_thickness=100,
    blanket_rear_wall_radial_thickness=10,
    elongation=2,
    triangularity=0.55,
    number_of_tf_coils=16,
    rotation_angle=180,
)

neutronics_model = paramak.NeutronicsModelFromReactor(
    reactor=my_reactor,
    materials={
        'DT_plasma': 'DT_plasma',
        'inboard_tf_coils_mat': 'eurofer',
        'center_column_shield_mat': 'eurofer',
        'divertor_mat': 'eurofer',
        'blanket_mat': 'eurofer',
        'blanket_mat': 'Li4SiO4'},
    tallies=['TBR', 'heat'],
    simulation_batches=10,
    simulation_particles_per_batches=1e4,
)

neutronics_model.create_neutronics_model()
neutronics_model.simulate()
print(neutronics_model.results)