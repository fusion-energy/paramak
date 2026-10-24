"""Structured meshes for tokamak blankets, divertors, and added coils.

The generated DAGMC and Exodus files contain blanket, divertor, center-column,
and coil meshes. Coil surfaces use CAD tessellation; Exodus coil volumes use
Gmsh. PyMOAB and PyDAGMC are required for H5M export, and the ``mesh`` optional
dependencies are required for Exodus export.
"""

import paramak


radial_build = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 80),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20, "first_wall"),
    (paramak.LayerType.SOLID, 80, "blanket"),
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 10, "rear_wall"),
]

arc_length = paramak.poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)
segment_length = (arc_length - 10) / 2
first_wall_segments = [
    (paramak.LayerType.SOLID, segment_length, "upper"),
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, segment_length, "lower"),
]
rotation_angle = 180
toroidal_arc = paramak.toroidal_arc_length(radial_build, rotation_angle=rotation_angle)
number_of_sectors = 4
sector_gap = 5
sector_length = (toroidal_arc - number_of_sectors * sector_gap) / number_of_sectors
toroidal_sectors = [
    (paramak.LayerType.SOLID, sector_length, "sector"),
    (paramak.LayerType.GAP, sector_gap),
] * number_of_sectors

reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[None, first_wall_segments, None, None, None],
    toroidal_build=[None, toroidal_sectors, toroidal_sectors, None, None],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=rotation_angle,
)
reactor = reactor.add_divertor(
    poloidal_start_angle=75,
    poloidal_extent_angle=30,
    divertor_layer_names=["upper_divertor_armor", "upper_divertor_heatsink", "upper_divertor_shield"],
    divertor_layer_thicknesses=[10, 30, 50],
)
reactor = reactor.add_divertor(
    poloidal_start_angle=255,
    poloidal_extent_angle=30,
    divertor_layer_names=["lower_divertor_armor", "lower_divertor_heatsink", "lower_divertor_shield"],
    divertor_layer_thicknesses=[10, 30, 50],
)

# Add coils after building the analytic reactor. The coil meshes are generated
# separately, so they do not remove or overlap blanket cells.
toroidal_coil = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point=(850, 800),
    vertical_mid_point=(1100, 0),
    thickness=40,
    distance=30,
    rotation_angle=rotation_angle,
    azimuthal_placement_angles=[0, 60, 120, 180],
    name="toroidal_field_coil",
)
reactor.add(toroidal_coil, name="toroidal_field_coil")

for index, vertical_position in enumerate((650, -650), start=1):
    poloidal_coil = paramak.poloidal_field_coil(
        height=50,
        width=50,
        center_point=(1250, vertical_position),
        rotation_angle=rotation_angle,
        name=f"poloidal_field_coil_{index}",
    )
    reactor.add(poloidal_coil, name=poloidal_coil.name)

meshes = reactor.mesh_structured_layers(n_poloidal=128, n_toroidal=32, n_axial=64)
for mesh in meshes:
    print(mesh["name"], len(mesh["vertices"]), len(mesh["triangles"]))

# Combine poloidally and toroidally segmented first-wall meshes into one
# material tag for each OpenMC material region.
tag_names = {
    f"first_wall_{section}_sector_{sector}": "first_wall"
    for section in ("upper", "lower")
    for sector in range(1, 5)
}
dagmc_model = reactor.create_structured_layer_dagmc_model(
    n_poloidal=128,
    n_toroidal=32,
    n_axial=64,
    tag_names=tag_names,
)
dagmc_model.write_file("tokamak_structured_layers.h5m")

# Blanket and divertor layers use the shared structured tetrahedral grid. Gmsh
# creates tetrahedra for the added CAD coil solids.
reactor.export_structured_layers_exodus(
    "tokamak_structured_layers.e",
    n_poloidal=128,
    n_toroidal=32,
    n_radial=2,
    n_axial=64,
    coil_mesh_size=10,
    tag_names=tag_names,
)
