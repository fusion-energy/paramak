"""
Example which creates a simple neutronics model using a parametric reactor
"""

import os
import uuid
import json
import openmc

import paramak
from neutronics_material_maker import Material, MultiMaterial


def make_neutronics_geometry(
    inner_bore_radial_thickness,
    inboard_tf_leg_radial_thickness,
    center_column_shield_radial_thickness,
    divertor_radial_thickness,
    inner_plasma_gap_radial_thickness,
    plasma_radial_thickness,
    outer_plasma_gap_radial_thickness,
    firstwall_radial_thickness,
    blanket_radial_thickness,
    blanket_rear_wall_radial_thickness,
    elongation,
    triangularity,
    number_of_tf_coils,
    rotation_angle,
):
    """
    Makes a reactor object from using theparametric
    BallReactor. Exports the neutronics description
    and stp files for the reactor
    """

    input_parameters = locals()

    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness=center_column_shield_radial_thickness,
        divertor_radial_thickness=divertor_radial_thickness,
        inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
        plasma_radial_thickness=plasma_radial_thickness,
        outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness=firstwall_radial_thickness,
        blanket_radial_thickness=blanket_radial_thickness,
        blanket_rear_wall_radial_thickness=blanket_rear_wall_radial_thickness,
        elongation=elongation,
        triangularity=triangularity,
        number_of_tf_coils=number_of_tf_coils,
        rotation_angle=rotation_angle,
    )

    my_reactor.export_stp()
    my_reactor.export_html("reactor.html")

    my_reactor.export_neutronics_description()

    """
    Uses Trelis together with a python script to
    reading the stp files assign material tags to
    the volumes and create a watertight h5m DAGMC
    file which can be used as neutronics geometry.
    """

    os.system("trelis -batch -nographics make_faceteted_neutronics_model.py")
    #     os.system('trelis make_faceteted_neutronics_model.py')

    os.system("make_watertight dagmc_notwatertight.h5m -o dagmc.h5m")

    # returns all the inputs and some extra reactor attributes, merged into a single dictionary
    return {
        **input_parameters,
        **{
            "major_radius": my_reactor.major_radius,
            "minor_radius": my_reactor.minor_radius,
        },
    }


def make_neutronics_model(
    reactor,
    firstwall_radial_thickness,
    firstwall_armour_material,
    firstwall_coolant_material,
    firstwall_structural_material,
    firstwall_armour_fraction,
    firstwall_coolant_fraction,
    firstwall_coolant_temperature_C,
    firstwall_coolant_pressure_Pa,
    firstwall_structural_fraction,
    blanket_rear_wall_coolant_material,
    blanket_rear_wall_structural_material,
    blanket_rear_wall_coolant_fraction,
    blanket_rear_wall_structural_fraction,
    blanket_rear_wall_coolant_temperature_C,
    blanket_rear_wall_coolant_pressure_Pa,
    blanket_lithium6_enrichment_percent,
    blanket_breeder_material,
    blanket_coolant_material,
    blanket_multiplier_material,
    blanket_structural_material,
    blanket_breeder_fraction,
    blanket_coolant_fraction,
    blanket_multiplier_fraction,
    blanket_structural_fraction,
    blanket_breeder_packing_fraction,
    blanket_multiplier_packing_fraction,
    blanket_coolant_temperature_C,
    blanket_coolant_pressure_Pa,
    blanket_breeder_temperature_C,
    blanket_breeder_pressure_Pa,
    divertor_coolant_fraction,
    divertor_structural_fraction,
    divertor_coolant_material,
    divertor_structural_material,
    divertor_coolant_temperature_C,
    divertor_coolant_pressure_Pa,
    center_column_shield_coolant_fraction,
    center_column_shield_structural_fraction,
    center_column_shield_coolant_material,
    center_column_shield_structural_material,
    center_column_shield_coolant_temperature_C,
    center_column_shield_coolant_pressure_Pa,
    inboard_tf_coils_conductor_fraction,
    inboard_tf_coils_coolant_fraction,
    inboard_tf_coils_structure_fraction,
    inboard_tf_coils_conductor_material,
    inboard_tf_coils_coolant_material,
    inboard_tf_coils_structure_material,
    inboard_tf_coils_coolant_temperature_C,
    inboard_tf_coils_coolant_pressure_Pa,
):
    """
    Makes and runs a simple OpenMC neutronics model with
    the materials with the same tags as the DAGMC neutronics
    geometry. The model also specifies the computational
    intensity (particles and batches) and the tally to record
    """
    input_parameters = locals()

    # this is the underlying geometry container that is filled with the faceteted CAD model
    universe = openmc.Universe()
    geom = openmc.Geometry(universe)

    center_column_shield_material = MultiMaterial(
        material_tag="center_column_shield_mat",
        materials=[
            Material(
                material_name=center_column_shield_coolant_material,
                temperature_in_C=center_column_shield_coolant_temperature_C,
                pressure_in_Pa=center_column_shield_coolant_pressure_Pa,
            ),
            Material(material_name=center_column_shield_structural_material),
        ],
        fracs=[
            center_column_shield_coolant_fraction,
            center_column_shield_structural_fraction,
        ],
        percent_type="vo",
        packing_fraction=1.0,
    ).openmc_material

    firstwall_material = MultiMaterial(
        material_tag="firstwall_mat",
        materials=[
            Material(
                material_name=firstwall_coolant_material,
                temperature_in_C=firstwall_coolant_temperature_C,
                pressure_in_Pa=firstwall_coolant_pressure_Pa,
            ),
            Material(material_name=firstwall_structural_material),
            Material(material_name=firstwall_armour_material),
        ],
        fracs=[
            firstwall_coolant_fraction,
            firstwall_structural_fraction,
            firstwall_armour_fraction,
        ],
        percent_type="vo",
        packing_fraction=1.0,
    ).openmc_material

    if (
        blanket_multiplier_material == None
        and blanket_multiplier_fraction == None
        and blanket_multiplier_packing_fraction == None
    ):

        blanket_material = MultiMaterial(
            material_tag="blanket_mat",
            materials=[
                Material(
                    material_name=blanket_coolant_material,
                    temperature_in_C=blanket_coolant_temperature_C,
                    pressure_in_Pa=blanket_coolant_pressure_Pa,
                ),
                Material(material_name=blanket_structural_material),
                Material(
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
                blanket_breeder_fraction,
            ],
            percent_type="vo",
            packing_fraction=1.0,
        ).openmc_material
    else:
        blanket_material = MultiMaterial(
            material_tag="blanket_mat",
            materials=[
                Material(
                    material_name=blanket_coolant_material,
                    temperature_in_C=blanket_coolant_temperature_C,
                    pressure_in_Pa=blanket_coolant_pressure_Pa,
                ),
                Material(material_name=blanket_structural_material),
                Material(
                    material_name=blanket_multiplier_material,
                    packing_fraction=blanket_multiplier_packing_fraction,
                ),
                Material(
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
            percent_type="vo",
            packing_fraction=1.0,
        ).openmc_material

    divertor_material = MultiMaterial(
        material_tag="divertor_mat",
        materials=[
            Material(
                material_name=divertor_coolant_material,
                temperature_in_C=divertor_coolant_temperature_C,
                pressure_in_Pa=divertor_coolant_pressure_Pa,
            ),
            Material(material_name=divertor_structural_material),
        ],
        fracs=[divertor_coolant_fraction, divertor_structural_fraction],
        percent_type="vo",
        packing_fraction=1.0,
    ).openmc_material

    inboard_tf_coils_material = MultiMaterial(
        material_tag="inboard_tf_coils_mat",
        materials=[
            Material(
                material_name=inboard_tf_coils_coolant_material,
                temperature_in_C=inboard_tf_coils_coolant_temperature_C,
                pressure_in_Pa=inboard_tf_coils_coolant_pressure_Pa,
            ),
            Material(material_name=inboard_tf_coils_conductor_material),
            Material(material_name=inboard_tf_coils_structure_material),
        ],
        fracs=[
            inboard_tf_coils_coolant_fraction,
            inboard_tf_coils_conductor_fraction,
            inboard_tf_coils_structure_fraction,
        ],
        percent_type="vo",
        packing_fraction=1.0,
    ).openmc_material

    blanket_rear_wall_material = MultiMaterial(
        material_tag="blanket_rear_wall_mat",
        materials=[
            Material(
                material_name=blanket_rear_wall_coolant_material,
                temperature_in_C=blanket_rear_wall_coolant_temperature_C,
                pressure_in_Pa=blanket_rear_wall_coolant_pressure_Pa,
            ),
            Material(material_name=blanket_rear_wall_structural_material),
        ],
        fracs=[
            blanket_rear_wall_coolant_fraction,
            blanket_rear_wall_structural_fraction,
        ],
        percent_type="vo",
        packing_fraction=1.0,
    ).openmc_material

    mats = openmc.Materials(
        [
            center_column_shield_material,
            firstwall_material,
            blanket_material,
            divertor_material,
            inboard_tf_coils_material,
            blanket_rear_wall_material,
        ]
    )

    # settings for the number of neutrons to simulate
    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 0
    settings.particles = 1000
    settings.run_mode = "fixed source"
    settings.dagmc = True

    # details of the birth locations and energy of the neutronis
    source = openmc.Source()
    source.space = openmc.stats.Point((reactor["major_radius"], 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    settings.source = source
    settings.photon_transport = (
        True  # This line is required to switch on photons tracking
    )

    # details about what neutrons interactions to keep track of (called a tally)
    tallies = openmc.Tallies()
    material_filter = openmc.MaterialFilter(blanket_material)
    tbr_tally = openmc.Tally(name="TBR")
    tbr_tally.filters = [material_filter]
    tbr_tally.scores = ["(n,Xt)"]  # where X is a wild card
    tallies.append(tbr_tally)

    material_filter = openmc.MaterialFilter(
        [blanket_material, firstwall_material, blanket_rear_wall_material]
    )
    blanket_heating_tally = openmc.Tally(name="blanket_heating")
    blanket_heating_tally.filters = [material_filter]
    blanket_heating_tally.scores = ["heating"]
    tallies.append(blanket_heating_tally)

    # make the model from gemonetry, materials, settings and tallies
    model = openmc.model.Model(geom, mats, settings, tallies)

    # run the simulation
    output_filename = model.run()

    """
    Reads the output file from the neutronics simulation
    and prints the TBR tally result to screen
    """

    # open the results file
    sp = openmc.StatePoint(output_filename)

    # access TBR tally
    tbr_tally = sp.get_tally(name="TBR")
    df = tbr_tally.get_pandas_dataframe()
    tbr_tally_result = df["mean"].sum()
    tbr_tally_std_dev = df["std. dev."].sum()

    # access heating tally
    blanket_heating_tally = sp.get_tally(name="blanket_heating")
    df = blanket_heating_tally.get_pandas_dataframe()
    blanket_heating_tally_result = df["mean"].sum() / 1e6
    blanket_heating_tally_std_dev = df["std. dev."].sum() / 1e6

    # returns all the inputs and some extra reactor attributes, merged into a single dictionary
    return {
        **input_parameters,
        **{
            "tbr": tbr_tally_result,
            "tbr_std_dev": tbr_tally_std_dev,
            "blanket_heating": blanket_heating_tally_result,
            "blanket_heating_std_dev": blanket_heating_tally_std_dev,
        },
    }


if __name__ == "__main__":

    for blanket_radial_thickness in range(15, 300, 10):

        geometry_parameters = make_neutronics_geometry(
            inner_bore_radial_thickness=1,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=3,
            blanket_radial_thickness=blanket_radial_thickness,
            blanket_rear_wall_radial_thickness=3,
            elongation=2.75,
            triangularity=0.5,
            number_of_tf_coils=16,
            rotation_angle=360,
        )

        material_parameters_and_results = make_neutronics_model(
            reactor=geometry_parameters,
            # based on http://www.euro-fusionscipub.org/wp-content/uploads/WPBBCP16_15535_submitted.pdf
            firstwall_radial_thickness=3.0,
            firstwall_armour_material="tungsten",
            firstwall_coolant_material="He",
            firstwall_structural_material="eurofer",
            firstwall_armour_fraction=0.106305,
            firstwall_coolant_fraction=0.333507,
            firstwall_coolant_temperature_C=400,
            firstwall_coolant_pressure_Pa=8e6,
            firstwall_structural_fraction=0.560188,
            # based on https://www.sciencedirect.com/science/article/pii/S2352179118300437
            blanket_rear_wall_coolant_material="H2O",
            blanket_rear_wall_structural_material="eurofer",
            blanket_rear_wall_coolant_fraction=0.3,
            blanket_rear_wall_structural_fraction=0.7,
            blanket_rear_wall_coolant_temperature_C=200,
            blanket_rear_wall_coolant_pressure_Pa=1e6,
            # based on https://www.sciencedirect.com/science/article/pii/S2352179118300437
            blanket_lithium6_enrichment_percent=60,
            blanket_breeder_material="Li4SiO4",
            blanket_coolant_material="He",
            blanket_multiplier_material="Be",
            blanket_structural_material="eurofer",
            blanket_breeder_fraction=0.15,
            blanket_coolant_fraction=0.05,
            blanket_multiplier_fraction=0.6,
            blanket_structural_fraction=0.2,
            blanket_breeder_packing_fraction=0.64,
            blanket_multiplier_packing_fraction=0.64,
            blanket_coolant_temperature_C=500,
            blanket_coolant_pressure_Pa=1e6,
            blanket_breeder_temperature_C=600,
            blanket_breeder_pressure_Pa=8e6,
            # based on https://www.sciencedirect.com/science/article/pii/S2352179118300437
            divertor_coolant_fraction=0.57195798876,
            divertor_structural_fraction=0.42804201123,
            divertor_coolant_material="H2O",
            divertor_structural_material="tungsten",
            divertor_coolant_temperature_C=150,
            divertor_coolant_pressure_Pa=5e6,
            # based on https://pdfs.semanticscholar.org/95fa/4dae7d82af89adf711b97e75a241051c7129.pdf?_ga=2.101398593.1139828080.1595493457-812289418.1595493457
            center_column_shield_coolant_fraction=0.13,
            center_column_shield_structural_fraction=0.57,
            center_column_shield_coolant_material="H2O",
            center_column_shield_structural_material="tungsten",
            center_column_shield_coolant_temperature_C=150,
            center_column_shield_coolant_pressure_Pa=5e6,
            # based on https://pdfs.semanticscholar.org/95fa/4dae7d82af89adf711b97e75a241051c7129.pdf?_ga=2.101398593.1139828080.1595493457-812289418.1595493457
            inboard_tf_coils_conductor_fraction=0.57,
            inboard_tf_coils_coolant_fraction=0.05,
            inboard_tf_coils_structure_fraction=0.38,
            inboard_tf_coils_conductor_material="copper",
            inboard_tf_coils_coolant_material="He",
            inboard_tf_coils_structure_material="SS316",
            inboard_tf_coils_coolant_temperature_C=30,
            inboard_tf_coils_coolant_pressure_Pa=8e6,
        )

        with open(str(uuid.uuid4()) + ".json", "w") as outfile:
            json.dump(
                {**geometry_parameters, **material_parameters_and_results}, outfile
            )
