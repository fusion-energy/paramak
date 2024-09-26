from typing import Optional, Sequence, Tuple, Union

import cadquery as cq

from ..utils import build_divertor_modify_blanket, extract_radial_builds, get_plasma_index, sum_after_plasma
from ..workplanes.blanket_from_plasma import blanket_from_plasma
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified
from .spherical_tokamak import get_plasma_value, sum_up_to_plasma


def count_cylinder_layers(radial_build):
    before_plasma = 0
    after_plasma = 0
    found_plasma = False

    for item in radial_build:
        if item[0] == "plasma":
            found_plasma = True
        elif item[0] == "layer":
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

    for index, item in enumerate(radial_build):
        if item[0] == "plasma":
            break

        if item[0] == "gap":
            total_sum += item[1]
            continue

        thickness = item[1]
        layer_count += 1

        if layer_count > number_of_cylinder_layers:
            break

        cylinder = center_column_shield_cylinder(
            inner_radius=total_sum,
            thickness=item[1],
            name=f"layer_{layer_count}",
            rotation_angle=rotation_angle,
            height=center_column_shield_height,
        )
        total_sum += thickness
        cylinders.append(cylinder)
    return cylinders


def distance_to_plasma(radial_build, index):
    distance = 0
    for item in radial_build[index + 1 :]:
        if item[0] == "plasma":
            break
        distance += item[1]
    return distance


def create_layers_from_plasma(
    radial_build, vertical_build, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column
):

    plasma_index_rb = get_plasma_index(radial_build)
    plasma_index_vb = get_plasma_index(vertical_build)
    indexes_from_plamsa_to_end = len(radial_build) - plasma_index_rb
    layers = []

    cumulative_thickness_orb = 0
    cumulative_thickness_irb = 0
    cumulative_thickness_uvb = 0
    cumulative_thickness_lvb = 0
    for index_delta in range(indexes_from_plamsa_to_end):

        if radial_build[plasma_index_rb + index_delta][0] == "plasma":
            continue
        outer_layer_thickness = radial_build[plasma_index_rb + index_delta][1]
        inner_layer_thickness = radial_build[plasma_index_rb - index_delta][1]
        upper_layer_thickness = vertical_build[plasma_index_vb - index_delta][1]
        lower_layer_thickness = vertical_build[plasma_index_vb + index_delta][1]

        if radial_build[plasma_index_rb + index_delta][0] == "gap":
            cumulative_thickness_orb += outer_layer_thickness
            cumulative_thickness_irb += inner_layer_thickness
            cumulative_thickness_uvb += upper_layer_thickness
            cumulative_thickness_lvb += lower_layer_thickness
            continue

        # build outer layer
        if radial_build[plasma_index_rb + index_delta][0] == "layer":
            outer_layer = blanket_from_plasma(
                minor_radius=minor_radius,
                major_radius=major_radius,
                triangularity=triangularity,
                elongation=elongation,
                thickness=[
                    upper_layer_thickness,
                    outer_layer_thickness,
                    lower_layer_thickness
                ],
                offset_from_plasma=[
                    cumulative_thickness_uvb,
                    cumulative_thickness_orb,
                    cumulative_thickness_lvb
                ],
                start_angle=90,
                stop_angle=-90,
                rotation_angle=rotation_angle,
                color=(0.5, 0.5, 0.5),
                name=f"layer_{index_delta}",
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
                name=f"layer_{index_delta}",
                allow_overlapping_shape=True,
            )
            layer = outer_layer.union(inner_layer)
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
    radial_builds: Union[Sequence[Sequence[Tuple[str, float]]], Sequence[Tuple[str, float]]],
    elongation: float = 2.0,
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    add_extra_cut_shapes: Sequence[cq.Workplane] = [],
):
    
    plasma_radial_build, _ = extract_radial_builds(radial_builds)

    inner_equatorial_point = sum_up_to_plasma(plasma_radial_build)
    plasma_radial_thickness = get_plasma_value(plasma_radial_build)
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    # sets major radius and minor radius from equatorial_points to allow a
    # radial build. This helps avoid the plasma overlapping the center
    # column and other components
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    # make vertical build from outer radial build
    pi = get_plasma_index(plasma_radial_build)
    upper_vertical_build = plasma_radial_build[pi:]

    plasma_height = 2 * minor_radius * elongation
    # slice opperation reverses the list and removes the last value to avoid two plasmas
    vertical_build = upper_vertical_build[::-1][:-1] + [("plasma", plasma_height)] + upper_vertical_build[1:]

    return tokamak(
        radial_builds=radial_builds,
        vertical_build=vertical_build,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
        add_extra_cut_shapes=add_extra_cut_shapes,
    )

def tokamak(
    radial_builds: Union[Sequence[Sequence[Tuple[str, float]]], Sequence[Tuple[str, float]]],
    vertical_build: Sequence[Tuple[str, float]],
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    add_extra_cut_shapes: Sequence[cq.Workplane]  = [],
):
    """
    Creates a tokamak fusion reactor from a radial build and plasma parameters.

    Args:
        radial_builds (Sequence[tuple[str, float]]): A list of tuples containing the radial build of the reactor.
        elongation (float, optional): The elongation of the plasma. Defaults to 2.0.
        triangularity (float, optional): The triangularity of the plasma. Defaults to 0.55.
        rotation_angle (float, optional): The rotation angle of the plasma. Defaults to 180.0.
        add_extra_cut_shapes (Sequence, optional): A list of extra shapes to cut the reactor with. Defaults to [].

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the tokamak fusion reactor.
    """

    plasma_radial_build, divertor_radial_builds = extract_radial_builds(radial_builds)

    inner_equatorial_point = sum_up_to_plasma(plasma_radial_build)
    plasma_radial_thickness = get_plasma_value(plasma_radial_build)
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
        plasma_radial_build, rotation_angle, blanket_rear_wall_end_height
    )

    blanket_layers = create_layers_from_plasma(
        radial_build=plasma_radial_build,
        vertical_build=vertical_build,
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        rotation_angle=rotation_angle,
        center_column=inner_radial_build[0],  # blanket_cutting_cylinder,
    )

    divertor_layers, blanket_layers = build_divertor_modify_blanket(
        blanket_layers, divertor_radial_builds, blanket_rear_wall_end_height, rotation_angle
    )

    my_assembly = cq.Assembly()

    for i, entry in enumerate(add_extra_cut_shapes):

        if isinstance(entry, cq.Workplane):
            my_assembly.add(entry, name=f"add_extra_cut_shape_{i+1}")
        else:
            raise ValueError(f"add_extra_cut_shapes should only contain cadquery Workplanes, not {type(entry)}")

    if len(add_extra_cut_shapes) == 0:
        for i, entry in enumerate(inner_radial_build):
            my_assembly.add(entry, name=f"inboard_layer_{i+1})")
        for i, entry in enumerate(blanket_layers):
            my_assembly.add(entry, name=f"outboard_layer_{i+1})")
        for i, entry in enumerate(divertor_layers):
            my_assembly.add(entry, name=f"{entry.name})")  # gets upper or lower name
    else:
        shapes_and_components = []
        for i, entry in enumerate(inner_radial_build + blanket_layers + divertor_layers):
            for cutter in add_extra_cut_shapes:
                entry = entry.cut(cutter)
                # TODO use something like this to return a list of material tags for the solids in order, as some solids get split into multiple
                # for subentry in entry.objects:
                #     print(i, subentry)
            shapes_and_components.append(entry)

        for i, entry in enumerate(shapes_and_components):
            my_assembly.add(entry, name=f"layer_{i+1})")  #TODO track the names of shapes, even when extra shapes are made due to splitting


    my_assembly.add(plasma, name="plasma")

    return my_assembly
