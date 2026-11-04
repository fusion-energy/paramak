from __future__ import annotations

from ..utils import (
    create_wire_workplane_from_points,
    rotate_to_rotation_start_angle,
    validate_positive,
    validate_rotation_angle,
)


def poloidal_field_coil_case(
    coil_height: float,
    coil_width: float,
    casing_thickness: tuple[float, float],
    center_point: tuple[float, float],
    name: str = "poloidal_field_coil_case",
    color: tuple[float, float, float, float | None] = (1.0, 1.0, 0.498),
    rotation_angle=90,
    rotation_start_angle: float = 0.0,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
):
    """Constant thickness casing for a rectangular poloidal coil.

    Args:
        coil_height: the vertical (z axis) height of the coil (cm).
        coil_width: the horizontal (x axis) width of the coil (cm).
        center_point: the center of the coil (x,z) values (cm).
        casing_thickness: the thickness of the coil casing (cm).
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    validate_positive(casing_thickness, "casing_thickness")
    validate_rotation_angle(rotation_angle)
    validate_positive(coil_height, "coil_height")
    validate_positive(coil_width, "coil_width")

    inner_points = [
        (center_point[0] + coil_width / 2.0, center_point[1] + coil_height / 2.0, "straight"),  # upper right
        (center_point[0] + coil_width / 2.0, center_point[1] - coil_height / 2.0, "straight"),  # lower right
        (center_point[0] - coil_width / 2.0, center_point[1] - coil_height / 2.0, "straight"),  # lower left
        (center_point[0] - coil_width / 2.0, center_point[1] + coil_height / 2.0, "straight"),  # upper left
    ]
    inner_points.append(inner_points[0])

    outer_points = [
        (
            center_point[0] + (casing_thickness + coil_width / 2.0),
            center_point[1] + (casing_thickness + coil_height / 2.0),
            "straight",
        ),
        (
            center_point[0] + (casing_thickness + coil_width / 2.0),
            center_point[1] - (casing_thickness + coil_height / 2.0),
            "straight",
        ),
        (
            center_point[0] - (casing_thickness + coil_width / 2.0),
            center_point[1] - (casing_thickness + coil_height / 2.0),
            "straight",
        ),
        (
            center_point[0] - (casing_thickness + coil_width / 2.0),
            center_point[1] + (casing_thickness + coil_height / 2.0),
            "straight",
        ),
    ]
    outer_points.append(outer_points[0])

    inner_wire = create_wire_workplane_from_points(points=inner_points, plane=plane, origin=origin, obj=obj)
    outer_wire = create_wire_workplane_from_points(points=outer_points, plane=plane, origin=origin, obj=obj)

    inner_solid = inner_wire.revolve(rotation_angle)
    solid = outer_wire.revolve(rotation_angle).cut(inner_solid)
    solid = rotate_to_rotation_start_angle(solid, outer_wire, rotation_start_angle)
    solid.name = name
    solid.color = color
    return solid
