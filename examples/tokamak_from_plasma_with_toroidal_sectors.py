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

# Six sectors separated by gaps. Gaps have parallel sides, so a 20 cm gap is
# 20 cm wide at every radius.
number_of_sectors = 6
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
        sectors,  # rear wall
    ],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=rotation_angle,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_toroidal_sectors.step")
print("Saved as tokamak_from_plasma_with_toroidal_sectors.step")

# toroidal_build can be combined with poloidal_build, each poloidal module is
# then split into the toroidal sectors, giving names such as
# layer_4_module_2_sector_3
poloidal_arc = paramak.poloidal_arc_length(radial_build, elongation=2.0, triangularity=0.55)
number_of_modules = 4
module_gap = 20  # gap between neighbouring modules
module_length = (poloidal_arc - number_of_modules * module_gap) / number_of_modules
modules = [
    (paramak.LayerType.SOLID, module_length, "module"),
    (paramak.LayerType.GAP, module_gap),
] * number_of_modules

my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=[None, None, modules, None],
    toroidal_build=[None, None, sectors, None],
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=rotation_angle,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_poloidal_and_toroidal_segments.step")
print("Saved as tokamak_from_plasma_with_poloidal_and_toroidal_segments.step")
