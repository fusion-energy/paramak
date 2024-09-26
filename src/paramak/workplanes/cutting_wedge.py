import typing

import cadquery as cq

from ..utils import create_wire_workplane_from_points


def cutting_wedge(
    height: float,
    radius: float,
    rotation_angle: float = 180.0,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.0,
        0.333,
        0.0,
    ),
    name="cutting_wedge",
):
    """Creates a wedge from height, radius and rotation angle arguments than
    can be useful for cutting sector models.

    Args:
        height: the vertical (z axis) height of the coil (cm).
        radius: the horizontal (x axis) width of the coil (cm).
        rotation_angle: Defaults to 180.0.
    """

    points = [
        (0, height / 2, "straight"),
        (radius, height / 2, "straight"),
        (radius, -height / 2, "straight"),
        (0, -height / 2, "straight"),
    ]
    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = cq.Color(*color)
    return solid
