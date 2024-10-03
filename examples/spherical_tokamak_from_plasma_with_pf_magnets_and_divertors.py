from pathlib import Path

from cad_to_dagmc import CadToDagmc
from example_util_functions import transport_particles_on_h5m_geometry

import paramak

rotation_angle = 180
poloidal_field_coils = []
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(500, 300), (560, 100), (560, -100), (500, -300)]
):
    poloidal_field_coils.append(
        paramak.poloidal_field_coil(
            height=height, width=width, center_point=center_point, rotation_angle=rotation_angle
        )
    )
    poloidal_field_coils.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=rotation_angle,
            center_point=center_point,
        )
    )

#TODO
# [(paramak.LayerType.GAP, 75), ("lower_divertor", 100)],
my_reactor = paramak.spherical_tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=rotation_angle,
    extra_cut_shapes=poloidal_field_coils,
)
my_reactor.save(f"spherical_tokamak_from_plasma_with_pf_magnets_and_divertor.step")



# my_model = CadToDagmc()
# material_tags = ["mat1"] * 5
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
