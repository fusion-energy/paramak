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

# arc length that the segments of each layer must sum to
arc_length = paramak.poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)

number_of_tiles = 4
tile_gap = 5  # gap between neighbouring tiles
tile_length = (arc_length - number_of_tiles * tile_gap) / number_of_tiles
first_wall_tiles = [
    (paramak.LayerType.SOLID, tile_length, "tile"),
    (paramak.LayerType.GAP, tile_gap),
    (paramak.LayerType.SOLID, tile_length, "tile"),
    (paramak.LayerType.GAP, tile_gap),
    (paramak.LayerType.SOLID, tile_length, "tile"),
    (paramak.LayerType.GAP, tile_gap),
    (paramak.LayerType.SOLID, tile_length, "tile"),
    (paramak.LayerType.GAP, tile_gap),
]

result = paramak.tokamak_from_plasma(
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

my_reactor = result.add_divertor(
    poloidal_start_angle=75,
    poloidal_extent_angle=30,
    divertor_layer_names=["upper_divertor_armor", "upper_divertor_heatsink", "upper_divertor_shield"],
    divertor_layer_thicknesses=[10, 30, 50],
)

my_reactor = my_reactor.add_divertor(
    poloidal_start_angle=255,
    poloidal_extent_angle=30,
    divertor_layer_names=["lower_divertor_armor", "lower_divertor_heatsink", "lower_divertor_shield"],
    divertor_layer_thicknesses=[10, 30, 50],
)
my_reactor.export("tokamak_with_divertor.step")
print("Saved as tokamak_with_divertor.step")
print(my_reactor.names())



