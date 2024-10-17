import typing

from paramak import center_column_shield_cylinder, constant_thickness_dome


def dished_vacuum_vessel(
    radius: float = 300,
    reference_point: tuple = ("center", 0),
    dish_height: typing.Tuple[float, float] = (20, 50),
    cylinder_height: float = 400,
    thickness: float = 15,
    rotation_angle: float = 90,
    name: str = "dished_vessel",
    plane="XZ",
):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange.

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
        #                     |    |
        #                     |    |
        #                    -     |
        #                  -      -
        #                -       -
        #          -  -       -
        #                  -
        #          -   -
        #

    if reference_point[0] == "center":
        center_height = reference_point[1]
        lower_chord_center_height = reference_point[1] - 0.5 * cylinder_height
        upper_chord_center_height = reference_point[1] + 0.5 * cylinder_height
    elif reference_point[0] == "lower":
        center_height = reference_point[1] + thickness + dish_height[0] + 0.5 * cylinder_height
        lower_chord_center_height = reference_point[1] + thickness + dish_height[0]
        upper_chord_center_height = reference_point[1] + thickness + dish_height[0] + cylinder_height
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

    upper_dome_section = constant_thickness_dome(
        thickness=thickness,
        chord_center_height=upper_chord_center_height,
        chord_width=(radius - thickness) * 2,
        chord_height=dish_height[1],
        upper_or_lower="upper",
        rotation_angle=rotation_angle,
        plane=plane,
    )

    lower_dome_section = constant_thickness_dome(
        thickness=thickness,
        chord_center_height=lower_chord_center_height,
        chord_width=(radius - thickness) * 2,
        chord_height=dish_height[0],
        upper_or_lower="lower",
        rotation_angle=rotation_angle,
        plane=plane,
    )

    # union can fail, safer to return 3 workplanes
    # solid = cylinder_section.union(upper_dome_section).union(lower_dome_section)

    cylinder_section.name = name
    upper_dome_section.name = name
    lower_dome_section.name = name
    return lower_dome_section, cylinder_section, upper_dome_section
