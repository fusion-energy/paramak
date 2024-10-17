import math
import numbers
import typing

import cadquery as cq

from ..utils import create_wire_workplane_from_points
from ..workplanes.cutting_wedge import cutting_wedge


def constant_thickness_dome(
    thickness: float = 10,
    chord_center_height: float = 0,
    chord_width: float = 100,
    chord_height: float = 20,
    upper_or_lower: str = "upper",
    name: str = "constant_thickness_dome",
    plane="XZ",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.0,
        0.333,
        0.0,
    ),
    origin=(0, 0, 0),
    rotation_angle=90,
    obj=None,
    **kwargs,
):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange. The
    dished shape is made from a chord of a circle.

    Arguments:
        thickness: the radial thickness of the dome.
        chord_center_height: the vertical position of the chord center
        chord_width: the width of the chord base
        chord_height: the height of the chord which is also distance between
            the chord_center_height and the inner surface of the dome
        upper_or_lower: Curves the dish with a positive or negative direction
            to allow the upper section or lower section of vacuum vessel
            domes to be made.
        name: the name of the shape, used in the graph legend and as a
            filename prefix when exporting.
    """

    if not isinstance(chord_width, numbers.Number):
        raise ValueError("ConstantThicknessDome.chord_width must be a float. Not", chord_width)
    if chord_width <= 0:
        msg = f"ConstantThicknessDome.chord_width must be a positive number above 0. Not {chord_width}"
        raise ValueError(msg)

    if not isinstance(chord_height, numbers.Number):
        raise ValueError("ConstantThicknessDome.chord_height must be a float. Not", chord_height)
    if chord_height <= 0:
        msg = f"ConstantThicknessDome.chord_height must be a positive number above 0. Not {chord_height}"
        raise ValueError(msg)

    if not isinstance(thickness, numbers.Number):
        msg = f"VacuumVessel.thickness must be a float. Not {thickness}"
        raise ValueError(msg)
    if thickness <= 0:
        msg = f"VacuumVessel.thickness must be a positive number above 0. Not {thickness}"
        raise ValueError(msg)

    # Note these points are not used in the normal way when constructing
    # the solid
    #
    #          6   -
    #          |       -
    #          7  -       -
    #                -       -
    #                  -       3
    #                    -     |
    #         cc          1 -- 2
    #     chord center
    #
    #
    #          cp
    #     center point
    #
    #
    #
    #
    #         cc           1 -- 2
    #                    -      |
    #                  -        3
    #                -       -
    #          7  -       -
    #          |       -
    #          6   -
    #       far side

    if chord_height * 2 >= chord_width:
        msg = "ConstantThicknessDome requires that the chord_width " "is at least 2 times as large as the chord height"
        raise ValueError(msg)

    radius_of_sphere = ((math.pow(chord_width, 2)) + (4.0 * math.pow(chord_height, 2))) / (8 * chord_height)

    # TODO set to 0 for now, add ability to shift the center of the chord left and right
    chord_center = (0, chord_center_height)

    point_1 = (chord_center[0] + (chord_width / 2), chord_center[1], "straight")

    if upper_or_lower == "upper":
        center_point = (chord_center[0], chord_center[1] + chord_height - radius_of_sphere)
        inner_tri_angle = math.atan((center_point[1] - chord_center[1]) / (chord_width / 2))
        outer_tri_adj = math.cos(inner_tri_angle) * thickness
        point_2 = (point_1[0] + thickness, point_1[1], "straight")
        outer_tri_opp = math.sqrt(math.pow(thickness, 2) - math.pow(outer_tri_adj, 2))
        point_7 = (chord_center[0], chord_center[1] + radius_of_sphere, "straight")
        point_6 = (chord_center[0], chord_center[1] + radius_of_sphere + thickness, "straight")
        far_side = (center_point[0], center_point[1] - (radius_of_sphere + thickness))
        point_3 = (point_2[0], point_2[1] + outer_tri_opp, "straight")
    elif upper_or_lower == "lower":
        center_point = (chord_center[0], chord_center[1] - chord_height + radius_of_sphere)
        inner_tri_angle = math.atan((center_point[1] - chord_center[1]) / (chord_width / 2))
        outer_tri_adj = math.cos(inner_tri_angle) * thickness
        point_2 = (point_1[0] + thickness, point_1[1], "straight")
        outer_tri_opp = math.sqrt(math.pow(thickness, 2) - math.pow(outer_tri_adj, 2))
        point_7 = (chord_center[0], chord_center[1] - radius_of_sphere, "straight")
        point_6 = (chord_center[0], chord_center[1] - (radius_of_sphere + thickness), "straight")
        far_side = (center_point[0], center_point[1] + radius_of_sphere + thickness)
        point_3 = (point_2[0], point_2[1] - outer_tri_opp, "straight")
    else:
        msg = f'upper_or_lower should be either "upper"  or "lower". Not {upper_or_lower}'
        raise ValueError(msg)

    points = [point_1, point_2, point_3, point_6, point_7]

    radius_of_sphere = ((math.pow(chord_width, 2)) + (4.0 * math.pow(chord_height, 2))) / (8 * chord_height)

    # TODO set to 0 for now, add ability to shift the center of the chord left and right
    chord_center = (0, chord_center_height)

    # far_side is center on x and
    if upper_or_lower == "upper":
        center_point = (chord_center[0], chord_center[1] + chord_height - radius_of_sphere)
        far_side = (center_point[0], center_point[1] - (radius_of_sphere + thickness))
    elif upper_or_lower == "lower":
        center_point = (chord_center[0], chord_center[1] - chord_height + radius_of_sphere)
        far_side = (center_point[0], center_point[1] + radius_of_sphere + thickness)
    else:
        raise ValueError("upper_or_lower argument must be set to either 'upper' or 'lower'")

    big_sphere = cq.Workplane(plane).moveTo(center_point[0], center_point[1]).sphere(radius_of_sphere + thickness)

    small_sphere = cq.Workplane(plane).moveTo(center_point[0], center_point[1]).sphere(radius_of_sphere)

    wire = create_wire_workplane_from_points(
        points=(
            (chord_center[0], chord_center[1], "straight"),
            (chord_center[0] + radius_of_sphere + thickness, chord_center[1], "straight"),
            (chord_center[0] + radius_of_sphere + thickness, far_side[1], "straight"),
            (chord_center[0], far_side[1], "straight"),
            (chord_center[0], chord_center[1], "straight"),
        ),
        plane=plane,
        origin=origin,
        obj=obj,
    )
    inner_cylinder_cutter = wire.revolve(360)

    wire = create_wire_workplane_from_points(
        points=(
            (chord_center[0], chord_center[1], "straight"),  # cc
            (points[1][0], points[1][1], "straight"),  # point 2
            (points[2][0], points[2][1], "straight"),  # point 3
            (points[2][0] + radius_of_sphere, points[2][1], "straight"),  # point 3 wider
            (points[2][0] + radius_of_sphere, far_side[1], "straight"),
            (far_side[0], far_side[1], "straight"),
            (chord_center[0], far_side[1], "straight"),
        ),
        plane=plane,
        origin=origin,
        obj=obj,
    )
    outer_cylinder_cutter = wire.revolve(360)

    cap = big_sphere.cut(small_sphere)

    height = 2 * (radius_of_sphere + abs(center_point[1]) + thickness)
    radius = 2 * (radius_of_sphere + abs(center_point[0]) + thickness)
    cutter = cutting_wedge(height=height, radius=radius, rotation_angle=rotation_angle, plane=plane)

    cap = cap.cut(outer_cylinder_cutter).cut(inner_cylinder_cutter)
    cap = cap.intersect(cutter)

    cap.name = name
    cap.color = cq.Color(*color)
    return cap
