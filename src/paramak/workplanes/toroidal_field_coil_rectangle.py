from __future__ import annotations

import math
import typing

from ..utils import (
    create_wire_workplane_from_points,
    rotate_solid,
    validate_positive,
    validate_rotation_angle,
    validate_rotation_start_angle,
)
from ..workplanes.cutting_wedge import cutting_wedge


def toroidal_field_coil_rectangle(
    horizontal_start_point: tuple[float, float] = (20, 200),
    vertical_mid_point: tuple[float, float] = (350, 0),
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
    """Creates a rectangular shaped toroidal field coil.

    Args:
        horizontal_start_point: the (x,z) coordinates of the inner upper
            point (cm).
        vertical_mid_point: the (x,z) coordinates of the mid point of the
            vertical section (cm). The coil is symmetric about this height,
            so the bottom is the horizontal_start_point mirrored about it.
        thickness: the thickness of the toroidal field coil.
        distance: the extrusion distance.
        rotation_angle (float): angle of rotation in degrees, this cuts the resulting shape with a wedge. Useful for sector models.
        rotation_start_angle (float): the angle in degrees the wedge that cuts the shape starts
            from, measured around the Z axis from the XZ plane, so the sector kept covers
            rotation_start_angle to rotation_start_angle + rotation_angle. The coils are
            still placed at azimuthal_placement_angles. Must be between -360 and 360.
            Defaults to 0.
        name: the name of the coil. Defaults to "toroidal_field_coil".
        with_inner_leg: include the inner tf leg. Defaults to True.
        azimuthal_placement_angles: the angles in degrees around the Z axis to
            place a coil at. Defaults to [0].
        vertical_displacement: the vertical distance to move the coil (cm).
            Defaults to 0.
        color: the RGB(A) color of the coil. Defaults to (0.0, 0.0, 1.0).
        plane: the plane the coil profile is drawn on. Defaults to "XZ".
        origin: the origin of the workplane. Defaults to (0.0, 0.0, 0.0).
        obj: an optional existing CadQuery object to build upon.
    """
    validate_rotation_angle(rotation_angle)
    validate_positive(thickness, "thickness")
    validate_positive(distance, "distance")
    validate_rotation_start_angle(rotation_start_angle)

    if azimuthal_placement_angles is None:
        azimuthal_placement_angles = [0]
    if horizontal_start_point[0] >= vertical_mid_point[0]:
        raise ValueError(
            "horizontal_start_point x should be smaller than the \
                vertical_mid_point x value"
        )
    if vertical_mid_point[1] >= horizontal_start_point[1]:
        raise ValueError(
            "vertical_mid_point y value should be smaller than the \
                horizontal_start_point y value"
        )

    # the coil is symmetric about the height of the vertical_mid_point, so the
    # bottom is the top mirrored about that height
    bottom = 2 * vertical_mid_point[1] - horizontal_start_point[1]

    points = [
        horizontal_start_point,  # connection point
        (
            horizontal_start_point[0] + thickness,
            horizontal_start_point[1],
        ),
        (vertical_mid_point[0], horizontal_start_point[1]),
        (vertical_mid_point[0], bottom),
        # connection point
        (
            horizontal_start_point[0] + thickness,
            bottom,
        ),
        # connection point
        (horizontal_start_point[0], bottom),
        (
            horizontal_start_point[0],
            bottom - thickness,
        ),
        (
            vertical_mid_point[0] + thickness,
            bottom - thickness,
        ),
        (
            vertical_mid_point[0] + thickness,
            horizontal_start_point[1] + thickness,
        ),
        (
            horizontal_start_point[0],
            horizontal_start_point[1] + thickness,
        ),
        horizontal_start_point,
    ]

    # adds any vertical displacement and the connection type to the points
    points = [(point[0], point[1] + vertical_displacement, "straight") for point in points]

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)
    solid = wire.extrude(until=distance / 2, both=True)
    solid = rotate_solid(angles=azimuthal_placement_angles, solid=solid)

    if with_inner_leg:
        inner_leg_connection_points = [
            (points[0][0], points[0][1], "straight"),
            (points[1][0], points[1][1], "straight"),
            (points[4][0], points[4][1], "straight"),
            (points[5][0], points[5][1], "straight"),
            (points[0][0], points[0][1], "straight"),
        ]
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
        radius = math.hypot(max(abs(bb.xmin), abs(bb.xmax)), max(abs(bb.ymin), abs(bb.ymax))) * 1.1
        height = max(abs(bb.zmin), abs(bb.zmax)) * 2.1
        cutting_shape = cutting_wedge(
            height=height,
            radius=radius,
            rotation_angle=rotation_angle,
            rotation_start_angle=rotation_start_angle,
        )
        solid = solid.intersect(cutting_shape)

    solid.name = name
    solid.color = color
    return solid
