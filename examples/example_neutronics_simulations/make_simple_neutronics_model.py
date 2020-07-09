"""
Example which creates a simple neutronics model using parametric shapes
"""

import os

import openmc
from neutronics_material_maker import Material

import paramak


def make_cad_model_with_paramak():

    width=500

    pf_coil = paramak.RotateStraightShape(
        points=[
            (width, width),
            (550, width),
            (550, 550),
            (500, 550)
        ]
    )

    pf_coil.export_html('test.html')


    blanket = paramak.RotateMixedShape(
        points=[
            (538, 305, "straight"),
            (538, -305, "straight"),
            (322, -305, "spline"),
            (470, 0, "spline"),
            (322, 305, "straight")
        ],
        rotation_angle=40,
        azimuth_placement_angle=[0, 45, 90, 135, 180, 225, 270, 315]
    )
    blanket.solid



    my_reactor = paramak.Reactor()

    blanket.stp_filename = 'blanket.stp'
    pf_coil.stp_filename = 'pf_coil.stp'

    blanket.material_tag = 'blanket_material'
    pf_coil.material_tag = 'pf_coil_material'

    my_reactor.add_shape_or_component(blanket)
    my_reactor.add_shape_or_component(pf_coil)


    my_reactor.export_neutronics_description()
    my_reactor.export_stp()


def convert_stp_files_to_neutronics_model():

    os.system('trelis -batch -nographics make_faceteted_neutronics_model.py')

    os.system('make_watertight dagmc_notwatertight.h5m -o dagmc.h5m')

    universe = openmc.Universe()
    geom = openmc.Geometry(universe)

    mat1 = Material(material_name='Li4SiO4',
                    material_tag='blanket_material').openmc_material

    mat2 = Material(material_name='copper',
                    material_tag='pf_coil_material').openmc_material

    mats = openmc.Materials([mat1, mat2])


    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 0
    settings.particles = 100
    settings.run_mode = 'fixed source'
    settings.dagmc = True 

    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    settings.source = source


    tallies = openmc.Tallies()
    tbr_tally = openmc.Tally(name='TBR')
    tbr_tally.scores = ['(n,Xt)'] # where X is a wild card
    tallies.append(tbr_tally)


    model = openmc.model.Model(geom, mats, settings, tallies)

    statepoint_filename = model.run()

    # open the results file
    sp = openmc.StatePoint(statepoint_filename)

    # access the tally
    tbr_tally = sp.get_tally(name='TBR')
    df = tbr_tally.get_pandas_dataframe()
    tbr_tally_result = df['mean'].sum()

    # print result
    print('The tritium breeding ratio was found, TBR = ', tbr_tally_result)
    return tbr_tally_result

if __name__ == "__main__":

    make_cad_model_with_paramak()
    convert_stp_files_to_neutronics_model()
