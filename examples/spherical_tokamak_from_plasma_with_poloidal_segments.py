import paramak

radial_build = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),  # first wall
    (paramak.LayerType.SOLID, 60),  # blanket
    (paramak.LayerType.SOLID, 10),  # rear wall
]

# The segments of every layer are measured along the plasma facing surface
# (the inner surface of the first wall). For a spherical tokamak this starts
# where the layer meets the centre column at the bottom, runs along the
# bottom, up the outboard side and along the top back to the centre column.
# The segments of each layer must sum to this arc length.
arc_length = paramak.spherical_poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)
print(f"poloidal arc length {arc_length}")

# First wall tiles
number_of_tiles = 16
tile_gap = 5  # gap between neighbouring tiles
tile_length = (arc_length - number_of_tiles * tile_gap) / number_of_tiles
first_wall_tiles = [("tile", tile_length), ("gap", tile_gap)] * number_of_tiles

# Blanket modules, the end of every second tile gap lines up with the end of a
# module gap
number_of_modules = 8
module_gap = 15  # gap between neighbouring modules
module_length = (arc_length - number_of_modules * module_gap) / number_of_modules
modules = [("module", module_length), ("gap", module_gap)] * number_of_modules

# poloidal_build has one entry per radial_build entry after the plasma,
# ordered from the plasma outwards, with None for layers that are not segmented
my_reactor = paramak.spherical_tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[
        None,  # gap after the plasma
        first_wall_tiles,  # first wall
        modules,  # blanket
        None,  # rear wall
    ],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=180,
)
print(my_reactor.names())
my_reactor.export("spherical_tokamak_from_plasma_with_poloidal_segments.step")
print("Saved as spherical_tokamak_from_plasma_with_poloidal_segments.step")
