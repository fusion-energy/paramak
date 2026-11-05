from __future__ import annotations

import numpy as np

from ..utils import (
    create_wire_workplane_from_points,
    rotate_to_rotation_start_angle,
    validate_positive,
    validate_positive_integer,
    validate_rotation_angle,
)


def plasma_simplified(
    elongation: float = 2.0,
    major_radius: float = 450.0,
    minor_radius: float = 150.0,
    triangularity: float = 0.55,
    vertical_displacement: float = 0.0,
    num_points: int = 200,
    name: str = "tokamak_plasma",
    color: tuple[float, float, float, float | None] = (
        0.333,
        0.0,
        0.0,
    ),
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    rotation_start_angle: float = 0.0,
):
    """Creates a double null tokamak plasma shape that is controlled by 4
    shaping parameters.

    Args:
        elongation: the elongation of the plasma.
        major_radius: the major radius of the plasma (cm).
        minor_radius: the minor radius of the plasma (cm).
        triangularity: the triangularity of the plasma.
        vertical_displacement: the vertical_displacement of the plasma (cm)..
        num_points: number of points to describe the shape.
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    validate_positive_integer(num_points, "num_points")
    validate_rotation_angle(rotation_angle)
    validate_positive(elongation, "elongation")
    validate_positive(major_radius, "major_radius")
    validate_positive(minor_radius, "minor_radius")
    if minor_radius >= major_radius:
        raise ValueError(f"minor_radius ({minor_radius}) must be less than major_radius ({major_radius}).")
    if not (-1.0 <= triangularity <= 1.0):
        raise ValueError(f"triangularity must be between -1 and 1, got {triangularity}.")

    # create array of angles theta
    theta = np.linspace(0, 2 * np.pi, num=num_points, endpoint=False)

    # parametric equations for plasma
    def R(theta):
        return major_radius + minor_radius * np.cos(theta + triangularity * np.sin(theta))

    def Z(theta):
        return elongation * minor_radius * np.sin(theta) + vertical_displacement

    points = np.stack((R(theta), Z(theta)), axis=1).tolist()
    points.append(points[0])
    for point in points:
        point.append("spline")

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    # avoids shape with surface on join that can't be meshed for 360 degree plasmas
    if rotation_angle >= 360:
        solid1 = wire.revolve(180, (0, 0, 0), (0, 1, 0))
        solid2 = solid1.mirror(solid1.faces(">X"), union=True)
        solid = solid2.union(solid1)  # todo try fuzzy bool tol=0.01
    else:
        solid = wire.revolve(rotation_angle)
    solid = rotate_to_rotation_start_angle(solid, wire, rotation_start_angle)
    solid.name = name
    solid.color = color
    return solid
