"""This example makes a reactor geometry, neutronics model and performs a TBR
simulation. A selection of materials are used from refrenced sources to
complete the neutronics model."""

import neutronics_material_maker as nmm
import paramak


def make_model_and_simulate():
    """Makes a neutronics Reactor model and simulates the TBR with specified materials"""

    # based on
    # http://www.euro-fusionscipub.org/wp-content/uploads/WPBBCP16_15535_submitted.pdf
    firstwall_radial_thickness = 3.0
    firstwall_armour_material = "tungsten"
    firstwall_coolant_material = "He"
    firstwall_structural_material = "eurofer"
    firstwall_armour_fraction = 0.106305
    firstwall_coolant_fraction = 0.333507
    firstwall_coolant_temperature_C = 400
    firstwall_coolant_pressure_Pa = 8e6
    firstwall_structural_fraction = 0.560188

    firstwall_material = nmm.MultiMaterial(
        material_tag="firstwall_mat",
        materials=[
            nmm.Material(
                material_name=firstwall_coolant_material,
                temperature_in_C=firstwall_coolant_temperature_C,
                pressure_in_Pa=firstwall_coolant_pressure_Pa,
            ),
            nmm.Material(material_name=firstwall_structural_material),
            nmm.Material(material_name=firstwall_armour_material),
        ],
        fracs=[
            firstwall_coolant_fraction,
            firstwall_structural_fraction,
            firstwall_armour_fraction,
        ],
        percent_type="vo"
    )

    # based on
    # https://www.sciencedirect.com/science/article/pii/S2352179118300437
    blanket_rear_wall_coolant_material = "H2O"
    blanket_rear_wall_structural_material = "eurofer"
    blanket_rear_wall_coolant_fraction = 0.3
    blanket_rear_wall_structural_fraction = 0.7
    blanket_rear_wall_coolant_temperature_C = 200
    blanket_rear_wall_coolant_pressure_Pa = 1e6

    blanket_rear_wall_material = nmm.MultiMaterial(
        material_tag="blanket_rear_wall_mat",
        materials=[
            nmm.Material(
                material_name=blanket_rear_wall_coolant_material,
                temperature_in_C=blanket_rear_wall_coolant_temperature_C,
                pressure_in_Pa=blanket_rear_wall_coolant_pressure_Pa,
            ),
            nmm.Material(material_name=blanket_rear_wall_structural_material),
        ],
        fracs=[
            blanket_rear_wall_coolant_fraction,
            blanket_rear_wall_structural_fraction,
        ],
        percent_type="vo"
    )

    # based on
    # https://www.sciencedirect.com/science/article/pii/S2352179118300437
    blanket_lithium6_enrichment_percent = 60
    blanket_breeder_material = "Li4SiO4"
    blanket_coolant_material = "He"
    blanket_multiplier_material = "Be"
    blanket_structural_material = "eurofer"
    blanket_breeder_fraction = 0.15
    blanket_coolant_fraction = 0.05
    blanket_multiplier_fraction = 0.6
    blanket_structural_fraction = 0.2
    blanket_breeder_packing_fraction = 0.64
    blanket_multiplier_packing_fraction = 0.64
    blanket_coolant_temperature_C = 500
    blanket_coolant_pressure_Pa = 1e6
    blanket_breeder_temperature_C = 600
    blanket_breeder_pressure_Pa = 8e6

    blanket_material = nmm.MultiMaterial(
        material_tag="blanket_mat",
        materials=[
            nmm.Material(
                material_name=blanket_coolant_material,
                temperature_in_C=blanket_coolant_temperature_C,
                pressure_in_Pa=blanket_coolant_pressure_Pa,
            ),
            nmm.Material(material_name=blanket_structural_material),
            nmm.Material(
                material_name=blanket_multiplier_material,
                packing_fraction=blanket_multiplier_packing_fraction,
            ),
            nmm.Material(
                material_name=blanket_breeder_material,
                enrichment=blanket_lithium6_enrichment_percent,
                packing_fraction=blanket_breeder_packing_fraction,
                temperature_in_C=blanket_breeder_temperature_C,
                pressure_in_Pa=blanket_breeder_pressure_Pa,
            ),
        ],
        fracs=[
            blanket_coolant_fraction,
            blanket_structural_fraction,
            blanket_multiplier_fraction,
            blanket_breeder_fraction,
        ],
        percent_type="vo"
    )

    # based on
    # https://www.sciencedirect.com/science/article/pii/S2352179118300437
    divertor_coolant_fraction = 0.57195798876
    divertor_structural_fraction = 0.42804201123
    divertor_coolant_material = "H2O"
    divertor_structural_material = "tungsten"
    divertor_coolant_temperature_C = 150
    divertor_coolant_pressure_Pa = 5e6

    divertor_material = nmm.MultiMaterial(
        material_tag="divertor_mat",
        materials=[
            nmm.Material(
                material_name=divertor_coolant_material,
                temperature_in_C=divertor_coolant_temperature_C,
                pressure_in_Pa=divertor_coolant_pressure_Pa,
            ),
            nmm.Material(material_name=divertor_structural_material),
        ],
        fracs=[divertor_coolant_fraction, divertor_structural_fraction],
        percent_type="vo"
    )

    # based on
    # https://pdfs.semanticscholar.org/95fa/4dae7d82af89adf711b97e75a241051c7129.pdf
    center_column_shield_coolant_fraction = 0.13
    center_column_shield_structural_fraction = 0.57
    center_column_shield_coolant_material = "H2O"
    center_column_shield_structural_material = "tungsten"
    center_column_shield_coolant_temperature_C = 150
    center_column_shield_coolant_pressure_Pa = 5e6

    center_column_shield_material = nmm.MultiMaterial(
        material_tag="center_column_shield_mat",
        materials=[
            nmm.Material(
                material_name=center_column_shield_coolant_material,
                temperature_in_C=center_column_shield_coolant_temperature_C,
                pressure_in_Pa=center_column_shield_coolant_pressure_Pa,
            ),
            nmm.Material(
                material_name=center_column_shield_structural_material),
        ],
        fracs=[
            center_column_shield_coolant_fraction,
            center_column_shield_structural_fraction,
        ],
        percent_type="vo")

    # based on
    # https://pdfs.semanticscholar.org/95fa/4dae7d82af89adf711b97e75a241051c7129.pdf
    inboard_tf_coils_conductor_fraction = 0.57
    inboard_tf_coils_coolant_fraction = 0.05
    inboard_tf_coils_structure_fraction = 0.38
    inboard_tf_coils_conductor_material = "copper"
    inboard_tf_coils_coolant_material = "He"
    inboard_tf_coils_structure_material = "SS_316L_N_IG"
    inboard_tf_coils_coolant_temperature_C = 30
    inboard_tf_coils_coolant_pressure_Pa = 8e6

    inboard_tf_coils_material = nmm.MultiMaterial(
        material_tag="inboard_tf_coils_mat",
        materials=[
            nmm.Material(
                material_name=inboard_tf_coils_coolant_material,
                temperature_in_C=inboard_tf_coils_coolant_temperature_C,
                pressure_in_Pa=inboard_tf_coils_coolant_pressure_Pa,
            ),
            nmm.Material(material_name=inboard_tf_coils_conductor_material),
            nmm.Material(material_name=inboard_tf_coils_structure_material),
        ],
        fracs=[
            inboard_tf_coils_coolant_fraction,
            inboard_tf_coils_conductor_fraction,
            inboard_tf_coils_structure_fraction,
        ],
        percent_type="vo"
    )

    # makes the 3d geometry
    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=1,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=firstwall_radial_thickness,
        # http://www.euro-fusionscipub.org/wp-content/uploads/WPBBCP16_15535_submitted.pdf
        blanket_radial_thickness=100,
        blanket_rear_wall_radial_thickness=3,
        elongation=2.75,
        triangularity=0.5,
        number_of_tf_coils=16,
        rotation_angle=360,
    )

    source = openmc.Source()
    # sets the location of the source to x=0 y=0 z=0
    source.space = openmc.stats.Point((my_reactor.major_radius, 0, 0))
    # sets the direction to isotropic
    source.angle = openmc.stats.Isotropic()
    # sets the energy distribution to 100% 14MeV neutrons
    source.energy = openmc.stats.Discrete([14e6], [1])

    # makes the neutronics material
    neutronics_model = paramak.NeutronicsModelFromReactor(
        reactor=my_reactor,
        source=source,
        materials={
            'inboard_tf_coils_mat': inboard_tf_coils_material,
            'center_column_shield_mat': center_column_shield_material,
            'divertor_mat': divertor_material,
            'firstwall_mat': firstwall_material,
            'blanket_mat': blanket_material,
            'blanket_rear_wall_mat': blanket_rear_wall_material},
        cell_tallies=['TBR'],
        simulation_batches=5,
        simulation_particles_per_batch=1e4,
    )

    # starts the neutronics simulation
    neutronics_model.simulate(method='trelis')

    # prints the simulation results to screen
    print('TBR', neutronics_model.results['TBR'])


if __name__ == "__main__":
    make_model_and_simulate()
