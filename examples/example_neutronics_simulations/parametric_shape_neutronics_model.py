"""
Example which creates a simple neutronics model using parametric shapes
"""

import os

import openmc
from neutronics_material_maker import Material

import paramak


def make_cad_model_with_paramak():
    """
    Makes a reactor object from two parametric
    shapes. Exports the neutronics description
    and stp files for the reactor
    """

    width = 500

    # creates a parametric shape
    pf_coil = paramak.RotateStraightShape(
        points=[(width, width), (550, width), (550, 550), (500, 550)],
        stp_filename="pf_coil.stp",
        material_tag="pf_coil_material",
    )

    pf_coil.export_html("test.html")

    # creates another parametric shape
    blanket = paramak.RotateMixedShape(
        points=[
            (538, 305, "straight"),
            (538, -305, "straight"),
            (322, -305, "spline"),
            (470, 0, "spline"),
            (322, 305, "straight"),
        ],
        rotation_angle=40,
        azimuth_placement_angle=[0, 45, 90, 135, 180, 225, 270, 315],
        stp_filename="blanket.stp",
        material_tag="blanket_material",
    )
    blanket.solid

    # creates a reactor object from the two components
    my_reactor = paramak.Reactor([blanket, pf_coil])

    # exports neutronics description and stp files
    my_reactor.export_neutronics_description()
    my_reactor.export_stp()


def convert_stp_files_to_neutronics_geometry():
    """
    Uses Trelis together with a python script to
    read the STP files, assign material tags to
    the volumes and create a watertight h5m DAGMC
    file which can be used as neutronics geometry.
    """

    os.system("trelis -batch -nographics make_faceteted_neutronics_model.py")

    os.system("make_watertight dagmc_notwatertight.h5m -o dagmc.h5m")


def make_other_aspects_of_neutronics_model():
    """
    Makes and runs a simple OpenMC neutronics model with
    the materials with the same tags as the DAGMC neutronics
    geometry. The model also specifies the computational
    intensity (particles and batches) and the tally to record
    """

    universe = openmc.Universe()
    geom = openmc.Geometry(universe)

    mat1 = Material(
        material_name="Li4SiO4", material_tag="blanket_material"
    ).openmc_material

    mat2 = Material(
        material_name="copper", material_tag="pf_coil_material"
    ).openmc_material

    mats = openmc.Materials([mat1, mat2])

    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 0
    settings.particles = 100
    settings.run_mode = "fixed source"
    settings.dagmc = True

    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    settings.source = source

    tallies = openmc.Tallies()
    tbr_tally = openmc.Tally(name="TBR")
    tbr_tally.scores = ["(n,Xt)"]  # where X is a wild card
    tallies.append(tbr_tally)

    model = openmc.model.Model(geom, mats, settings, tallies)

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
    return tbr_tally_result


if __name__ == "__main__":

    make_cad_model_with_paramak()
    convert_stp_files_to_neutronics_geometry()
    output_filename = make_other_aspects_of_neutronics_model()
    read_simulation_results(output_filename)
