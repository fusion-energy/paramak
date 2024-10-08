import typing
import numpy as np
from ..utils import create_wire_workplane_from_points, rotate_solid
from scipy import integrate
from scipy.optimize import minimize
from typing import List, Tuple
from ..workplanes.cutting_wedge import cutting_wedge


def _compute_inner_points(R1, R2):
    """Computes the inner curve points

    Args:
        R1 (float): smallest radius (cm)
        R2 (float): largest radius (cm)

    Returns:
        (list, list, list): R, Z and derivative lists for outer curve
        points
    """

    def error(z_0, R0, R2):
        segment = get_segment(R0, R2, z_0)
        return abs(segment[1][-1])

    def get_segment(a, b, z_0,num=5):
        a_R = np.linspace(a, b, num=num, endpoint=True)
        asol = integrate.odeint(solvr, [z_0[0], 0], a_R)
        return a_R, asol[:, 0], asol[:, 1]

    def solvr(Y, R):
        return [Y[1], -1 / (k * R) * (1 + Y[1] ** 2) ** (3 / 2)]

    R0 = (R1 * R2) ** 0.5
    k = 0.5 * np.log(R2 / R1)

    # computing of z_0
    # z_0 is computed by ensuring outer segment end is zero
    z_0 = 10  # initial guess for z_0
    res = minimize(error, z_0, args=(R0, R2))
    z_0 = res.x

    # compute inner and outer segments
    segment1 = get_segment(R0, R1, z_0)
    segment2 = get_segment(R0, R2, z_0)

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


def add_thickness(x: List[float], y: List[float], thickness: float, dy_dx: List[float] = None) -> Tuple[list, list]:
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


def find_points(R1, R2, thickness,vertical_displacement):
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
    name: str = "toroidal_field_coil",
    with_inner_leg: bool = True,
    azimuthal_placement_angles: typing.Sequence[float] = [0],
    vertical_displacement: float = 0.0,
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (0.0, 0.0, 1.0),
    plane: str = "XZ",
    origin: typing.Tuple[float, float, float] = (0.0, 0.0, 0.0),
    obj=None,
):
    """
    Creates a toroidal field coil with a Princeton-D shape.

    Args:
        r1 (float, optional): Inner radius of the coil. Defaults to 100.
        r2 (float, optional): Outer radius of the coil. Defaults to 300.
        thickness (float, optional): Thickness of the coil. Defaults to 30.
        distance (float, optional): Distance to extrude the coil. Defaults to 20.
        rotation_angle (float): angle of rotation in degrees, this cuts the resulting shape with a wedge. Useful for sector models.
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
    points, inner_leg_connection_points, inner_points, outer_points = find_points(r1, r2, thickness, vertical_displacement)
    # need to get square end, it appears to miss the last point in the solid, TODO fix so this append is not needed
    points.append(points[-1])
    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)
    solid = wire.extrude(until=distance / 2, both=True)
    solid = rotate_solid(angles=azimuthal_placement_angles, solid=solid)

    if with_inner_leg:
        inner_leg_connection_points=[(x,z,'straight') for x,z in inner_leg_connection_points]
        # need to get square end, it appears to miss the last point in the solid, TODO fix so this append is not needed
        inner_leg_connection_points.append(inner_leg_connection_points[-1])
        inner_wire = create_wire_workplane_from_points(
            points=inner_leg_connection_points, plane=plane, origin=origin, obj=obj
        )
        inner_solid = inner_wire.extrude(until=distance / 2, both=True)
        inner_solid = rotate_solid(angles=azimuthal_placement_angles, solid=inner_solid)
        solid = solid.union(inner_solid)

    if rotation_angle < 360.:
        bb=solid.val().BoundingBox()
        radius = max(bb.xmax, bb.ymax)*2.1 # larger than the bounding box to ensure clean cut
        height = max(bb.zmax, bb.zmin)*2.1 # larger than the bounding box to ensure clean cut
        cutting_shape = cutting_wedge(height=height, radius=radius, rotation_angle=rotation_angle)
        solid = solid.intersect(cutting_shape)

    solid.name = name
    solid.color = color
    return solid