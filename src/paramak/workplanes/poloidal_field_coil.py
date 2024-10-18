import typing

from ..utils import create_wire_workplane_from_points


def poloidal_field_coil(
    height: float,
    width: float,
    center_point: float,
    name: str = "poloidal_field_coil",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.0,
        0.333,
        0.0,
    ),
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
):
    """A rectangular poloidal field coil.

    Args:
        height: the vertical (z axis) height of the coil.
        width: the horizontal (x axis) width of the coil.
        center_point: the center of the coil (x,z) values.
    """

    points = [
        (center_point[0] + width / 2.0, center_point[1] + height / 2.0, "straight"),  # upper right
        (center_point[0] + width / 2.0, center_point[1] - height / 2.0, "straight"),  # lower right
        (center_point[0] - width / 2.0, center_point[1] - height / 2.0, "straight"),  # lower left
        (center_point[0] - width / 2.0, center_point[1] + height / 2.0, "straight"),
    ]

    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = color
    return solid
