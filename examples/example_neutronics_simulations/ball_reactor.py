"""This example makes a reactor geometry and a neutronics model, the addition
of a homogenised material is added to demonstrate the ability of making more
complex materials"""

import neutronics_material_maker as nmm
import paramak

# makes the 3d geometry
my_reactor = paramak.BallReactor(
    inner_bore_radial_thickness=1,
    inboard_tf_leg_radial_thickness=30,
    center_column_shield_radial_thickness=60,
    divertor_radial_thickness=50,
    inner_plasma_gap_radial_thickness=30,
    plasma_radial_thickness=300,
    outer_plasma_gap_radial_thickness=30,
    firstwall_radial_thickness=3,
    blanket_radial_thickness=100,
    blanket_rear_wall_radial_thickness=3,
    elongation=2.75,
    triangularity=0.5,
    number_of_tf_coils=16,
    rotation_angle=360,
)

#makes a homogenised material for the blanket from lithium lead and eurofer
blanket_material = nmm.MultiMaterial(
    fracs=[0.8, 0.2],
    materials=[
        nmm.Material('Pb842Li158',
                     enrichment=90,
                     temperature_in_K=500),
        nmm.Material('eurofer')
    ])

# makes the neutronics material
neutronics_model = paramak.NeutronicsModelFromReactor(
    reactor=my_reactor,
    materials={
        'inboard_tf_coils_mat': 'copper',
        'center_column_shield_mat': 'WC',
        'divertor_mat': 'eurofer',
        'firstwall_mat': 'eurofer',
        'blanket_mat': blanket_material, # use of homogenised material
        'blanket_rear_wall_mat': 'eurofer'},
    outputs=['TBR'],
    simulation_batches=5,
    simulation_particles_per_batches=1e4,
)

# starts the neutronics simulation
neutronics_model.simulate()

# prints the results to screen
print('tbr', neutronics_model.results['TBR'])
