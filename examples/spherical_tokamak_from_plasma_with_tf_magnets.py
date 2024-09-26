from pathlib import Path

from cad_to_dagmc import CadToDagmc
from example_util_functions import transport_particles_on_h5m_geometry

import paramak

tf = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point = (10, 520),
    vertical_mid_point = (600, 0),
    thickness = 50,
    distance = 40,
    with_inner_leg = True,
    azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
)

result = paramak.spherical_tokamak_from_plasma(
    radial_builds=[
        ("gap", 70),
        ("layer", 10),
        ("layer", 10),
        ("gap", 50),
        ("plasma", 300),
        ("gap", 60),
        ("layer", 10),
        ("layer", 60),
        ("layer", 10),
    ],
    elongation=2.5,
    rotation_angle=180,
    triangularity=0.55,
    add_extra_cut_shapes=[tf]
)

result.save(f"spherical_tokamak_minimal.step")


# needed to downgrade pip with ... python -m pip  install pip==24.0
from jupyter_cadquery import show

view = show(result)
view.export_html("3d.html")


my_model = CadToDagmc()
material_tags = ["mat1"] * 7
my_model.add_cadquery_object(cadquery_object=result, material_tags=material_tags)
my_model.export_dagmc_h5m_file(min_mesh_size=3.0, max_mesh_size=20.0)

h5m_filename = "dagmc.h5m"
flux = transport_particles_on_h5m_geometry(
    h5m_filename=h5m_filename,
    material_tags=material_tags,
    nuclides=["H1"] * len(material_tags),
    cross_sections_xml="tests/cross_sections.xml",
)
assert flux > 0.0
