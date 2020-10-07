import matplotlib.pyplot as plt
import paramak

total_heats_in_MW = []
plasma_to_center_column_gaps = []

# this will take a few mins to perform 3 simulations at 
for plasma_to_center_column_gap in [50, 100, 150]:

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
        # first number must be between plasma inner/outer radius
        plasma_high_point=(180+plasma_to_center_column_gap, 240),
        plasma_gap_vertical_thickness=40,
        center_column_arc_vertical_thickness=520,
        rotation_angle=360
    )

    neutronics_model = paramak.NeutronicsModelFromReactor(
        reactor=my_reactor,
        materials={
            'DT_plasma': 'DT_plasma',
            'inboard_tf_coils_mat': 'eurofer',
            'center_column_shield_mat': 'eurofer',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_mat': 'Li4SiO4'},
        outputs=['TBR', 'heat'],
        simulation_batches=5,
        simulation_particles_per_batches=1e4,
    )

    neutronics_model.simulate()

    total_heat_in_MW = (neutronics_model.results['center_column_shield_mat_heat']['Watts']['result'] + \
                        neutronics_model.results['firstwall_mat_heat']['Watts']['result']) / 1e6

    total_heats_in_MW.append(total_heat_in_MW)
    plasma_to_center_column_gaps.append(plasma_to_center_column_gap)

plt.scatter(plasma_to_center_column_gaps, total_heats_in_MW)
plt.xlabel('plasma_to_center_column_gap (cm)')
plt.ylabel('Heat on the inboard (MW)')
plt.show()
