import typing

import numpy as np

from ..utils import create_wire_workplane_from_points


def plasma_simplified(
    elongation: float = 2.0,
    major_radius: float = 450.0,
    minor_radius: float = 150.0,
    triangularity: float = 0.55,
    vertical_displacement: float = 0.0,
    num_points: float = 50,
    name: str = "tokamak_plasma",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.333,
        0.0,
        0.0,
    ),
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
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
    """

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
        solid1 = wire.revolve(180, (1, 0, 0), (1, 1, 0))
        solid2 = solid1.mirror(solid1.faces(">X"), union=True)
        solid = solid2.union(solid1)  # todo try fuzzy bool tol=0.01
    else:
        solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = color
    return solid
