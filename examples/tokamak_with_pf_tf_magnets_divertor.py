
from example_util_functions import transport_particles_on_h5m_geometry

import paramak
from cadquery import vis, Workplane

# makes a rectangle that overlaps the lower blanket under the plasma
# the intersection of this and the layers will form the lower divertor
points = [(300, -700), (300, 0), (400, 0), (400, -700)]
divertor_lower = Workplane('XZ', origin=(0,0,0)).polyline(points).close().revolve(180)

# creates a toroidal 
tf = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point = (10, 520),
    vertical_mid_point = (860, 0),
    thickness = 50,
    distance = 40,
    with_inner_leg = True,
    azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
)

extra_cut_shapes = [tf]

# creates pf coil
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
    [(730, 370), (810, 235), (810, -235), (730, -370)]
):
    extra_cut_shapes.append(
        paramak.poloidal_field_coil(
            height=height, width=width, center_point=center_point, rotation_angle=180
        )
    )
    extra_cut_shapes.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=180,
            center_point=center_point,
        )
    )

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 650),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
    ],
    triangularity=0.55,
    rotation_angle=180,
    extra_cut_shapes=extra_cut_shapes,
    extra_intersect_shapes=[divertor_lower]
)
my_reactor.save(f"tokamak_with_divertor.step")
print(f"Saved as tokamak_with_divertor.step")
# vis.show(my_reactor)

# from cad_to_dagmc import CadToDagmc
# my_model = CadToDagmc()
# material_tags = ["mat1"] * 6  # as inner and outer layers are one solid there are only 6 solids in model
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
