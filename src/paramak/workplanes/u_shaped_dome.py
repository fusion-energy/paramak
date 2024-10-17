import typing

from paramak import center_column_shield_cylinder, constant_thickness_dome

from ..utils import create_wire_workplane_from_points


def u_shaped_dome(
    radius: float = 310,
    reference_point: tuple = ("lower", 0),
    dish_height: typing.Tuple[float, float] = 50,
    cylinder_height: float = 400,
    thickness: float = 16,
    rotation_angle: float = 180,
    name: str = "u_shaped_dome",
    plane="XZ",
    upper_or_lower="upper",
):
    """A cylindrical u shaped dome with constant thickness.

    Arguments:
        radius: the radius from which the centres of the vessel meets the outer
            circumference.
        reference_point: the x,z coordinates to build te vessel from. Can be
            either the 'center' with a value or 'lower' with a
            value. For example
        dish_height: the height of the lower and upper dish sections.
        cylinder_height: the height of the cylindrical section of the vacuum
            vessel.
        thickness: the radial thickness of the vessel in cm.
    """

    if not isinstance(radius, (float, int)):
        raise ValueError(f"radius must be a number. Not {type(radius)}")
    if radius <= 0:
        msg = "radius must be a positive number above 0. " f"Not {radius}"
        raise ValueError(msg)

    if not isinstance(thickness, (float, int)):
        msg = f"VacuumVessel.thickness must be a number. Not {type(thickness)}"
        raise ValueError(msg)
    if thickness <= 0:
        msg = f"VacuumVessel.thickness must be a positive number above 0. Not {value}"
        raise ValueError(msg)

        #
        #          -   -
        #                  -
        #          -  -       -
        #                -       -
        #                  -       -
        #                    -     |
        #                     |    |
        #                     |    |
        #                     |    |
        #          c,p        |    |
        #                     |    |

    if reference_point[0] == "center":
        center_height = reference_point[1]
        lower_chord_center_height = reference_point[1] - 0.5 * cylinder_height
        upper_chord_center_height = reference_point[1] + 0.5 * cylinder_height
    elif reference_point[0] == "lower":
        center_height = reference_point[1] + thickness + dish_height + 0.5 * cylinder_height
        lower_chord_center_height = reference_point[1] + thickness + dish_height
        upper_chord_center_height = reference_point[1] + thickness + dish_height + cylinder_height
    else:
        raise ValueError('reference_point should be a tuple where the first value is either "center" or "lower"')

    cylinder_section = center_column_shield_cylinder(
        height=cylinder_height,
        inner_radius=radius - thickness,
        thickness=thickness,
        reference_point=("center", center_height),
        rotation_angle=rotation_angle,
        plane=plane,
    )

    if upper_or_lower == "upper":
        dome_section = constant_thickness_dome(
            thickness=thickness,
            chord_center_height=upper_chord_center_height,
            chord_width=(radius - thickness) * 2,
            chord_height=dish_height,
            upper_or_lower="upper",
            rotation_angle=rotation_angle,
            plane=plane,
        )

    elif upper_or_lower == "lower":
        dome_section = constant_thickness_dome(
            thickness=thickness,
            chord_center_height=lower_chord_center_height,
            chord_width=(radius - thickness) * 2,
            chord_height=dish_height,
            upper_or_lower="lower",
            rotation_angle=rotation_angle,
            plane=plane,
        )
    else:
        raise ValueError(f'upper_or_lower must be either "lower" or "upper" not {upper_or_lower}')

    dome_section.name = name
    cylinder_section.name = name
    return dome_section, cylinder_section
