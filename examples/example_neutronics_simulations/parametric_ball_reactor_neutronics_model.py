"""
Example which creates a simple neutronics model using a parametric reactor
"""

import os

import openmc
from neutronics_material_maker import Material

import paramak


def make_cad_model_with_paramak():
    """
    Makes a reactor object by using the parametric
    BallReactor. Exports the neutronics description
    and stp files for the reactor
    """
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

    my_reactor.export_stp()

    my_reactor.export_neutronics_description()

    return my_reactor


def convert_stp_files_to_neutronics_geometry():
    """
    Uses Trelis together with a python script to
    read the STP files, assign material tags to
    the volumes and create a watertight h5m DAGMC
    file which can be used as neutronics geometry.
    """

    os.system("trelis -batch -nographics make_faceteted_neutronics_model.py")

    os.system("make_watertight dagmc_notwatertight.h5m -o dagmc.h5m")


def make_other_aspects_of_neutronics_model(my_reactor):
    """
    Makes and runs a simple OpenMC neutronics model with
    the materials with the same tags as the DAGMC neutronics
    geometry. The model also specifies the computational
    intensity (particles and batches) and the tally to record
    """

    # these materials are overly simplified to keep the example short
    firstwall_mat = Material(
        material_name="eurofer", material_tag="firstwall_mat"
    ).openmc_material

    inboard_tf_coils_mat = Material(
        material_name="WC", material_tag="inboard_tf_coils_mat"
    ).openmc_material

    center_column_mat = Material(
        material_name="WC", material_tag="center_column_shield_mat"
    ).openmc_material

    divertor_mat = Material(
        material_name="eurofer", material_tag="divertor_mat"
    ).openmc_material

    blanket_mat = Material(
        material_name="Li4SiO4", enrichment=60, material_tag="blanket_mat"
    ).openmc_material

    blanket_rear_wall_mat = Material(
        material_name="eurofer", material_tag="blanket_rear_wall_mat"
    ).openmc_material

    mats = openmc.Materials(
        [
            firstwall_mat,
            inboard_tf_coils_mat,
            center_column_mat,
            divertor_mat,
            blanket_mat,
            blanket_rear_wall_mat,
        ]
    )

    # this is the underlying geometry container that is filled with the
    # faceteted CAD model
    universe = openmc.Universe()
    geom = openmc.Geometry(universe)

    # settings for the number of neutrons to simulate
    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 0
    settings.particles = 100
    settings.run_mode = "fixed source"
    settings.dagmc = True

    # details of the birth locations and energy of the neutronis
    source = openmc.Source()
    source.space = openmc.stats.Point((my_reactor.major_radius, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    settings.source = source

    # details about what neutrons interactions to keep track of (called a
    # tally)
    tallies = openmc.Tallies()
    material_filter = openmc.MaterialFilter(blanket_mat)
    tbr_tally = openmc.Tally(name="TBR")
    tbr_tally.filters = [material_filter]
    tbr_tally.scores = ["(n,Xt)"]  # where X is a wild card
    tallies.append(tbr_tally)

    # make the model from gemonetry, materials, settings and tallies
    model = openmc.model.Model(geom, mats, settings, tallies)

    # run the simulation
    output_filename = model.run()

    return output_filename


def read_simulation_results(output_filename):
    """
    Reads the output file from the neutronics simulation
    and prints the TBR tally result to screen
    """

    # open the results file
    sp = openmc.StatePoint(output_filename)

    # access the tally
    tbr_tally = sp.get_tally(name="TBR")
    df = tbr_tally.get_pandas_dataframe()
    tbr_tally_result = df["mean"].sum()

    # print result
    print("The tritium breeding ratio was found, TBR = ", tbr_tally_result)
    # return tbr_tally_result


if __name__ == "__main__":

    my_reactor = make_cad_model_with_paramak()
    convert_stp_files_to_neutronics_geometry()
    output_filename = make_other_aspects_of_neutronics_model(my_reactor)
    read_simulation_results(output_filename)
