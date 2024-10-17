import typing

import cadquery as cq

from ..utils import create_wire_workplane_from_points


def blanket_constant_thickness_arc_h(
    inner_mid_point: typing.Tuple[float, float],
    inner_upper_point: typing.Tuple[float, float],
    inner_lower_point: typing.Tuple[float, float],
    thickness: float,
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.0,
        0.333,
        0.0,
    ),
    name="blanket_constant_thickness_arc_h",
):
    points = [
        (inner_upper_point[0], inner_upper_point[1], "circle"),
        (inner_mid_point[0], inner_mid_point[1], "circle"),
        (inner_lower_point[0], inner_lower_point[1], "straight"),
        (
            inner_lower_point[0] + abs(thickness),
            inner_lower_point[1],
            "circle",
        ),
        (
            inner_mid_point[0] + abs(thickness),
            inner_mid_point[1],
            "circle",
        ),
        (
            inner_upper_point[0] + abs(thickness),
            inner_upper_point[1],
            "straight",
        ),
    ]

    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = cq.Color(*color)
    return solid
