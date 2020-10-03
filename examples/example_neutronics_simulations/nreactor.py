
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
    rotation_angle=360,
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
    tallies=['TBR'],
    ion_density_origin=200,
    ion_density_peaking_factor=200,
    ion_density_pedestal=200,
    ion_density_separatrix=200,
    ion_temperature_origin=200,
    ion_temperature_peaking_factor=200,
    ion_temperature_pedestal=200,
    ion_temperature_separatrix=200,
    pedestal_radius=200,
    shafranov_shift=200,
    triangularity=200,
    ion_temperature_beta=200,
    output_folder=200,
)

neutronics_model.create_materials()