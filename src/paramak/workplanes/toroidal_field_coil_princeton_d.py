from __future__ import annotations

import math
import typing

import numpy as np

from ..utils import (
    create_wire_workplane_from_points,
    rotate_solid,
    validate_positive,
    validate_rotation_angle,
    validate_rotation_start_angle,
)
from ..workplanes.cutting_wedge import cutting_wedge


def _compute_inner_points(R1, R2):
    """Computes the inner curve points

    The constant tension (Princeton D) curve has
    dz/dr = -ln(r / r0) / sqrt(k**2 - ln(r / r0)**2) with r0 = sqrt(R1 * R2)
    and k = ln(R2 / R1) / 2, which has a vertical tangent at R1 and R2.
    Substituting r = r0 * exp(k * sin(phi)) gives the smooth integrand
    dz/dphi = -r0 * k * sin(phi) * exp(k * sin(phi)), so the height is found
    by integrating that from the top of the curve (phi = 0) without an ODE
    solver.

    Args:
        R1 (float): smallest radius (cm)
        R2 (float): largest radius (cm)

    Returns:
        (list, list): R and Z lists for the inner curve points
    """
    R0 = (R1 * R2) ** 0.5
    k = 0.5 * np.log(R2 / R1)

    def drop_from_top(r):
        """height of the top of the curve above the curve at radius r"""
        phi = np.arcsin(np.clip(np.log(r / R0) / k, -1.0, 1.0))
        grid = np.linspace(0.0, phi, 2001)
        values = np.sin(grid) * np.exp(k * np.sin(grid))
        # trapezoidal rule, written out as np.trapezoid needs numpy 2
        return R0 * k * np.sum((values[1:] + values[:-1]) * np.diff(grid)) / 2

    # the curve is at z=0 where it meets the outboard leg at R2
    z_0 = drop_from_top(R2)

    def get_segment(a, b, num=5):
        a_R = np.linspace(a, b, num=num, endpoint=True)
        return a_R, np.array([z_0 - drop_from_top(r) for r in a_R])

    # compute inner and outer segments
    segment1 = get_segment(R0, R1)
    segment2 = get_segment(R0, R2)

    r_values = np.concatenate(
        [
            np.flip(segment1[0]),
            segment2[0][1:],
            np.flip(segment2[0])[1:],
            segment1[0][1:],
        ]
    )
    z_values = np.concatenate(
        [
            np.flip(segment1[1]),
            segment2[1][1:],
            -np.flip(segment2[1])[1:],
            -segment1[1][1:],
        ]
    )
    return r_values, z_values


def add_thickness(
    x: list[float],
    y: list[float],
    thickness: float,
    dy_dx: list[float] | None = None,
) -> tuple[list, list]:
    """Computes outer curve points based on thickness

    Args:
        x (list): list of floats containing x values
        y (list): list of floats containing y values
        thickness (float): thickness of the magnet
        dy_dx (list): list of floats containing the first order
            derivatives

    Returns:
        R and Z lists for outer curve points
    """

    if dy_dx is None:
        dy_dx = np.diff(y) / np.diff(x)

    x_outer, y_outer = [], []
    for i in range(len(dy_dx)):
        if dy_dx[i] == float("-inf"):
            nx, ny = -1, 0
        elif dy_dx[i] == float("inf"):
            nx, ny = 1, 0
        else:
            nx = -dy_dx[i]
            ny = 1
        if i != len(dy_dx) - 1:
            if x[i] < x[i + 1]:
                convex = False
            else:
                convex = True

        if convex:
            nx *= -1
            ny *= -1
        # normalize normal vector
        normal_vector_norm = (nx**2 + ny**2) ** 0.5
        nx /= normal_vector_norm
        ny /= normal_vector_norm
        # calculate outer points
        val_x_outer = x[i] + thickness * nx
        val_y_outer = y[i] + thickness * ny
        x_outer.append(val_x_outer)
        y_outer.append(val_y_outer)

    return x_outer, y_outer


def find_points(R1, R2, thickness, vertical_displacement):
    """Finds the XZ points joined by connections that describe the 2D
    profile of the toroidal field coil shape."""
    # compute inner points
    r_inner, z_inner = _compute_inner_points(R1 + thickness, R2)

    # compute outer points
    dz_dr = np.diff(z_inner) / np.diff(r_inner)
    dz_dr[0] = float("-inf")
    dz_dr = np.append(dz_dr, float("inf"))
    r_outer, z_outer = add_thickness(r_inner, z_inner, thickness, dy_dx=dz_dr)
    r_outer, z_outer = np.flip(r_outer), np.flip(z_outer)

    # add vertical displacement
    z_outer += vertical_displacement
    z_inner += vertical_displacement

    # extract helping points for inner leg
    inner_leg_connection_points = [
        (r_inner[0], z_inner[0]),
        (r_inner[-1], z_inner[-1]),
        (r_outer[0], z_outer[0]),
        (r_outer[-1], z_outer[-1]),
    ]

    # add connections
    inner_points = [[r, z, "spline"] for r, z in zip(r_inner, z_inner)]
    outer_points = [[r, z, "spline"] for r, z in zip(r_outer, z_outer)]

    inner_points[-1][2] = "straight"
    outer_points[-1][2] = "straight"

    points = inner_points + outer_points
    outer_points = np.vstack((r_outer, z_outer)).T
    inner_points = np.vstack((r_inner, z_inner)).T

    return points, inner_leg_connection_points, inner_points, outer_points


def toroidal_field_coil_princeton_d(
    r1: float = 100,
    r2: float = 300,
    thickness: float = 30,
    distance: float = 20,
    rotation_angle: float = 360.0,
    rotation_start_angle: float = 0.0,
    name: str = "toroidal_field_coil",
    with_inner_leg: bool = True,
    azimuthal_placement_angles: typing.Sequence[float] | None = None,
    vertical_displacement: float = 0.0,
    color: tuple[float, float, float, float | None] = (0.0, 0.0, 1.0),
    plane: str = "XZ",
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    obj=None,
):
    """
    Creates a toroidal field coil with a Princeton-D shape.

    Args:
        r1 (float, optional): Inner radius of the coil, the inner face of the inner leg. Defaults to 100.
        r2 (float, optional): Radius of the inner face of the outer leg, the coil extends to
            r2 + thickness. Must be greater than r1 + thickness. Defaults to 300.
        thickness (float, optional): Thickness of the coil. Defaults to 30.
        distance (float, optional): Distance to extrude the coil. Defaults to 20.
        rotation_angle (float): angle of rotation in degrees, this cuts the resulting shape with a wedge. Useful for sector models.
        rotation_start_angle (float): the angle in degrees the wedge that cuts the shape starts
            from, measured around the Z axis from the XZ plane, so the sector kept covers
            rotation_start_angle to rotation_start_angle + rotation_angle. The coils are
            still placed at azimuthal_placement_angles. Must be between -360 and 360.
            Defaults to 0.
        name (str, optional): Name of the coil. Defaults to "toroidal_field_coil".
        with_inner_leg (bool, optional): Whether to include the inner leg of the coil. Defaults to True.
        azimuthal_placement_angles (typing.Sequence[float], optional): Angles for azimuthal placement. Defaults to [0].
        vertical_displacement (float, optional): Vertical displacement of the coil. Defaults to 0.0.
        color (typing.Tuple[float, float, float, typing.Optional[float]], optional): Color of the coil. Defaults to (0.0, 0.0, 1.0).
        plane (str, optional): Plane in which to create the coil. Defaults to "XZ".
        origin (typing.Tuple[float, float, float], optional): Origin point for the coil. Defaults to (0.0, 0.0, 0.0).
        obj (optional): Existing object to modify. Defaults to None.

    Returns:
        solid: The created toroidal field coil solid.
    """
    validate_rotation_angle(rotation_angle)
    validate_positive(r1, "r1")
    validate_positive(r2, "r2")
    validate_positive(thickness, "thickness")
    if r2 <= r1 + thickness:
        raise ValueError(
            f"r2 ({r2}) must be greater than r1 + thickness ({r1 + thickness}), as the inner surface of the "
            "coil runs from r1 + thickness to r2."
        )
    validate_positive(distance, "distance")
    validate_rotation_start_angle(rotation_start_angle)
        
    if azimuthal_placement_angles is None:
        azimuthal_placement_angles = [0]
    points, inner_leg_connection_points, _inner_points, _outer_points = find_points(
        r1, r2, thickness, vertical_displacement
    )
    # need to get square end, it appears to miss the last point in the solid, TODO fix so this append is not needed
    points.append(points[-1])
    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)
    solid = wire.extrude(until=distance / 2, both=True)
    solid = rotate_solid(angles=azimuthal_placement_angles, solid=solid)

    if with_inner_leg:
        inner_leg_connection_points = [(x, z, "straight") for x, z in inner_leg_connection_points]
        # need to get square end, it appears to miss the last point in the solid, TODO fix so this append is not needed
        inner_leg_connection_points.append(inner_leg_connection_points[-1])
        inner_wire = create_wire_workplane_from_points(
            points=inner_leg_connection_points, plane=plane, origin=origin, obj=obj
        )
        inner_solid = inner_wire.extrude(until=distance / 2, both=True)
        inner_solid = rotate_solid(angles=azimuthal_placement_angles, solid=inner_solid)
        solid = solid.union(inner_solid)

    if rotation_angle < 360.0:
        bb = solid.val().BoundingBox()
        # the coils can be at any azimuthal angle, including negative x and y, so the wedge
        # radius is the largest distance from the Z axis the bounding box allows. The wedge
        # is made larger than the coils to ensure a clean cut.
        radius = math.hypot(max(abs(bb.xmin), abs(bb.xmax)), max(abs(bb.ymin), abs(bb.ymax))) * 2.1
        height = max(abs(bb.zmin), abs(bb.zmax)) * 2.1
        cutting_shape = cutting_wedge(
            height=height,
            radius=radius,
            rotation_angle=rotation_angle,
            rotation_start_angle=rotation_start_angle,
            origin=origin,
        )
        solid = solid.intersect(cutting_shape)

    solid.name = name
    solid.color = color
    return solid
