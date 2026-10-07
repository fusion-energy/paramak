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
rotation_angle = 180

# The sectors of every layer are measured around the plasma facing surface
# (the inner surface of the first wall) at the outboard midplane, starting at
# the XZ plane. The sectors of each layer must sum to this arc length.
toroidal_arc = paramak.toroidal_arc_length(radial_build, rotation_angle=rotation_angle)
print(f"toroidal arc length {toroidal_arc}")

# Eight sectors separated by gaps. Gaps have parallel sides, so a 20 cm gap is
# 20 cm wide at every radius.
number_of_sectors = 8
sector_gap = 20  # width of the gap between neighbouring sectors
sector_length = (toroidal_arc - number_of_sectors * sector_gap) / number_of_sectors
sectors = [
    (paramak.LayerType.SOLID, sector_length, "sector"),
    (paramak.LayerType.GAP, sector_gap),
] * number_of_sectors

# toroidal_build has one entry per radial_build entry after the plasma,
# ordered from the plasma outwards, with None for layers that are not segmented
my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    toroidal_build=[
        None,  # gap after the plasma
        sectors,  # first wall
        sectors,  # blanket
        None,  # rear wall, not split so it stays a continuous ring
    ],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=rotation_angle,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_toroidal_sectors.step")
print("Saved as tokamak_from_plasma_with_toroidal_sectors.step")

# toroidal_build can be combined with poloidal_build on the same layer, each
# poloidal segment is then split into the toroidal sectors. Here the first
# wall is split into a grid of tiles, rows going poloidally around the plasma
# and columns going toroidally around the reactor, giving names such as
# layer_3_tile_row_2_tile_column_5
poloidal_arc = paramak.poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)
number_of_rows = 12
row_gap = 5  # gap between neighbouring rows of tiles
row_length = (poloidal_arc - number_of_rows * row_gap) / number_of_rows
tile_rows = [
    (paramak.LayerType.SOLID, row_length, "tile_row"),
    (paramak.LayerType.GAP, row_gap),
] * number_of_rows

number_of_columns = 10
column_gap = 5  # width of the gap between neighbouring columns of tiles
column_length = (toroidal_arc - number_of_columns * column_gap) / number_of_columns
tile_columns = [
    (paramak.LayerType.SOLID, column_length, "tile_column"),
    (paramak.LayerType.GAP, column_gap),
] * number_of_columns

my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[None, tile_rows, None, None],  # only the first wall is split
    toroidal_build=[None, tile_columns, None, None],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=rotation_angle,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_first_wall_tile_grid.step")
print("Saved as tokamak_from_plasma_with_first_wall_tile_grid.step")
