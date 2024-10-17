from typing import Optional, Sequence, Tuple, Union

import cadquery as cq

from ..utils import (
    get_plasma_index,
    get_plasma_value,
    sum_up_to_gap_before_plasma,
    sum_up_to_plasma,
    sum_before_after_plasma,
    LayerType
)
from ..workplanes.blanket_from_plasma import blanket_from_plasma
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified


def create_blanket_layers_after_plasma(
    radial_build, vertical_build, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column
):
    layers = []
    cumulative_thickness_rb = 0
    cumulative_thickness_uvb = 0
    cumulative_thickness_lvb = 0

    plasma_index_radial = get_plasma_index(radial_build)
    plasma_index_vertical = get_plasma_index(vertical_build)

    for i, item in enumerate(radial_build[plasma_index_radial + 1 :]):
        upper_thicknees = vertical_build[plasma_index_vertical + 1 + i][1]
        lower_thicknees = vertical_build[plasma_index_vertical - 1 - i][1]
        radial_thickness = item[1]

        if item[0] == LayerType.GAP:
            cumulative_thickness_rb += radial_thickness
            cumulative_thickness_uvb += upper_thicknees
            cumulative_thickness_lvb += lower_thicknees
            continue

        layer = blanket_from_plasma(
            minor_radius=minor_radius,
            major_radius=major_radius,
            triangularity=triangularity,
            elongation=elongation,
            thickness=[
                lower_thicknees,
                radial_thickness,
                upper_thicknees,
            ],
            offset_from_plasma=[
                cumulative_thickness_lvb,
                cumulative_thickness_rb,
                cumulative_thickness_uvb,
            ],
            start_angle=-90,
            stop_angle=90,
            rotation_angle=rotation_angle,
            color=(0.5, 0.5, 0.5),
            name=f"layer_{plasma_index_radial+i+1}",
            allow_overlapping_shape=True,
            connect_to_center=True,
        )
        layer = layer.cut(center_column)
        cumulative_thickness_rb += radial_thickness
        cumulative_thickness_uvb += upper_thicknees
        cumulative_thickness_lvb += lower_thicknees
        layers.append(layer)

    return layers


def create_center_column_shield_cylinders(radial_build, vertical_build, rotation_angle):
    cylinders = []
    total_sum = 0
    layer_count = 0

    before, _ = sum_before_after_plasma(vertical_build)
    center_column_shield_height = sum([item[1] for item in vertical_build])

    for index, item in enumerate(radial_build):
        if item[0] == LayerType.PLASMA:
            break
        if item[0] == LayerType.GAP and radial_build[index + 1][0] == LayerType.PLASMA:
            break
        if item[0] == LayerType.GAP:
            total_sum += item[1]
            continue

        layer_count += 1
        # print('inner_radius', total_sum, 'item thickness', item[1], 'layer_count', layer_count)
        cylinder = center_column_shield_cylinder(
            inner_radius=total_sum,
            thickness=item[1],
            name=f"layer_{layer_count}",
            rotation_angle=rotation_angle,
            height=center_column_shield_height,
            reference_point=("lower", -before),
        )
        cylinders.append(cylinder)
        total_sum += item[1]

    return cylinders


def spherical_tokamak_from_plasma(
    radial_build: Sequence[Tuple[LayerType, float]],
    elongation: float = 2.0,
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] = [],
    extra_intersect_shapes: Sequence[cq.Workplane] = [],
):
    """_summary_

    Args:

        elongation (float, optional): _description_. Defaults to 2.0.
        triangularity (float, optional): _description_. Defaults to 0.55.
        rotation_angle (Optional[str], optional): _description_. Defaults to 180.0.
        extra_cut_shapes (Sequence, optional): _description_. Defaults to [].

    Returns:
        _type_: _description_
    """

    inner_equatorial_point = sum_up_to_plasma(radial_build)
    plasma_radial_thickness = get_plasma_value(radial_build)
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    # sets major radius and minor radius from equatorial_points to allow a
    # radial build. This helps avoid the plasma overlapping the center
    # column and other components
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    # make vertical build from outer radial build
    pi = get_plasma_index(radial_build)
    upper_vertical_build = radial_build[pi:]

    plasma_height = 2 * minor_radius * elongation
    # slice opperation reverses the list and removes the last value to avoid two plasmas
    vertical_build = upper_vertical_build[::-1][:-1] + [(LayerType.PLASMA, plasma_height)] + upper_vertical_build[1:]

    return spherical_tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=extra_intersect_shapes
    )


def spherical_tokamak(
    radial_build: Union[Sequence[Sequence[Tuple[str, float]]], Sequence[Tuple[str, float]]],
    vertical_build: Sequence[Tuple[str, float]],
    triangularity: float = 0.55,
    rotation_angle: Optional[str] = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] = [],
    extra_intersect_shapes: Sequence[cq.Workplane] = [],
):
    """_summary_

    Args:

        radial_build
        elongation (float, optional): _description_. Defaults to 2.0.
        triangularity (float, optional): _description_. Defaults to 0.55.
        rotation_angle (Optional[str], optional): _description_. Defaults to 180.0.
        extra_cut_shapes (Sequence, optional): _description_. Defaults to [].

    Returns:
        _type_: _description_
    """

    inner_equatorial_point = sum_up_to_plasma(radial_build)
    plasma_radial_thickness = get_plasma_value(radial_build)
    plasma_vertical_thickness = get_plasma_value(vertical_build)
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    # sets major radius and minor radius from equatorial_points to allow a
    # radial build. This helps avoid the plasma overlapping the center
    # column and other components
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    # vertical build
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
        radial_build=radial_build,
        vertical_build=vertical_build,
        rotation_angle=rotation_angle,
    )

    blanket_cutting_cylinder = center_column_shield_cylinder(
        inner_radius=0,
        thickness=sum_up_to_gap_before_plasma(radial_build),
        rotation_angle=360,
        height=2 * blanket_rear_wall_end_height,
    )

    blanket_layers = create_blanket_layers_after_plasma(
        radial_build=radial_build,
        vertical_build=vertical_build,
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        rotation_angle=rotation_angle,
        center_column=blanket_cutting_cylinder,
    )


    my_assembly = cq.Assembly()

    for i, entry in enumerate(extra_cut_shapes):

        if isinstance(entry, cq.Workplane):
            my_assembly.add(entry, name=f"add_extra_cut_shape_{i+1}")
        else:
            raise ValueError(f"extra_cut_shapes should only contain cadquery Workplanes, not {type(entry)}")

    # builds up the intersect shapes
    intersect_shapes_to_cut = []
    if len(extra_intersect_shapes)>0:
        all_shapes = []
        for shape in inner_radial_build + blanket_layers:
            all_shapes.append(shape)

        # makes a union of the the radial build to use as a base for the intersect shapes
        reactor_compound=inner_radial_build[0]
        for i, entry in enumerate(inner_radial_build[1:] + blanket_layers):
            reactor_compound = reactor_compound.union(entry)

        # adds the extra intersect shapes to the assembly
        for i, entry in enumerate(extra_intersect_shapes):
            reactor_entry_intersection = entry.intersect(reactor_compound)
            intersect_shapes_to_cut.append(reactor_entry_intersection)
            my_assembly.add(reactor_entry_intersection, name=f"extra_intersect_shapes_{i+1}")

    # builds just the core if there are no extra parts
    if len(extra_cut_shapes) == 0 and len(intersect_shapes_to_cut) == 0:
        for i, entry in enumerate(inner_radial_build):
            my_assembly.add(entry, name=f"inboard_layer_{i+1})")
        for i, entry in enumerate(blanket_layers):
            my_assembly.add(entry, name=f"outboard_layer_{i+1})")
    else:
        shapes_and_components = []
        for i, entry in enumerate(inner_radial_build + blanket_layers):
            for cutter in extra_cut_shapes + extra_intersect_shapes:
                entry = entry.cut(cutter)
                # TODO use something like this to return a list of material tags for the solids in order, as some solids get split into multiple
                # for subentry in entry.objects:
                #     print(i, subentry)
            shapes_and_components.append(entry)

        for i, entry in enumerate(shapes_and_components):
            my_assembly.add(entry, name=f"layer_{i+1})")  #TODO track the names of shapes, even when extra shapes are made due to splitting

    my_assembly.add(plasma, name="plasma")

    return my_assembly
