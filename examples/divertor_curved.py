"""Builds a curved lower divertor and intersects it into a tokamak.

Demonstrates building a divertor with the shape-based `extra_intersect_shapes`
workflow plus the `paramak.revolved_shape` helper, which revolves an arbitrary
2D profile and builds the same smooth spline/arc profiles used internally for
the blankets and domes (instead of a blocky rectangle).
"""

import cadquery as cq

import paramak

# Divertor cross-section in the XZ plane. The third element of each point is
# the connection type: "straight", "spline" or "circle". Using splines gives
# a smooth curved profile instead of a blocky rectangle.
# Do not repeat the first point; revolved_shape closes the profile for you.
points = [
    (300, -700, "straight"),
    (300, -300, "spline"),  # inner vertical target
    (370, -180, "spline"),  # curve toward the dome
    (470, -240, "spline"),  # dome
    (560, -180, "spline"),  # outer vertical target
    (600, -700, "straight"),
]

divertor_lower = paramak.revolved_shape(points=points, rotation_angle=180, plane="XZ")

# Save the divertor shape on its own.
cq.exporters.export(divertor_lower, "divertor.step")
print("Saved divertor.step")

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
print("Saved tokamak_with_divertor.step")
