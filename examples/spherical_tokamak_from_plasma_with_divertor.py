from cadquery import Workplane

import paramak

# makes a rectangle that overlaps the lower blanket under the plasma
# the intersection of this and the layers will form the lower divertor
points = [(150, -700), (150, 0), (270, 0), (270, -700)]
divertor_lower = Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)

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
    extra_intersect_shapes=[divertor_lower],
)
my_reactor.save("spherical_tokamak_from_plasma_with_divertor.step")
print("written spherical_tokamak_from_plasma_with_divertor.step")
