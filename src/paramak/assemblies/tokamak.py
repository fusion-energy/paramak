from __future__ import annotations

import math
from typing import Sequence

import cadquery as cq
import numpy as np

from ..utils import (
    get_plasma_geometry,
    smooth_profile,
    LayerType,
    get_assembly_names,
    get_layer_name,
    get_plasma_index,
    validate_unique_assembly_names,
    validate_vertical_build_names,
)
from ..workplanes.blanket_from_plasma import (
    blanket_from_plasma,
    offset_curve_coordinates,
    poloidal_arc_length_table,
)
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified
from .assembly import Assembly
from .poloidal import (
    check_not_empty,
    get_poloidal_segment_angles,
    intersect_with_each_part,
    resolve_vertical_build,
    validate_poloidal_build,
)
from .spherical_tokamak import get_plasma_value

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


def get_layer_pairs(radial_build, vertical_build, layer_count=0):
    """Describes each inboard/outboard pair of layers, ordered from the plasma
    outwards. This is the ordering used by poloidal_build.

    Returns:
        list of dict: one entry per pair with the keys "type" (the LayerType
        of the outboard entry), "name" (None for GAP pairs), "offsets" and
        "thicknesses". The offsets and thicknesses are tuples of values at the
        outboard midplane, top, inboard midplane and bottom of the plasma.
    """
    plasma_index_rb = get_plasma_index(radial_build)
    plasma_index_vb = get_plasma_index(vertical_build)

    pairs = []
    cumulative_thickness_orb = 0
    cumulative_thickness_irb = 0
    cumulative_thickness_uvb = 0
    cumulative_thickness_lvb = 0

    for index_delta in range(1, len(radial_build) - plasma_index_rb):
        outer_entry = radial_build[plasma_index_rb + index_delta]
        inner_entry = radial_build[plasma_index_rb - index_delta]
        outer_layer_thickness = outer_entry[1]
        inner_layer_thickness = inner_entry[1]
        upper_layer_thickness = vertical_build[plasma_index_vb - index_delta][1]
        lower_layer_thickness = vertical_build[plasma_index_vb + index_delta][1]

        if outer_entry[0] == LayerType.GAP:
            layer_name = None
        else:
            layer_count += 1
            if len(inner_entry) == 3:
                layer_name = inner_entry[2]
            elif len(outer_entry) == 3:
                layer_name = outer_entry[2]
            else:
                layer_name = f"layer_{layer_count}"

        pairs.append(
            {
                "type": outer_entry[0],
                "name": layer_name,
                "offsets": (
                    cumulative_thickness_orb,
                    cumulative_thickness_uvb,
                    cumulative_thickness_irb,
                    cumulative_thickness_lvb,
                ),
                "thicknesses": (
                    outer_layer_thickness,
                    upper_layer_thickness,
                    inner_layer_thickness,
                    lower_layer_thickness,
                ),
            }
        )

        cumulative_thickness_orb += outer_layer_thickness
        cumulative_thickness_irb += inner_layer_thickness
        cumulative_thickness_uvb += upper_layer_thickness
        cumulative_thickness_lvb += lower_layer_thickness

    return pairs


def poloidal_profile(outer, upper, inner, lower):
    """Returns a function of poloidal angle (degrees, measured counter
    clockwise from the outboard midplane) that varies smoothly between the
    values at the outboard midplane, top, inboard midplane and bottom, so the
    layer has no corners where the radial and vertical builds differ. Used for
    the thickness and offset of every layer."""

    return smooth_profile([0, 90, 180, 270, 360], [outer, upper, inner, lower, outer], period=360)


def create_layer(pair, minor_radius, major_radius, triangularity, elongation, rotation_angle):
    """Builds the full (unsegmented) solid of a layer pair from an outboard
    and an inboard half."""
    thickness = poloidal_profile(*pair["thicknesses"])
    offset = poloidal_profile(*pair["offsets"])
    outer_layer = blanket_from_plasma(
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        thickness=thickness,
        offset_from_plasma=offset,
        start_angle=90,
        stop_angle=-90,
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name=pair["name"],
        allow_overlapping_shape=True,
    )
    inner_layer = blanket_from_plasma(
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        thickness=thickness,
        offset_from_plasma=offset,
        start_angle=-90,
        stop_angle=-270,
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name=pair["name"],
        allow_overlapping_shape=True,
    )
    layer = outer_layer.union(inner_layer)
    layer.name = pair["name"]
    return layer


def create_poloidal_segments(
    pair, segment_angles, minor_radius, major_radius, triangularity, elongation, rotation_angle
):
    """Builds one solid per poloidal segment of a layer pair.

    The full layer is built as it would be without segmentation and each
    segment is cut out of it, so the faces of the segments are the faces of
    the full layer. This keeps them coincident with the neighbouring layers,
    which boolean operations (such as making a divertor) rely on.
    """
    layer = create_layer(pair, minor_radius, major_radius, triangularity, elongation, rotation_angle)

    # a single segment covering the whole loop is the full layer
    if len(segment_angles) == 1 and segment_angles[0][2] - segment_angles[0][1] >= 360.0 - 1e-9:
        layer.name = f"{pair['name']}_{segment_angles[0][0]}"
        return [layer]

    offset = poloidal_profile(*pair["offsets"])
    thickness = poloidal_profile(*pair["thicknesses"])
    # the cutting regions extend past the inner and outer surfaces of the layer
    margin = 0.05 * minor_radius

    solids = []
    for segment_name, start_angle, stop_angle in segment_angles:
        # the sides of the cutting region follow the normal to the plasma surface
        # at the start and stop angles, the same direction the layers are offset in
        thetas = np.linspace(start_angle, stop_angle, max(10, math.ceil(400 * (stop_angle - start_angle) / 360)))
        inner_r, inner_z = offset_curve_coordinates(
            major_radius, minor_radius, triangularity, elongation, 0.0, thetas, offset(thetas) - margin
        )
        outer_r, outer_z = offset_curve_coordinates(
            major_radius,
            minor_radius,
            triangularity,
            elongation,
            0.0,
            thetas[::-1],
            offset(thetas[::-1]) + thickness(thetas[::-1]) + margin,
        )
        # the region must not cross the axis it is revolved around
        points = list(zip(np.maximum(np.concatenate([inner_r, outer_r]), 0.0), np.concatenate([inner_z, outer_z])))
        cutting_region = cq.Workplane("XZ").polyline(points).close().revolve(360)

        name = f"{pair['name']}_{segment_name}"
        solid = layer.intersect(cutting_region)
        check_not_empty(solid, f"Poloidal segment {name}")
        solid.name = name
        solids.append(solid)
    return solids


def create_layers_from_plasma(
    radial_build,
    vertical_build,
    minor_radius,
    major_radius,
    triangularity,
    elongation,
    rotation_angle,
    center_column,
    layer_count=0,
    poloidal_segment_angles=None,
):
    pairs = get_layer_pairs(radial_build, vertical_build, layer_count)
    if poloidal_segment_angles is None:
        poloidal_segment_angles = [None] * len(pairs)

    layers = []
    for pair, segment_angles in zip(pairs, poloidal_segment_angles):
        if pair["type"] != LayerType.SOLID:
            continue

        if segment_angles is not None:
            layers.extend(
                create_poloidal_segments(
                    pair, segment_angles, minor_radius, major_radius, triangularity, elongation, rotation_angle
                )
            )
            continue

        layers.append(
            create_layer(pair, minor_radius, major_radius, triangularity, elongation, rotation_angle)
        )

    return layers


def vertical_build_from_radial_build(radial_build, elongation):
    """Makes the vertical build used by tokamak_from_plasma, where the layers
    above and below the plasma have the same thickness as the inboard layers."""
    minor_radius = get_plasma_value(radial_build) / 2

    # make vertical build from inner radial build
    pi = get_plasma_index(radial_build)
    rbi = len(radial_build) - 1 - pi  # number of unique entries in outer or inner radial build
    # drop any layer names, they are only supported in radial_build not vertical_build
    upper_vertical_build = [(item[0], item[1]) for item in radial_build[pi - rbi : pi][::-1]]  # get the inner radial build

    plasma_height = 2 * minor_radius * elongation
    # slice operation reverses the list and removes the last value to avoid two plasmas
    return upper_vertical_build[::-1] + [(LayerType.PLASMA, plasma_height)] + upper_vertical_build


def get_reference_arc_length_table(radial_build, vertical_build, triangularity):
    """Returns the (angles, cumulative arc lengths) table of the reference
    surface that poloidal_build arc lengths are measured on. This is the
    plasma facing surface, the inner surface of the first solid layer after
    the plasma."""
    for pair in get_layer_pairs(radial_build, vertical_build):
        if pair["type"] == LayerType.SOLID:
            major_radius, minor_radius, elongation = get_plasma_geometry(radial_build, vertical_build)
            return poloidal_arc_length_table(
                major_radius=major_radius,
                minor_radius=minor_radius,
                triangularity=triangularity,
                elongation=elongation,
                offset=poloidal_profile(*pair["offsets"]),
            )
    raise ValueError("The radial_build has no LayerType.SOLID entries after the plasma to segment.")


def get_poloidal_build_segment_angles(
    poloidal_build, radial_build, vertical_build, triangularity, layer_count=0
):
    """Validates poloidal_build and converts the segment arc lengths into
    poloidal angles for each layer pair. All arc lengths are measured on the
    same reference surface, so layers with the same segments line up."""
    pairs = get_layer_pairs(radial_build, vertical_build, layer_count)
    validate_poloidal_build(poloidal_build, pairs)
    if all(segments is None for segments in poloidal_build):
        return list(poloidal_build)

    arc_thetas, arc_lengths = get_reference_arc_length_table(radial_build, vertical_build, triangularity)
    return [
        None if segments is None else get_poloidal_segment_angles(segments, arc_thetas, arc_lengths, index, "poloidal_arc_length")
        for index, segments in enumerate(poloidal_build)
    ]


def poloidal_arc_length(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    elongation: float | None = None,
    triangularity: float = 0.55,
    vertical_build: Sequence[tuple[LayerType, float]] | None = None,
) -> float:
    """Returns the poloidal arc length that the segments in a poloidal_build
    must sum to.

    The arc length is measured around the full poloidal loop of the plasma
    facing surface, which is the inner surface of the first solid layer after
    the plasma. All poloidal_build entries are measured on this surface, so
    layers given the same segments line up.

    Args:
        radial_build: the radial build of the reactor, as passed to
            tokamak_from_plasma or tokamak.
        elongation: the elongation of the plasma, as passed to
            tokamak_from_plasma. Defaults to 2.0. Must not be set when a
            vertical_build is provided, as the elongation is then calculated
            from the builds.
        triangularity: the triangularity of the plasma. Defaults to 0.55.
        vertical_build: the vertical build of the reactor, as passed to
            tokamak. Leave as None for tokamak_from_plasma.

    Returns:
        float: the poloidal arc length of the plasma facing surface.
    """
    vertical_build = resolve_vertical_build(
        radial_build, elongation, vertical_build, vertical_build_from_radial_build
    )
    _, arc_lengths = get_reference_arc_length_table(radial_build, vertical_build, triangularity)
    return float(arc_lengths[-1])


def tokamak_from_plasma(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    elongation: float = 2.0,
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] | None = None,
    extra_intersect_shapes: Sequence[cq.Workplane] | None = None,
    colors: dict | None = None,
    poloidal_build: Sequence[Sequence[tuple[str, float]] | None] | None = None,
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
        poloidal_build: optional poloidal segmentation of the layers. A list
            with one entry per radial_build entry after the plasma, ordered
            from the plasma outwards, so each entry covers the matching
            inboard and outboard layer pair. Entries are None for layers that
            are not segmented (and must be None for LayerType.GAP entries),
            otherwise a list of segments in the same format as radial_build
            entries: (paramak.LayerType.SOLID, arc_length, name) for a solid
            segment (the name is optional) or (paramak.LayerType.GAP,
            arc_length) for a gap that produces no solid. Arc lengths are
            measured along the plasma facing surface (the inner surface of
            the first solid layer after the plasma) for every layer, starting
            at the outboard midplane and proceeding counter clockwise
            (upwards on the outboard side). Each entry must sum to the arc
            length returned by paramak.poloidal_arc_length (within 0.1
            percent). Cuts between segments follow the normal to the plasma
            surface, so layers given the same segments line up. Solid
            segments are named "<layer name>_<segment name>", unnamed solid
            segments are called "segment", and repeated names within a layer
            get a "_1", "_2" suffix. Defaults to None.

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the tokamak fusion reactor.
    """

    if extra_cut_shapes is None:
        extra_cut_shapes = []
    if extra_intersect_shapes is None:
        extra_intersect_shapes = []
    if colors is None:
        colors = {}

    vertical_build = vertical_build_from_radial_build(radial_build, elongation)

    return tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=extra_intersect_shapes,
        colors=colors,
        poloidal_build=poloidal_build,
    )


def tokamak(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    vertical_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] | None = None,
    extra_intersect_shapes: Sequence[cq.Workplane] | None = None,
    colors: dict | None = None,
    poloidal_build: Sequence[Sequence[tuple[str, float]] | None] | None = None,
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
        poloidal_build: optional poloidal segmentation of the layers. A list
            with one entry per radial_build entry after the plasma, ordered
            from the plasma outwards, so each entry covers the matching
            inboard and outboard layer pair. Entries are None for layers that
            are not segmented (and must be None for LayerType.GAP entries),
            otherwise a list of segments in the same format as radial_build
            entries: (paramak.LayerType.SOLID, arc_length, name) for a solid
            segment (the name is optional) or (paramak.LayerType.GAP,
            arc_length) for a gap that produces no solid. Arc lengths are
            measured along the plasma facing surface (the inner surface of
            the first solid layer after the plasma) for every layer, starting
            at the outboard midplane and proceeding counter clockwise
            (upwards on the outboard side). Each entry must sum to the arc
            length returned by paramak.poloidal_arc_length (within 0.1
            percent). Cuts between segments follow the normal to the plasma
            surface, so layers given the same segments line up. Solid
            segments are named "<layer name>_<segment name>", unnamed solid
            segments are called "segment", and repeated names within a layer
            get a "_1", "_2" suffix. Defaults to None.

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

    major_radius, minor_radius, elongation = get_plasma_geometry(radial_build, vertical_build)
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

    # validated before the blanket layers are built so errors are raised quickly
    poloidal_segment_angles = None
    if poloidal_build is not None:
        poloidal_segment_angles = get_poloidal_build_segment_angles(
            poloidal_build, radial_build, vertical_build, triangularity, layer_count=len(inner_radial_build)
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
        layer_count=len(inner_radial_build),
        poloidal_segment_angles=poloidal_segment_angles,
    )

    cut_names, intersect_names, layer_names = get_assembly_names(
        extra_cut_shapes, extra_intersect_shapes, inner_radial_build, blanket_layers
    )

    validate_unique_assembly_names([*cut_names, *intersect_names, *layer_names, "plasma"], "tokamak()")

    my_assembly = Assembly()

    for entry, name in zip(extra_cut_shapes, cut_names):
        if not isinstance(entry, cq.Workplane):
            raise TypeError(f"extra_cut_shapes should only contain cadquery Workplanes, not {type(entry)}")
        my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    # builds up the intersect shapes
    if len(extra_intersect_shapes) > 0:
        if poloidal_build is None:
            # makes a union of the the radial build to use as a base for the intersect shapes
            reactor_compound = inner_radial_build[0]
            for entry in inner_radial_build[1:] + blanket_layers:
                reactor_compound = reactor_compound.union(entry)

        # adds the extra intersect shapes to the assembly
        for entry, name in zip(extra_intersect_shapes, intersect_names):
            if poloidal_build is None:
                reactor_entry_intersection = entry.intersect(reactor_compound)
            else:
                # poloidal segments share many faces with their neighbours, which
                # makes fusing all the parts unreliable, so the shape is intersected
                # with each part and the pieces are kept together in a compound
                reactor_entry_intersection = intersect_with_each_part(entry, inner_radial_build + blanket_layers)
            my_assembly.add(reactor_entry_intersection, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    # cut the core layers with any extra shapes (a no-op when there are none)
    cutters = extra_cut_shapes + extra_intersect_shapes
    for entry, name in zip(inner_radial_build + blanket_layers, layer_names):
        # TODO track the names of shapes, even when extra shapes are made due to splitting
        for cutter in cutters:
            entry = entry.cut(cutter)
        my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    my_assembly.add(plasma, name="plasma", color=cq.Color(*colors.get("plasma", (0.5,0.5,0.5))))

    my_assembly.elongation = elongation
    my_assembly.triangularity = triangularity
    my_assembly.major_radius = major_radius
    my_assembly.minor_radius = minor_radius

    return my_assembly
