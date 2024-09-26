from cad_to_dagmc import CadToDagmc
from example_util_functions import transport_particles_on_h5m_geometry

import paramak

my_reactor = paramak.tokamak(
    radial_builds=[
        ("gap", 10),
        ("layer", 30),
        ("layer", 50),
        ("layer", 10),
        ("layer", 120),
        ("layer", 20),
        ("gap", 60),
        ("plasma", 300),
        ("gap", 60),
        ("layer", 20),
        ("layer", 120),
        ("layer", 10),
    ],
    vertical_build=[
        ("layer", 15),
        ("layer", 80),
        ("layer", 10),
        ("gap", 50),
        ("plasma", 700),
        ("gap", 60),
        ("layer", 10),
        ("layer", 40),
        ("layer", 15),
    ],
    triangularity=0.55,
    rotation_angle=180,
)

from cadquery.vis import show
show(my_reactor)

my_reactor.save(f"tokamak_minimal.step")
print(f"Saved as tokamak_minimal.step")

my_model = CadToDagmc()
material_tags = ["mat1"] * 6  # as inner and outer layers are one solid there are only 6 solids in model
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
my_model.export_dagmc_h5m_file(min_mesh_size=3.0, max_mesh_size=20.0)

h5m_filename = "dagmc.h5m"
flux = transport_particles_on_h5m_geometry(
    h5m_filename=h5m_filename,
    material_tags=material_tags,
    nuclides=["H1"] * len(material_tags),
    cross_sections_xml="tests/cross_sections.xml",
)
assert flux > 0.0
