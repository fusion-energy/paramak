from __future__ import annotations

from ..utils import create_wire_workplane_from_points, rotate_to_rotation_start_angle


def poloidal_field_coil(
    height: float,
    width: float,
    center_point: float,
    name: str = "poloidal_field_coil",
    color: tuple[float, float, float, float | None] = (
        0.0,
        0.333,
        0.0,
    ),
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    rotation_start_angle: float = 0.0,
):
    """A rectangular poloidal field coil.

    Args:
        height: the vertical (z axis) height of the coil.
        width: the horizontal (x axis) width of the coil.
        center_point: the center of the coil (x,z) values.
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}.")
    if width <= 0:
        raise ValueError(f"width must be positive, got {width}.")

    points = [
        (center_point[0] + width / 2.0, center_point[1] + height / 2.0, "straight"),  # upper right
        (center_point[0] + width / 2.0, center_point[1] - height / 2.0, "straight"),  # lower right
        (center_point[0] - width / 2.0, center_point[1] - height / 2.0, "straight"),  # lower left
        (center_point[0] - width / 2.0, center_point[1] + height / 2.0, "straight"),
    ]

    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid = rotate_to_rotation_start_angle(solid, wire, rotation_start_angle)
    solid.name = name
    solid.color = color
    return solid
