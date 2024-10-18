import typing

from ..utils import create_wire_workplane_from_points


def center_column_shield_cylinder(
    height: float,
    inner_radius: float,
    thickness: float,
    reference_point: tuple = ("center", 0),
    name: str = "center_column_shield_cylinder",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.0,
        0.333,
        0.0,
    ),
    rotation_angle=90,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
):
    """A cylindrical center column shield volume with constant thickness.

    Args:
        height: height of the center column shield.
        inner_radius: the inner radius of the center column shield.
        thickness: the outer radius of the center column shield.
        reference_point: the vertical coordinates to build te vessel from and
            description of the reference point. Can be either the 'center'
            with a numerical value or 'lower' with a numerical value.
    """

    outer_radius = inner_radius + thickness

    if reference_point[0] == "center":
        center_height = reference_point[1]
    elif reference_point[0] == "lower":
        center_height = reference_point[1] + 0.5 * height
    else:
        raise ValueError('reference_point should be a tuple where the first value is either "center" or "lower"')

    if not isinstance(center_height, (int, float)):
        msg = f"center_height should be a float or int. Not a {type(center_height)}"
        raise TypeError(msg)

    points = [
        (inner_radius, center_height + height / 2, "straight"),
        (outer_radius, center_height + height / 2, "straight"),
        (outer_radius, center_height + (-height / 2), "straight"),
        (inner_radius, center_height + (-height / 2), "straight"),
    ]

    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = color
    return solid
