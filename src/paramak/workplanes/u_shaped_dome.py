from __future__ import annotations

from ..utils import validate_positive, validate_rotation_angle
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.constant_thickness_dome import constant_thickness_dome


def u_shaped_dome(
    radius: float = 310,
    reference_point: tuple = ("lower", 0),
    dish_height: float = 50,
    cylinder_height: float = 400,
    thickness: float = 16,
    rotation_angle: float = 180,
    name: str = "u_shaped_dome",
    plane="XZ",
    upper_or_lower="upper",
    rotation_start_angle: float = 0.0,
):
    """A cylindrical u shaped dome with constant thickness.

    Arguments:
        radius: the radius from which the centres of the vessel meets the outer
            circumference.
        reference_point: the vertical position to build the vessel from,
            either ("center", z) for the middle of the cylinder or
            ("lower", z) for the lowest point of the shape (the bottom of
            the cylinder for an upper dome, the bottom of the dish for a
            lower dome).
        dish_height: the height of the dish section.
        cylinder_height: the height of the cylindrical section of the vacuum
            vessel.
        thickness: the radial thickness of the vessel in cm.
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    validate_positive(dish_height, "dish_height")
    validate_rotation_angle(rotation_angle)
    validate_positive(cylinder_height, "cylinder_height")
    validate_positive(radius, "radius")
    validate_positive(thickness, "thickness")

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
        # the lowest point is the bottom of the dish for a lower dome and the
        # bottom of the cylinder for an upper dome
        cylinder_bottom = reference_point[1] + (thickness + dish_height if upper_or_lower == "lower" else 0)
        center_height = cylinder_bottom + 0.5 * cylinder_height
        lower_chord_center_height = cylinder_bottom
        upper_chord_center_height = cylinder_bottom + cylinder_height
    else:
        raise ValueError('reference_point should be a tuple where the first value is either "center" or "lower"')

    cylinder_section = center_column_shield_cylinder(
        height=cylinder_height,
        inner_radius=radius - thickness,
        thickness=thickness,
        reference_point=("center", center_height),
        rotation_angle=rotation_angle,
        rotation_start_angle=rotation_start_angle,
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
            rotation_start_angle=rotation_start_angle,
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
            rotation_start_angle=rotation_start_angle,
            plane=plane,
        )
    else:
        raise ValueError(f'upper_or_lower must be either "lower" or "upper" not {upper_or_lower}')

    dome_section.name = name
    cylinder_section.name = name
    return dome_section, cylinder_section
