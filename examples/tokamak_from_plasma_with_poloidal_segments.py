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
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 10),
]

# Step 1: get the poloidal arc length of the inner surface of each layer.
# The list is ordered from the plasma outwards, one entry per radial_build
# entry after the plasma, with None for gaps.
arc_lengths = paramak.poloidal_arc_lengths(radial_build, elongation=2.0, triangularity=0.55)
print(arc_lengths)

# Step 2: design the segments for the thick blanket layer (third entry after
# the plasma). Segments start at the outboard midplane and go counter
# clockwise, so this gives an upper and lower outboard module either side of
# the midplane and one inboard module, separated by 50 cm gaps.
gap = 50
blanket = arc_lengths[2] - 2 * gap
poloidal_build = [
    None,  # gap after the plasma
    None,  # first wall, not segmented
    [  # blanket
        ("outboard", blanket * 0.2),
        ("gap", gap),
        ("inboard", blanket * 0.6),
        ("gap", gap),
        ("outboard", blanket * 0.2),
    ],
    None,  # rear wall, not segmented
]

my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=poloidal_build,
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=180,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_poloidal_segments.step")
print("Saved as tokamak_from_plasma_with_poloidal_segments.step")

# Segments sized separately on each layer do not line up between layers.
# aligned_poloidal_build gives several layers the same segment boundaries so
# the gaps run straight through them. Here the first wall and blanket are
# split into eight modules with 20 cm gaps, sized on the first wall.
gap = 20
number_of_modules = 8
module = (arc_lengths[1] - number_of_modules * gap) / number_of_modules
aligned_poloidal_build = paramak.aligned_poloidal_build(
    radial_build,
    segments=[("module", module), ("gap", gap)] * number_of_modules,
    layers=[1, 2],
    elongation=2.0,
    triangularity=0.55,
)

my_reactor = paramak.tokamak_from_plasma(
    radial_build=radial_build,
    poloidal_build=aligned_poloidal_build,
    elongation=2.0,
    triangularity=0.55,
    rotation_angle=180,
)
print(my_reactor.names())
my_reactor.export("tokamak_from_plasma_with_aligned_poloidal_segments.step")
print("Saved as tokamak_from_plasma_with_aligned_poloidal_segments.step")
