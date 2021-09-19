
# This minimal example makes a 3D volume and exports the shape to a stp file
# A surrounding volume called a graveyard is needed for neutronics simulations

import paramak


import numpy as np


my_reactor = paramak.EuDemoFrom2015PaperDiagram(
    number_of_tf_coils=10,
    rotation_angle=180
)

[divertor, blanket, vac_vessel, vac_vessel_inner] = my_reactor.create_vessel_components()

vac_vessel_inner.solid = paramak.utils.cut_solid(
    vac_vessel_inner.solid, blanket)
vac_vessel_inner.export_stl('stage_1_output/vac_vessel_inner.stl')
# vac_vessel.export_stl('stage_1_output/vacvessel.stl')
# my_reactor.export_stl(output_folder='stage_1_output')
# my_reactor.export_neutronics_description('stage_1_output/manifest.json')
