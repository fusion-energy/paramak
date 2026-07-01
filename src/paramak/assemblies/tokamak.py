from typing import Sequence, Tuple

import cadquery as cq
from .assembly import Assembly

from ..utils import get_plasma_index, get_layer_name, validate_vertical_build_names, validate_unique_assembly_names, LayerType
from ..workplanes.blanket_from_plasma import blanket_from_plasma
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified
from .spherical_tokamak import get_plasma_value, sum_up_to_plasma


def count_cylinder_layers(radial_build):
    before_plasma = 0
    after_plasma = 0
    found_plasma = False

    for item in radial_build:
        if item[0] == LayerType.PLASMA:
            found_plasma = True
        elif item[0] == LayerType.SOLID:
            if not found_plasma:
                before_plasma += 1
            else:
                after_plasma += 1

    return before_plasma - after_plasma


def create_center_column_shield_cylinders(radial_build, rotation_angle, center_column_shield_height):
    cylinders = []
    total_sum = 0
    layer_count = 0

    number_of_cylinder_layers = count_cylinder_layers(radial_build)

    for _, item in enumerate(radial_build):
        if item[0] == LayerType.PLASMA:
            break

        if item[0] == LayerType.GAP:
            total_sum += item[1]
            continue

        thickness = item[1]
        layer_count += 1

        if layer_count > number_of_cylinder_layers:
            break

        layer_name = get_layer_name(item, layer_count)

        cylinder = center_column_shield_cylinder(
            inner_radius=total_sum,
            thickness=item[1],
            name=layer_name,
            rotation_angle=rotation_angle,
            height=center_column_shield_height,
        )
        total_sum += thickness
        cylinders.append(cylinder)
    return cylinders


def distance_to_plasma(radial_build, index):
    distance = 0
    for item in radial_build[index + 1 :]:
        if item[0] == LayerType.PLASMA:
            break
        distance += item[1]
    return distance


def create_layers_from_plasma(
    radial_build, vertical_build, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column, layer_count=0
):

    plasma_index_rb = get_plasma_index(radial_build)
    plasma_index_vb = get_plasma_index(vertical_build)
    indexes_from_plasma_to_end = len(radial_build) - plasma_index_rb
    layers = []

    cumulative_thickness_orb = 0
    cumulative_thickness_irb = 0
    cumulative_thickness_uvb = 0
    cumulative_thickness_lvb = 0

    for index_delta in range(indexes_from_plasma_to_end):

        if radial_build[plasma_index_rb + index_delta][0] == LayerType.PLASMA:
            continue
        outer_layer_thickness = radial_build[plasma_index_rb + index_delta][1]
        inner_layer_thickness = radial_build[plasma_index_rb - index_delta][1]
        upper_layer_thickness = vertical_build[plasma_index_vb - index_delta][1]
        lower_layer_thickness = vertical_build[plasma_index_vb + index_delta][1]

        if radial_build[plasma_index_rb + index_delta][0] == LayerType.GAP:
            cumulative_thickness_orb += outer_layer_thickness
            cumulative_thickness_irb += inner_layer_thickness
            cumulative_thickness_uvb += upper_layer_thickness
            cumulative_thickness_lvb += lower_layer_thickness
            continue

        layer_count += 1
        if len(radial_build[plasma_index_rb - index_delta]) == 3:
            layer_name = radial_build[plasma_index_rb - index_delta][2]
        elif len(radial_build[plasma_index_rb + index_delta]) == 3:
            layer_name = radial_build[plasma_index_rb + index_delta][2]
        else:
            layer_name = f"layer_{layer_count}"

        # build outer layer
        if radial_build[plasma_index_rb + index_delta][0] == LayerType.SOLID:
            outer_layer = blanket_from_plasma(
                minor_radius=minor_radius,
                major_radius=major_radius,
                triangularity=triangularity,
                elongation=elongation,
                thickness=[upper_layer_thickness, outer_layer_thickness, lower_layer_thickness],
                offset_from_plasma=[cumulative_thickness_uvb, cumulative_thickness_orb, cumulative_thickness_lvb],
                start_angle=90,
                stop_angle=-90,
                rotation_angle=rotation_angle,
                color=(0.5, 0.5, 0.5),
                name=layer_name,
                allow_overlapping_shape=True,
            )
            inner_layer = blanket_from_plasma(
                minor_radius=minor_radius,
                major_radius=major_radius,
                triangularity=triangularity,
                elongation=elongation,
                thickness=[
                    lower_layer_thickness,
                    inner_layer_thickness,
                    upper_layer_thickness,
                ],
                offset_from_plasma=[
                    cumulative_thickness_lvb,
                    cumulative_thickness_irb,
                    cumulative_thickness_uvb,
                ],
                start_angle=-90,
                stop_angle=-270,
                rotation_angle=rotation_angle,
                color=(0.5, 0.5, 0.5),
                name=layer_name,
                allow_overlapping_shape=True,
            )
            layer = outer_layer.union(inner_layer)
            layer.name = layer_name
            layers.append(layer)
            # layers.append(inner_layer)
        cumulative_thickness_orb += outer_layer_thickness
        cumulative_thickness_irb += inner_layer_thickness
        cumulative_thickness_uvb += upper_layer_thickness
        cumulative_thickness_lvb += lower_layer_thickness
        # build inner layer

        # union layers

    return layers


def tokamak_from_plasma(
    radial_build: Sequence[Tuple[LayerType, float] | Tuple[LayerType, float, str]],
    elongation: float = 2.0,
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] = None,
    extra_intersect_shapes: Sequence[cq.Workplane] = None,
    colors: dict = None,
) -> Assembly:
    """
    Creates a tokamak fusion reactor from a radial build and plasma parameters.

    Args:
        radial_build: sequence of tuples containing the radial build of the
            reactor. Each tuple should contain a LayerType, a float and a string.
        elongation: The elongation of the plasma. Defaults to 2.0.
        triangularity: The triangularity of the plasma. Defaults to 0.55.
        rotation_angle: The rotation angle of the plasma. Defaults to 180.0.
        extra_cut_shapes: A list of extra shapes to cut the reactor with. Defaults to [].
        extra_intersect_shapes: A list of extra shapes to intersect the reactor with. Defaults to [].
        colors (dict, optional): the colors to assign to the assembly parts. Defaults to {}.
            Each dictionary entry should be a key that matches the assembly part name
            (e.g. 'plasma', or 'layer_1') and a tuple of 3 or 4 floats between 0 and 1
            representing the RGB or RGBA values.

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the tokamak fusion reactor.
    """

    if extra_cut_shapes is None:
        extra_cut_shapes = []
    if extra_intersect_shapes is None:
        extra_intersect_shapes = []
    if colors is None:
        colors = {}

    inner_equatorial_point = sum_up_to_plasma(radial_build)
    plasma_radial_thickness = get_plasma_value(radial_build)
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    # sets major radius and minor radius from equatorial_points to allow a
    # radial build. This helps avoid the plasma overlapping the center
    # column and other components
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    # make vertical build from inner radial build
    pi = get_plasma_index(radial_build)
    rbi = len(radial_build) - 1 - pi  # number of unique entries in outer or inner radial build
    upper_vertical_build = radial_build[pi - rbi : pi][::-1]  # get the inner radial build

    plasma_height = 2 * minor_radius * elongation
    # slice operation reverses the list and removes the last value to avoid two plasmas
    vertical_build = upper_vertical_build[::-1] + [(LayerType.PLASMA, plasma_height)] + upper_vertical_build

    return tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=extra_intersect_shapes,
        colors=colors
    )


def tokamak(
    radial_build: Sequence[Tuple[str, float] | Tuple[str, float, str]],
    vertical_build: Sequence[Tuple[str, float] | Tuple[str, float, str]],
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] = None,
    extra_intersect_shapes: Sequence[cq.Workplane] = None,
    colors: dict = None,
) -> Assembly:
    """
    Creates a tokamak fusion reactor from a radial and vertical build.

    Args:
        radial_build: sequence of tuples containing the radial build of the
            reactor. Each tuple should contain a LayerType, a float and the string is optional.
        vertical_build: sequence of tuples containing the vertical build of the
            reactor. Each tuple should contain a LayerType, a float and the string is optional.
        triangularity: The triangularity of the plasma. Defaults to 0.55.
        rotation_angle: The rotation angle of the plasma. Defaults to 180.0.
        extra_cut_shapes: A list of extra shapes to cut the reactor with. Defaults to [].
        extra_intersect_shapes: A list of extra shapes to intersect the reactor with. Defaults to [].
        colors (dict, optional): the colors to assign to the assembly parts. Defaults to {}.
            Each dictionary entry should be a key that matches the assembly part name
            (e.g. 'plasma', or 'layer_1') and a tuple of 3 or 4 floats between 0 and 1
            representing the RGB or RGBA values.

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the tokamak fusion reactor.
    """

    if extra_cut_shapes is None:
        extra_cut_shapes = []
    if extra_intersect_shapes is None:
        extra_intersect_shapes = []
    if colors is None:
        colors = {}

    validate_vertical_build_names(vertical_build, "tokamak()")

    inner_equatorial_point = sum_up_to_plasma(radial_build)
    plasma_radial_thickness = get_plasma_value(radial_build)
    plasma_vertical_thickness = get_plasma_value(vertical_build)
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    elongation = (plasma_vertical_thickness / 2) / minor_radius
    blanket_rear_wall_end_height = sum([item[1] for item in vertical_build])

    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
    )

    inner_radial_build = create_center_column_shield_cylinders(
        radial_build, rotation_angle, blanket_rear_wall_end_height
    )

    blanket_layers = create_layers_from_plasma(
        radial_build=radial_build,
        vertical_build=vertical_build,
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        rotation_angle=rotation_angle,
        center_column=inner_radial_build[0],  # blanket_cutting_cylinder,
        layer_count=len(inner_radial_build)
    )

    assembly_names = [
        *[
            f"{getattr(entry, 'name', None)}_{i + 1}" if getattr(entry, 'name', None) else f"add_extra_cut_shape_{i + 1}"
            for i, entry in enumerate(extra_cut_shapes)
        ],
        *[
            f"{getattr(entry, 'name', None)}_{i + 1}" if getattr(entry, 'name', None) else f"extra_intersect_shapes_{i + 1}"
            for i, entry in enumerate(extra_intersect_shapes)
        ],
        *[
            getattr(entry, 'name', None) if getattr(entry, 'name', None) else f"layer_{i + 1}"
            for i, entry in enumerate(inner_radial_build + blanket_layers)
        ],
        "plasma",
    ]

    validate_unique_assembly_names(assembly_names, "tokamak()")

    my_assembly = Assembly()

    for i, entry in enumerate(extra_cut_shapes):
        if isinstance(entry, cq.Workplane):
            # Use the object's name attribute if it exists, otherwise fallback
            base_name = getattr(entry, 'name', None)
            if base_name:
                name = f"{base_name}_{i+1}"
            else:
                name = f"add_extra_cut_shape_{i+1}"
            my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))
        else:
            raise ValueError(f"extra_cut_shapes should only contain cadquery Workplanes, not {type(entry)}")

    # builds up the intersect shapes
    intersect_shapes_to_cut = []
    if len(extra_intersect_shapes) > 0:
        all_shapes = []
        for shape in inner_radial_build + blanket_layers:
            all_shapes.append(shape)

        # makes a union of the the radial build to use as a base for the intersect shapes
        reactor_compound = inner_radial_build[0]
        for i, entry in enumerate(inner_radial_build[1:] + blanket_layers):
            reactor_compound = reactor_compound.union(entry)

        # adds the extra intersect shapes to the assembly
        for i, entry in enumerate(extra_intersect_shapes):
            reactor_entry_intersection = entry.intersect(reactor_compound)
            intersect_shapes_to_cut.append(reactor_entry_intersection)
            # Use the object's name attribute if it exists, otherwise fallback
            base_name = getattr(entry, 'name', None)
            if base_name:
                name = f"{base_name}_{i+1}"
            else:
                name=f"extra_intersect_shapes_{i+1}"
            my_assembly.add(reactor_entry_intersection, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    # builds just the core if there are no extra parts
    if len(extra_cut_shapes) == 0 and len(intersect_shapes_to_cut) == 0:
        for i, entry in enumerate(inner_radial_build+blanket_layers):
            base_name = getattr(entry, 'name', None)
            name = base_name if base_name else f"layer_{i+1}"
            my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))
    else:
        shapes_and_components = []
        names = []
        for i, entry in enumerate(inner_radial_build + blanket_layers):
            base_name = getattr(entry, 'name', None)
            name = base_name if base_name else f"layer_{i+1}"
            for cutter in extra_cut_shapes + extra_intersect_shapes:
                entry = entry.cut(cutter)
            shapes_and_components.append(entry)
            names.append(name)

        for entry, name in zip(shapes_and_components, names):
            # TODO track the names of shapes, even when extra shapes are made due to splitting
            my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    my_assembly.add(plasma, name="plasma", color=cq.Color(*colors.get("plasma", (0.5,0.5,0.5))))

    my_assembly.elongation = elongation
    my_assembly.triangularity = triangularity
    my_assembly.major_radius = major_radius
    my_assembly.minor_radius = minor_radius

    return my_assembly
