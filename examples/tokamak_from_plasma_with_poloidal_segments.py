import paramak

radial_build = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20),  # first wall
    (paramak.LayerType.SOLID, 120),  # blanket
    (paramak.LayerType.SOLID, 10),  # rear wall
]

# The segments of every layer are measured along the plasma facing surface
# (the inner surface of the first wall), starting at the outboard midplane
# and going counter clockwise. The segments of each layer must sum to this
# arc length.
arc_length = paramak.poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)
print(f"poloidal arc length {arc_length}")

# First wall tiles: only the first wall is segmented.
number_of_tiles = 4
tile_gap = 5  # gap between neighbouring tiles
tile_length = (arc_length - number_of_tiles * tile_gap) / number_of_tiles
first_wall_tiles = [
    ("tile", tile_length),
    ("gap", tile_gap),
    ("tile", tile_length),
    ("gap", tile_gap),
    ("tile", tile_length),
    ("gap", tile_gap),
    ("tile", tile_length),
    ("gap", tile_gap),
]

# poloidal_build has one entry per radial_build entry after the plasma,
# ordered from the plasma outwards, with None for layers that are not segmented
my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[
        None,  # gap after the plasma
        first_wall_tiles,  # first wall
        None,  # blanket
        None,  # rear wall
    ],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=180,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_first_wall_tiles.step")
print("Saved as tokamak_from_plasma_with_first_wall_tiles.step")

# First wall and blanket modules: giving both layers the same segments makes
# the gaps line up, as the cuts follow the normal to the plasma surface.
number_of_modules = 8
module_gap = 20  # gap between neighbouring modules
module_length = (arc_length - number_of_modules * module_gap) / number_of_modules
modules = [("module", module_length), ("gap", module_gap)] * number_of_modules

my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[
        None,  # gap after the plasma
        modules,  # first wall
        modules,  # blanket
        None,  # rear wall
    ],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=180,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_first_wall_and_blanket_modules.step")
print("Saved as tokamak_from_plasma_with_first_wall_and_blanket_modules.step")

# Each layer can also have different segments, for example first wall tiles
# in front of the blanket modules. Boundaries at the same arc length line up,
# here the end of each tile gap lines up with the end of every second module gap.
my_reactor = paramak.tokamak_from_plasma(
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
my_reactor.export("tokamak_from_plasma_with_tiles_and_modules.step")
print("Saved as tokamak_from_plasma_with_tiles_and_modules.step")
