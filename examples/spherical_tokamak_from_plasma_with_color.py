import paramak

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
    rotation_angle=180,
    colors={
        "layer_1": (0.4, 0.9, 0.4),
        "layer_2": (0.6, 0.8, 0.6),
        "plasma": (1., 0.7, 0.8, 0.6),
        "layer_3": (0.1, 0.1, 0.9),
        "layer_4": (0.4, 0.4, 0.8),
        "layer_5": (0.5, 0.5, 0.8),
    },
)
my_reactor.save(f"spherical_tokamak_from_plasma_with_colors.step")

# show colors with built-in vtk viewer
# from cadquery.vis import show
# show(my_reactor)

# cadquery also supports svg export
# currently needs converting to compound first as svg export not supported by assembly objects
# lots of options https://cadquery.readthedocs.io/en/latest/importexport.html#exporting-svg
my_reactor.toCompound().export("spherical_tokamak_from_plasma_with_colors.svg")

# show colors with png file export using cadquery's built-in screenshot support
from cadquery.vis import show
show(my_reactor, screenshot='spherical_tokamak_from_plasma_with_colors.png', interact=False, width=1280, height=1024, zoom=1.4)

