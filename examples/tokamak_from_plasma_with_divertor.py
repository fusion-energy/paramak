from cadquery import Workplane

import paramak

# makes a rectangle that overlaps the lower blanket under the plasma
# the intersection of this and the layers will form the lower divertor
points = [(300, -700), (300, 0), (400, 0), (400, -700)]
divertor_lower = Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)


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
    extra_intersect_shapes=[divertor_lower],
)
my_reactor.save("tokamak_with_divertor.step")
print("Saved as tokamak_with_divertor.step")

