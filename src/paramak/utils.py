import numbers
import typing
from collections import Counter
from enum import Enum

import numpy as np
from cadquery import Workplane


class LayerType(Enum):
    GAP = "gap"
    SOLID = "solid"
    PLASMA = "plasma"


def instructions_from_points(points):
    # obtains the first two values of the points list
    XZ_points = [(p[0], p[1]) for p in points]

    # obtains the last values of the points list
    connections = [p[2] for p in points[:-1]]

    current_linetype = connections[0]
    current_points_list = []
    instructions = []
    # groups together common connection types
    for i, connection in enumerate(connections):
        if connection == current_linetype:
            current_points_list.append(XZ_points[i])
        else:
            current_points_list.append(XZ_points[i])
            instructions.append({current_linetype: current_points_list})
            current_linetype = connection
            current_points_list = [XZ_points[i]]
    instructions.append({current_linetype: current_points_list})

    if next(iter(instructions[-1].values()))[-1] != XZ_points[0]:
        keyname = next(iter(instructions[-1].keys()))
        instructions[-1][keyname].append(XZ_points[0])
    return instructions


def create_wire_workplane_from_instructions(
    instructions,
    workplane,
):

    for entry in instructions:
        instruction_type, points = next(iter(entry.items()))
        if instruction_type == "spline":
            workplane = workplane.spline(listOfXYTuple=points)
        if instruction_type == "straight":
            workplane = workplane.polyline(points)
        if instruction_type == "circle":
            # each arc goes through a start, middle and end point, and the end
            # of one arc is the start of the next
            if len(points) < 3 or len(points) % 2 == 0:
                raise ValueError(
                    'Each "circle" arc uses two points (its start and middle point) and ends at the next '
                    f"point, so a run of consecutive circle points must have an even number of points, "
                    f"got {len(points) - 1} circle points starting at {points[0]}."
                )
            workplane = workplane.moveTo(points[0][0], points[0][1])
            for start in range(0, len(points) - 1, 2):
                workplane = workplane.threePointArc(points[start + 1], points[start + 2])

    return workplane.close()


def create_wire_workplane_from_points(points, plane, origin=(0, 0, 0), obj=None):

    workplane = Workplane(plane, origin=origin, obj=obj)

    all_straight = all(entry[-1] == "straight" for entry in points)
    all_spline = all(entry[-1] == "spline" for entry in points)

    if all_straight:
        entry_values = [entry[:2] for entry in points[:-1]]
        result = workplane.polyline(entry_values).close()
    elif all_spline:
        entry_values = [entry[:2] for entry in points[:-1]]
        result = workplane.spline(
            entry_values, makeWire=True, tol=1e-1, periodic=True
        )  # periodic smooths out the connecting joint
    else:
        instructions = instructions_from_points(points)

        result = create_wire_workplane_from_instructions(
            instructions=instructions,
            workplane=workplane,
        )

    return result


def validate_number(value, name):
    """Checks value is a real number (bools are not accepted)."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a number, not {type(value).__name__}.")


def validate_positive(value, name):
    """Checks value is a number above 0."""
    validate_number(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}.")


def validate_non_negative(value, name):
    """Checks value is a number of 0 or more."""
    validate_number(value, name)
    if value < 0:
        raise ValueError(f"{name} must be zero or positive, got {value}.")


def validate_positive_integer(value, name):
    """Checks value is a whole number above 0."""
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise TypeError(f"{name} must be an integer, not {type(value).__name__}.")
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}.")


def validate_rotation_angle(rotation_angle):
    """Checks the rotation_angle is above 0 and at most 360 degrees."""
    validate_number(rotation_angle, "rotation_angle")
    if not 0 < rotation_angle <= 360:
        raise ValueError(f"rotation_angle must be above 0 and at most 360 degrees, not {rotation_angle}.")


def validate_rotation_start_angle(rotation_start_angle):
    """Checks the rotation_start_angle is between -360 and 360 degrees."""
    validate_number(rotation_start_angle, "rotation_start_angle")
    if not -360 <= rotation_start_angle <= 360:
        raise ValueError(
            f"rotation_start_angle must be between -360 and 360 degrees, not {rotation_start_angle}."
        )


def rotate_to_rotation_start_angle(solid: Workplane, wire: Workplane, rotation_start_angle: float) -> Workplane:
    """Rotates a solid revolved from wire by rotation_start_angle degrees
    about the axis it was revolved around, so the revolution starts at
    rotation_start_angle instead of 0."""
    validate_rotation_start_angle(rotation_start_angle)
    if rotation_start_angle == 0:
        return solid
    axis_start = wire.plane.toWorldCoords((0, 0))
    axis_end = wire.plane.toWorldCoords((0, 1))
    return solid.rotate(axis_start.toTuple(), axis_end.toTuple(), rotation_start_angle)


def rotate_about_z(shape: Workplane, angle: float) -> Workplane:
    """Rotates a shape about the Z axis by angle degrees, keeping the name
    and layer_name attributes that paramak sets on the parts of a reactor."""
    if angle == 0:
        return shape
    rotated = shape.rotate((0, 0, 0), (0, 0, 1), angle)
    for attribute in ("name", "layer_name"):
        if hasattr(shape, attribute):
            setattr(rotated, attribute, getattr(shape, attribute))
    return rotated


def rotate_solid(angles: typing.Sequence[float], solid: Workplane) -> Workplane:
    rotation_axis = {
        "X": [(-1, 0, 0), (1, 0, 0)],
        "-X": [(1, 0, 0), (-1, 0, 0)],
        "Y": [(0, -1, 0), (0, 1, 0)],
        "-Y": [(0, 1, 0), (0, -1, 0)],
        "Z": [(0, 0, -1), (0, 0, 1)],
        "-Z": [(0, 0, 1), (0, 0, -1)],
    }

    rotated_solids = []
    # Perform separate rotations for each angle
    for angle in angles:
        rotated_solids.append(solid.rotate(*rotation_axis["Z"], angle))
    solid = Workplane(solid.plane)

    # Joins the solids together
    for i in rotated_solids:
        solid = solid.union(i)
    return solid


def sum_up_to_gap_before_plasma(radial_build):
    total_sum = 0
    for i, item in enumerate(radial_build):
        if item[0] == LayerType.PLASMA:
            return total_sum
        if item[0] == LayerType.GAP and i + 1 < len(radial_build) and radial_build[i + 1][0] == LayerType.PLASMA:
            return total_sum
        total_sum += item[1]
    return total_sum


def sum_up_to_plasma(radial_build):
    total_sum = 0
    for item in radial_build:
        if item[0] == LayerType.PLASMA:
            break
        total_sum += item[1]
    return total_sum


def get_plasma_geometry(radial_build, vertical_build):
    """Returns the major radius, minor radius and elongation of the plasma
    defined by the radial and vertical builds."""
    inner_equatorial_point = sum_up_to_plasma(radial_build)
    outer_equatorial_point = inner_equatorial_point + get_plasma_value(radial_build)
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point
    elongation = (get_plasma_value(vertical_build) / 2) / minor_radius
    return major_radius, minor_radius, elongation


def smooth_profile(angles, values, period=None):
    """Returns a function of poloidal angle (degrees) that passes through the
    values at the angles and eases between neighbouring angles with a cosine.

    The slope is zero at each angle, so a layer whose thickness or offset is
    set by this profile has no corners where the values change (linear
    interpolation leaves a corner at each angle). The profile is constant
    between neighbouring angles with equal values.

    Args:
        angles: increasing angles in degrees.
        values: the value at each angle.
        period: if given, angles outside the range are wrapped by this period
            (360 for a closed loop), otherwise they are clipped to the range.
    """
    angles = np.asarray(angles, dtype=float)
    values = np.asarray(values, dtype=float)

    def profile(theta):
        theta = np.asarray(theta, dtype=float)
        if period is not None:
            theta = angles[0] + np.mod(theta - angles[0], period)
        theta = np.clip(theta, angles[0], angles[-1])
        index = np.clip(np.searchsorted(angles, theta, side="right") - 1, 0, len(angles) - 2)
        fraction = (theta - angles[index]) / (angles[index + 1] - angles[index])
        return values[index] + (values[index + 1] - values[index]) * (1 - np.cos(np.pi * fraction)) / 2

    return profile


class ValidationError(ValueError):
    """Raised when a radial or vertical build is not valid."""


def sum_before_after_plasma(vertical_build):
    before_plasma = 0
    after_plasma = 0
    plasma_value = 0
    plasma_found = False

    for item in vertical_build:
        if item[0] == LayerType.PLASMA:
            plasma_value = item[1] / 2
            plasma_found = True
            continue
        if not plasma_found:
            before_plasma += item[1]
        else:
            after_plasma += item[1]

    before_plasma += plasma_value
    after_plasma += plasma_value

    return before_plasma, after_plasma


def validate_divertor_radial_build(radial_build):
    if len(radial_build) != 2:
        raise ValidationError(
            f'The radial build for the divertor should only contain two entries, for example ((LayerType.GAP,10), ("lower_divertor", 10)) not {radial_build}'
        )

    if len(radial_build[0]) != 2 or len(radial_build[1]) != 2:
        raise ValidationError(
            "The radial build for the divertor should only contain tuples of length 2,, for example (LayerType.GAP,10)"
        )

    if radial_build[1][0] not in {"lower_divertor", "upper_divertor"}:
        raise ValidationError(
            f'The second entry in the radial build for the divertor should be either "lower_divertor" or "upper_divertor" not {radial_build[1][0]}'
        )

    if radial_build[0][0] != LayerType.GAP:
        raise ValidationError(
            f"The first entry in the radial build for the divertor should be a LayerType.GAP not {radial_build[0][0]}"
        )

    if not isinstance(radial_build[0][1], (int, float)) or not isinstance(radial_build[1][1], (int, float)):
        raise ValidationError(
            f"The thickness of the gap and the divertor should both be integers or floats, not {type(radial_build[0][1])} and {type(radial_build[1][1])}"
        )

    if radial_build[0][1] <= 0 or radial_build[1][1] <= 0:
        raise ValidationError(
            f"The thickness of the gap and the divertor should both be positive values, not {radial_build[0][1]} and {radial_build[1][1]}"
        )


def validate_plasma_radial_build(radial_build, build_name="radial_build"):
    """Checks a radial or vertical build that contains a plasma: every entry
    is a (LayerType, thickness) or (LayerType, thickness, name) tuple with a
    positive thickness, and there is one LayerType.PLASMA entry with a
    LayerType.GAP either side of it."""
    if not isinstance(radial_build, (list, tuple)) or len(radial_build) == 0:
        raise ValidationError(f"{build_name} must be a non empty list of tuples, not {radial_build!r}")
    plasma_count = 0
    plasma_index = -1
    for index, item in enumerate(radial_build):
        if not isinstance(item, (list, tuple)) or len(item) not in (2, 3):
            raise ValidationError(
                f"Each {build_name} entry should be a tuple of (LayerType, thickness) or "
                f"(LayerType, thickness, name), not {item!r} at index {index}"
            )
        if not isinstance(item[0], LayerType):
            raise ValidationError(f"First entry in each {build_name} Tuple should be a paramak.LayerType")
        if isinstance(item[1], bool) or not isinstance(item[1], numbers.Real):
            raise ValidationError(f"Second entry in each {build_name} Tuple should be a Float")
        if item[1] <= 0:
            raise ValidationError(f"Non-positive value '{item[1]}' at index {index} of the {build_name}")
        if len(item) == 3 and not isinstance(item[2], str):
            raise ValidationError(f"Third entry in each {build_name} Tuple should be a str name, not {item[2]!r}")
        if item[0] == LayerType.PLASMA:
            plasma_count += 1
            plasma_index = index
            if plasma_count > 1:
                raise ValidationError(f"Multiple LayerType.PLASMA entries found in the {build_name}")
    if plasma_count != 1:
        raise ValidationError(f"LayerType.PLASMA entry not found or found multiple times in the {build_name}")
    if plasma_index == 0 or plasma_index == len(radial_build) - 1:
        raise ValidationError("LayerType.PLASMA entry must have at least one entry before and after it")
    if radial_build[plasma_index - 1][0] != LayerType.GAP or radial_build[plasma_index + 1][0] != LayerType.GAP:
        raise ValidationError("LayerType.PLASMA entry must be preceded and followed by a LayerType.GAP")


def validate_build_lengths(radial_build, vertical_build, reactor_name, inboard_layers=True):
    """Checks the vertical_build has an entry above and below the plasma for
    each radial_build entry after the plasma, as each layer after the plasma
    takes its top and bottom thickness from the vertical_build. When
    inboard_layers is True (tokamak) the radial_build also needs an entry
    before the plasma for each entry after it, as the layers are made from
    inboard and outboard pairs."""
    plasma_index_rb = get_plasma_index(radial_build)
    plasma_index_vb = get_plasma_index(vertical_build)
    after_plasma = len(radial_build) - plasma_index_rb - 1
    above = plasma_index_vb
    below = len(vertical_build) - plasma_index_vb - 1
    if inboard_layers and plasma_index_rb < after_plasma:
        raise ValueError(
            f"The radial_build for {reactor_name} has {after_plasma} entries after the plasma but only "
            f"{plasma_index_rb} before it. Each entry after the plasma is paired with an entry before the plasma, "
            "so the radial_build needs at least as many entries before the plasma as after it."
        )
    if above < after_plasma or below < after_plasma:
        raise ValueError(
            f"The vertical_build for {reactor_name} needs at least {after_plasma} entries above and below the "
            f"plasma, one for each radial_build entry after the plasma, but it has {above} above and {below} below."
        )


def is_lower_or_upper_divertor(radial_build):
    for item in radial_build:
        if item[0] == "lower_divertor":
            return "lower_divertor"
        if item[0] == "upper_divertor":
            return "upper_divertor"
    raise ValidationError("neither upper_divertor or lower_divertor found")


def get_plasma_value(radial_build):
    for item in radial_build:
        if item[0] == LayerType.PLASMA:
            return item[1]
    raise ValueError("LayerType.PLASMA entry not found")


def get_plasma_index(radial_build):
    for i, item in enumerate(radial_build):
        if item[0] == LayerType.PLASMA:
            return i
    raise ValueError("LayerType.PLASMA entry not found")


def get_gap_after_plasma(radial_build):
    for index, item in enumerate(radial_build):
        if item[0] == LayerType.PLASMA:
            if index + 1 < len(radial_build) and radial_build[index + 1][0] == LayerType.GAP:
                return radial_build[index + 1][1]
            else:
                raise ValueError("LayerType.PLASMA entry is not followed by a 'gap'")
    raise ValueError("LayerType.PLASMA entry not found")


def sum_after_gap_following_plasma(radial_build):
    found_plasma = False
    found_gap_after_plasma = False
    total_sum = 0

    for item in radial_build:
        if found_gap_after_plasma:
            total_sum += item[1]
        elif found_plasma and item[0] == LayerType.GAP:
            found_gap_after_plasma = True
        elif item[0] == LayerType.PLASMA:
            found_plasma = True

    if not found_plasma:
        raise ValueError("LayerType.PLASMA entry not found")
    if not found_gap_after_plasma:
        raise ValueError("LayerType.PLASMA entry is not followed by a 'gap'")

    return total_sum

def get_layer_name(item, index):
    if len(item) == 2:
        layer_name = f"layer_{index}"
    else:
        layer_name = item[2]
    return layer_name

def validate_vertical_build_names(vertical_build, reactor_name):
    named_layers = [item[2] for item in vertical_build if len(item) == 3]
    if named_layers:
        unique_names = ", ".join(dict.fromkeys(named_layers))
        raise ValueError(
            f"Names are not supported in vertical_build for {reactor_name}. "
            f"Found named entries: {unique_names}. Please define names in radial_build only."
        )


def validate_unique_assembly_names(names, reactor_name):
    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        duplicate_names = ", ".join(sorted(duplicates))
        raise ValueError(
            f"Unique names are required for {reactor_name}. "
            f"The following names are duplicated in the assembly: {duplicate_names}. "
            "Please rename the repeated layers in radial_build."
        )
    
def get_assembly_names(extra_cut_shapes, extra_intersect_shapes, inner_radial_build, blanket_layers):
    cut_names = [
        f"{name}_{i + 1}" if (name := getattr(entry, 'name', None)) else f"add_extra_cut_shape_{i + 1}"
        for i, entry in enumerate(extra_cut_shapes)
    ]
    intersect_names = [
        f"{name}_{i + 1}" if (name := getattr(entry, 'name', None)) else f"extra_intersect_shapes_{i + 1}"
        for i, entry in enumerate(extra_intersect_shapes)
    ]
    layer_names = [
        name if (name := getattr(entry, 'name', None)) else f"layer_{i + 1}"
        for i, entry in enumerate(inner_radial_build + blanket_layers)
    ]
    return cut_names, intersect_names, layer_names


DEFAULT_LAYER_COLORS = [
    (0.4, 0.9, 0.4),  # green
    (0.6, 0.8, 0.6),  # light green
    (0.1, 0.1, 0.9),  # blue
    (0.4, 0.4, 0.8),  # medium blue/purple
    (0.5, 0.5, 0.8),  # slate blue
    (0.2, 0.7, 0.8),  # cyan
    (0.7, 0.5, 0.8),  # lavender
]

DEFAULT_PLASMA_COLOR = (1.0, 0.7, 0.8, 0.25)


def resolve_assembly_color(
    name: str, layer_index: int | None = None, colors: dict | None = None, layer_name: str | None = None
):
    """Returns the RGB(A) color for an assembly part.

    A color given in colors for the part name is used first, then a color
    given for layer_name (the radial layer the part was made from, so every
    poloidal segment and toroidal sector of a layer shares the layer color),
    then a default based on the part name or the layer index.

    Args:
        name: the name of the part in the assembly.
        layer_index: the index of the radial layer the part belongs to, used
            to pick a default layer color.
        colors: user specified colors keyed by part or layer name.
        layer_name: the name of the radial layer the part was made from.
    """
    colors = colors or {}
    if name in colors:
        return colors[name]
    if layer_name is not None and layer_name in colors:
        return colors[layer_name]
    if name == "plasma":
        return DEFAULT_PLASMA_COLOR
    lower_name = name.lower()
    if "divertor" in lower_name or "extra_intersect" in lower_name:
        return (0.8, 0.2, 0.2)
    if "toroidal_field_coil" in lower_name or lower_name.startswith("tf"):
        return (0.6, 0.3, 0.4)
    if "poloidal_field_coil_case" in lower_name:
        return (0.9, 0.4, 0.4)
    if "poloidal_field_coil" in lower_name or lower_name.startswith("pf"):
        return (0.4, 0.9, 0.4)
    if layer_index is not None:
        return DEFAULT_LAYER_COLORS[layer_index % len(DEFAULT_LAYER_COLORS)]
    return (0.5, 0.5, 0.5)
