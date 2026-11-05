from __future__ import annotations


from ..utils import (
    create_wire_workplane_from_points,
    rotate_to_rotation_start_angle,
    validate_positive,
    validate_rotation_angle,
)


def cutting_wedge(
    height: float,
    radius: float,
    rotation_angle: float = 180.0,
    rotation_start_angle: float = 0.0,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    color: tuple[float, float, float, float | None] = (
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
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    validate_positive(height, "height")
    validate_positive(radius, "radius")
    validate_rotation_angle(rotation_angle)

    points = [
        (0, height / 2, "straight"),
        (radius, height / 2, "straight"),
        (radius, -height / 2, "straight"),
        (0, -height / 2, "straight"),
    ]
    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(
        angleDegrees=rotation_angle,
    )
    solid = rotate_to_rotation_start_angle(solid, wire, rotation_start_angle)
    solid.name = name
    solid.color = color
    return solid
