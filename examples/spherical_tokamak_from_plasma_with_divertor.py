from pathlib import Path

from cad_to_dagmc import CadToDagmc
from example_util_functions import transport_particles_on_h5m_geometry

import paramak

my_reactor = paramak.spherical_tokamak_from_plasma(
    radial_builds=[
        [
            ("gap", 10),
            ("layer", 50),
            ("layer", 15),
            ("gap", 50),
            ("plasma", 300),
            ("gap", 60),
            ("layer", 15),
            ("layer", 60),
            ("layer", 10),
        ],
        [("gap", 75), ("lower_divertor", 100)],  # this divertor connects to the center column
        [("gap", 120), ("upper_divertor", 140)],  # this divertor has some blanket between the center colum and itself
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
)
my_reactor.save("spherical_tokamak_from_plasma_with_divertor.step")
print('written spherical_tokamak_from_plasma_with_divertor.step')


# my_model = CadToDagmc()
# material_tags = ["mat1"] * 21 # the two divertors split the 3 blanket layers into 9 and the magnets also splt the blanket.
# my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
# my_model.export_dagmc_h5m_file(min_mesh_size=3.0, max_mesh_size=20.0)

# h5m_filename = "dagmc.h5m"
# flux = transport_particles_on_h5m_geometry(
#     h5m_filename=h5m_filename,
#     material_tags=material_tags,
#     nuclides=["H1"] * len(material_tags),
#     cross_sections_xml="tests/cross_sections.xml",
# )
# assert flux > 0.0
