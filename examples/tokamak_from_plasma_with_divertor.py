import paramak
from cad_to_dagmc import CadToDagmc

my_reactor = paramak.tokamak_from_plasma(
    radial_build=[
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
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
)

my_reactor = my_reactor.add_divertor(
    poloidal_start_angle=75,
    poloidal_extent_angle=30,
    divertor_layer_names=["lower_divertor_armor", "lower_divertor_heatsink", "lower_divertor_shield"],
    divertor_layer_thicknesses=[10, 30, 50],
)
my_reactor.export("tokamak_with_divertor.step")
print("Saved as tokamak_with_divertor.step")



