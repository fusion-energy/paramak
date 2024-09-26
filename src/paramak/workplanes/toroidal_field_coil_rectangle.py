import typing

from ..utils import create_wire_workplane_from_points, rotate_solid


def toroidal_field_coil_rectangle(
    horizontal_start_point: typing.Tuple[float, float] = (20, 200),
    vertical_mid_point: typing.Tuple[float, float] = (350, 0),
    thickness: float = 30,
    distance: float = 20,
    name: str = "toroidal_field_coil",
    with_inner_leg: bool = True,
    azimuthal_placement_angles: typing.Sequence[float] = [0, 90, 180],
    vertical_displacement: float = 0.0,
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (0.0, 0.0, 1.0),
    plane: str = "XZ",
    origin: typing.Tuple[float, float, float] = (0.0, 0.0, 0.0),
    obj=None,
):
    """Creates a rectangular shaped toroidal field coil.

    Args:
        horizontal_start_point: the (x,z) coordinates of the inner upper
            point (cm).
        vertical_mid_point: the (x,z) coordinates of the mid point of the
            vertical section (cm).
        thickness: the thickness of the toroidal field coil.
        distance: the extrusion distance.
        number_of_coils: the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        with_inner_leg: include the inner tf leg. Defaults to True.
        azimuth_start_angle: The azimuth angle to for the first TF coil which
            offsets the placement of coils around the azimuthal angle
    """

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

    points = [
        horizontal_start_point,  # connection point
        (
            horizontal_start_point[0] + thickness,
            horizontal_start_point[1],
        ),
        (vertical_mid_point[0], horizontal_start_point[1]),
        (vertical_mid_point[0], -horizontal_start_point[1]),
        # connection point
        (
            horizontal_start_point[0] + thickness,
            -horizontal_start_point[1],
        ),
        # connection point
        (horizontal_start_point[0], -horizontal_start_point[1]),
        (
            horizontal_start_point[0],
            -(horizontal_start_point[1] + thickness),
        ),
        (
            vertical_mid_point[0] + thickness,
            -(horizontal_start_point[1] + thickness),
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

    solid.name = name
    solid.color = color
    return solid
