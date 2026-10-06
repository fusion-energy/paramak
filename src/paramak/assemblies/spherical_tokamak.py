from __future__ import annotations

import math
from typing import Sequence

import cadquery as cq
import numpy as np

from ..utils import (
    LayerType,
    get_assembly_names,
    get_layer_name,
    get_plasma_index,
    get_plasma_value,
    sum_before_after_plasma,
    sum_up_to_gap_before_plasma,
    sum_up_to_plasma,
    validate_unique_assembly_names,
    validate_vertical_build_names,
)
from ..workplanes.blanket_from_plasma import blanket_from_plasma, offset_curve_coordinates
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified
from .assembly import Assembly
from .toroidal import apply_toroidal_sectors, get_toroidal_build_sectors
from .poloidal import SegmentBuild, get_poloidal_segment_angles, intersect_with_each_part, validate_segment_build


def get_spherical_layer_pairs(radial_build, vertical_build, layer_count=0):
    """Describes each layer after the plasma, ordered from the plasma outwards.
    This is the ordering used by poloidal_build.

    Returns:
        list of dict: one entry per radial_build entry after the plasma with the
        keys "type", "name" (None for GAP entries), "offsets" and "thicknesses".
        The offsets and thicknesses are tuples of values at poloidal angles of
        -90, 0 and 90 degrees.
    """
    plasma_index_radial = get_plasma_index(radial_build)
    plasma_index_vertical = get_plasma_index(vertical_build)

    pairs = []
    cumulative_thickness_rb = 0
    cumulative_thickness_uvb = 0
    cumulative_thickness_lvb = 0

    for i, item in enumerate(radial_build[plasma_index_radial + 1 :]):
        upper_thickness = vertical_build[plasma_index_vertical + 1 + i][1]
        lower_thickness = vertical_build[plasma_index_vertical - 1 - i][1]
        radial_thickness = item[1]

        if item[0] == LayerType.GAP:
            layer_name = None
        else:
            layer_count += 1
            layer_name = get_layer_name(item, layer_count)

        pairs.append(
            {
                "type": item[0],
                "name": layer_name,
                "offsets": (cumulative_thickness_lvb, cumulative_thickness_rb, cumulative_thickness_uvb),
                "thicknesses": (lower_thickness, radial_thickness, upper_thickness),
            }
        )

        cumulative_thickness_rb += radial_thickness
        cumulative_thickness_uvb += upper_thickness
        cumulative_thickness_lvb += lower_thickness

    return pairs


def spherical_profile(lower, outboard, upper):
    """Returns a function of poloidal angle (degrees, -90 to 90) that varies
    linearly between the values at -90, 0 and 90 degrees. This matches the
    interpolation used when a layer is built without poloidal segments."""

    def profile(theta):
        return np.interp(theta, [-90.0, 0.0, 90.0], [lower, outboard, upper])

    return profile


def spherical_path_coordinates(path_positions, offset, geometry):
    """R and Z coordinates along the open path followed by a spherical tokamak
    layer, offset from the plasma by the offset function of poloidal angle.

    The path runs from the centre column along the bottom of the layer
    (positions 0 to 1), around the outboard side of the plasma from -90 to 90
    degrees (positions 1 to 2) and back along the top to the centre column
    (positions 2 to 3). The top and bottom are flat, so the radius at a given
    position is the same for every layer, which keeps segments with the same
    boundaries lined up.
    """
    major_radius, minor_radius, triangularity, elongation, column_radius = geometry
    path_positions = np.asarray(path_positions, dtype=float)
    thetas = np.clip(-90.0 + 180.0 * (path_positions - 1.0), -90.0, 90.0)
    offsets = offset(thetas)
    curve_r, curve_z = offset_curve_coordinates(
        major_radius, minor_radius, triangularity, elongation, 0.0, thetas, offsets
    )
    # radius of the plasma surface at the top and bottom, where the normal is vertical
    edge_radius = major_radius + minor_radius * math.cos(math.pi / 2 + triangularity)
    flat_length = edge_radius - column_radius
    r = np.where(
        path_positions < 1.0,
        column_radius + path_positions * flat_length,
        np.where(path_positions > 2.0, edge_radius - (path_positions - 2.0) * flat_length, curve_r),
    )
    z = np.where(
        path_positions < 1.0,
        -elongation * minor_radius - offsets,
        np.where(path_positions > 2.0, elongation * minor_radius + offsets, curve_z),
    )
    return r, z


def spherical_arc_length_table(offset, geometry):
    """Positions along the spherical tokamak layer path and the cumulative arc
    length at each position."""
    path_positions = np.concatenate(
        [np.linspace(0.0, 1.0, 51), np.linspace(1.0, 2.0, 3601)[1:], np.linspace(2.0, 3.0, 51)[1:]]
    )
    r, z = spherical_path_coordinates(path_positions, offset, geometry)
    arc_lengths = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(r), np.diff(z)))])
    return path_positions, arc_lengths


def create_spherical_layer(pair, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column):
    """Builds the full (unsegmented) solid of a spherical tokamak layer."""
    lower_offset, outboard_offset, upper_offset = pair["offsets"]
    lower_thickness, radial_thickness, upper_thickness = pair["thicknesses"]
    layer = blanket_from_plasma(
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        thickness=[lower_thickness, radial_thickness, upper_thickness],
        offset_from_plasma=[lower_offset, outboard_offset, upper_offset],
        start_angle=-90,
        stop_angle=90,
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name=pair["name"],
        allow_overlapping_shape=True,
        connect_to_center=True,
    )
    layer = layer.cut(center_column)
    layer.name = pair["name"]
    return layer


def create_spherical_poloidal_segments(pair, segment_positions, geometry, rotation_angle, center_column):
    """Builds one solid per poloidal segment of a spherical tokamak layer by
    cutting each segment out of the full layer, so the faces of the segments
    are the faces of the full layer."""
    major_radius, minor_radius, triangularity, elongation, column_radius = geometry
    layer = create_spherical_layer(
        pair, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column
    )

    # a single segment covering the whole path is the full layer
    if len(segment_positions) == 1 and segment_positions[0][2] - segment_positions[0][1] >= 3.0 - 1e-9:
        layer.name = f"{pair['name']}_{segment_positions[0][0]}"
        return [layer]

    offset = spherical_profile(*pair["offsets"])
    thickness = spherical_profile(*pair["thicknesses"])
    # the cutting regions extend past the surfaces of the layer
    margin = 0.05 * minor_radius

    def inner_offset(theta):
        return offset(theta) - margin

    def outer_offset(theta):
        return offset(theta) + thickness(theta) + margin

    solids = []
    for segment_name, start, stop in segment_positions:
        path_positions = np.linspace(start, stop, max(10, math.ceil(400 * (stop - start) / 2)))
        inner_r, inner_z = spherical_path_coordinates(path_positions, inner_offset, geometry)
        outer_r, outer_z = spherical_path_coordinates(path_positions[::-1], outer_offset, geometry)
        # segments that reach the centre column extend past it so the layer end is included
        if start <= 1e-9:
            inner_r[0] = column_radius - margin
            outer_r[-1] = column_radius - margin
        if stop >= 3.0 - 1e-9:
            inner_r[-1] = column_radius - margin
            outer_r[0] = column_radius - margin
        points = list(zip(np.concatenate([inner_r, outer_r]), np.concatenate([inner_z, outer_z])))
        cutting_region = cq.Workplane("XZ").polyline(points).close().revolve(360)

        name = f"{pair['name']}_{segment_name}"
        solid = layer.intersect(cutting_region)
        solid.name = name
        solids.append(solid)
    return solids


def create_blanket_layers_after_plasma(
    radial_build,
    vertical_build,
    minor_radius,
    major_radius,
    triangularity,
    elongation,
    rotation_angle,
    center_column,
    layer_count=0,
    poloidal_segment_positions=None,
    toroidal_sectors=None,
    toroidal_region_size=None,
):
    pairs = get_spherical_layer_pairs(radial_build, vertical_build, layer_count)
    if poloidal_segment_positions is None:
        poloidal_segment_positions = [None] * len(pairs)
    if toroidal_sectors is None:
        toroidal_sectors = [None] * len(pairs)
    geometry = (major_radius, minor_radius, triangularity, elongation, sum_up_to_gap_before_plasma(radial_build))

    layers = []
    for pair, segment_positions, sectors in zip(pairs, poloidal_segment_positions, toroidal_sectors):
        if pair["type"] == LayerType.GAP:
            continue
        if segment_positions is not None:
            pair_solids = create_spherical_poloidal_segments(
                pair, segment_positions, geometry, rotation_angle, center_column
            )
        else:
            pair_solids = [
                create_spherical_layer(
                    pair, minor_radius, major_radius, triangularity, elongation, rotation_angle, center_column
                )
            ]
        if sectors is not None:
            pair_solids = apply_toroidal_sectors(pair_solids, sectors, rotation_angle, toroidal_region_size)
        layers.extend(pair_solids)

    return layers


def get_spherical_plasma_geometry(radial_build, vertical_build):
    """Returns the major radius, minor radius and elongation of the plasma
    defined by the radial and vertical builds."""
    inner_equatorial_point = sum_up_to_plasma(radial_build)
    outer_equatorial_point = inner_equatorial_point + get_plasma_value(radial_build)
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point
    elongation = (get_plasma_value(vertical_build) / 2) / minor_radius
    return major_radius, minor_radius, elongation


def spherical_vertical_build_from_radial_build(radial_build, elongation):
    """Makes the vertical build used by spherical_tokamak_from_plasma, where
    the layers above and below the plasma have the same thickness as the
    outboard layers."""
    minor_radius = get_plasma_value(radial_build) / 2
    pi = get_plasma_index(radial_build)
    # drop any layer names, they are only supported in radial_build not vertical_build
    upper_vertical_build = [(item[0], item[1]) for item in radial_build[pi:]]
    plasma_height = 2 * minor_radius * elongation
    # slice operation reverses the list and removes the last value to avoid two plasmas
    return upper_vertical_build[::-1][:-1] + [(LayerType.PLASMA, plasma_height)] + upper_vertical_build[1:]


def get_spherical_reference_arc_length_table(radial_build, vertical_build, triangularity):
    """Returns the (path positions, cumulative arc lengths) table of the plasma
    facing surface, the inner surface of the first solid layer after the
    plasma, which poloidal_build arc lengths are measured on."""
    major_radius, minor_radius, elongation = get_spherical_plasma_geometry(radial_build, vertical_build)
    geometry = (major_radius, minor_radius, triangularity, elongation, sum_up_to_gap_before_plasma(radial_build))
    for pair in get_spherical_layer_pairs(radial_build, vertical_build):
        if pair["type"] == LayerType.SOLID:
            return spherical_arc_length_table(spherical_profile(*pair["offsets"]), geometry)
    raise ValueError("The radial_build has no LayerType.SOLID entries after the plasma to segment.")


def get_spherical_poloidal_build_segment_positions(
    poloidal_build, radial_build, vertical_build, triangularity, layer_count=0
):
    """Validates poloidal_build and converts the segment arc lengths into
    positions along the layer path for each layer."""
    pairs = get_spherical_layer_pairs(radial_build, vertical_build, layer_count)
    validate_segment_build(poloidal_build, pairs)
    if all(segments is None for segments in poloidal_build):
        return list(poloidal_build)

    path_positions, arc_lengths = get_spherical_reference_arc_length_table(radial_build, vertical_build, triangularity)
    return [
        None
        if segments is None
        else get_poloidal_segment_angles(
            segments, path_positions, arc_lengths, index, "spherical_poloidal_arc_length"
        )
        for index, segments in enumerate(poloidal_build)
    ]


def spherical_poloidal_arc_length(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    elongation: float | None = None,
    triangularity: float = 0.55,
    vertical_build: Sequence[tuple[LayerType, float]] | None = None,
) -> float:
    """Returns the arc length that the segments in a spherical tokamak
    poloidal_build must sum to.

    The arc length is measured along the plasma facing surface, which is the
    inner surface of the first solid layer after the plasma. This surface runs
    from the centre column along the bottom of the layer, around the outboard
    side of the plasma and back along the top of the layer to the centre
    column. All poloidal_build entries are measured on this surface, so layers
    given the same segments line up.

    Args:
        radial_build: the radial build of the reactor, as passed to
            spherical_tokamak_from_plasma or spherical_tokamak.
        elongation: the elongation of the plasma, as passed to
            spherical_tokamak_from_plasma. Defaults to 2.0. Must not be set
            when a vertical_build is provided, as the elongation is then
            calculated from the builds.
        triangularity: the triangularity of the plasma. Defaults to 0.55.
        vertical_build: the vertical build of the reactor, as passed to
            spherical_tokamak. Leave as None for spherical_tokamak_from_plasma.

    Returns:
        float: the arc length of the plasma facing surface.
    """
    if vertical_build is None:
        vertical_build = spherical_vertical_build_from_radial_build(
            radial_build, 2.0 if elongation is None else elongation
        )
    elif elongation is not None:
        raise ValueError(
            "elongation can not be set when a vertical_build is provided, "
            "the elongation is calculated from the radial_build and vertical_build."
        )
    _, arc_lengths = get_spherical_reference_arc_length_table(radial_build, vertical_build, triangularity)
    return float(arc_lengths[-1])


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
        layer_name = get_layer_name(item, layer_count)

        cylinder = center_column_shield_cylinder(
            inner_radius=total_sum,
            thickness=item[1],
            name=layer_name,
            rotation_angle=rotation_angle,
            height=center_column_shield_height,
            reference_point=("lower", -before),
        )
        cylinders.append(cylinder)
        total_sum += item[1]

    return cylinders


def spherical_tokamak_from_plasma(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    elongation: float = 2.0,
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] | None = None,
    extra_intersect_shapes: Sequence[cq.Workplane] | None = None,
    colors: dict | None = None,
    poloidal_build: SegmentBuild | None = None,
    toroidal_build: SegmentBuild | None = None,
) -> Assembly:
    """Creates a spherical tokamak fusion reactor from a radial build and plasma parameters.

    Args:
        radial_build: sequence of tuples containing the radial build of the
            reactor. Each tuple should contain a LayerType, a float and the string is optional.
        elongation: The elongation of the plasma. Defaults to 2.0.
        triangularity: The triangularity of the plasma. Defaults to 0.55.
        rotation_angle: The rotation angle of the reactor in degrees. Defaults to 180.0.
        extra_cut_shapes: A list of extra shapes to cut the reactor with. Defaults to [].
        colors: the colors to assign to the assembly parts. Defaults to {}.
            Each dictionary entry should be a key that matches the assembly part name
            (e.g. 'plasma', or 'layer_1') and a tuple of 3 or 4 floats between 0 and 1
            representing the RGB or RGBA values.
        poloidal_build: optional poloidal segmentation of the layers after
            the plasma. A list with one entry per radial_build entry after the
            plasma, ordered from the plasma outwards. Entries are None for
            layers that are not segmented (and must be None for
            LayerType.GAP entries), otherwise a list of segments in the same
            format as radial_build entries: (paramak.LayerType.SOLID,
            arc_length, name) for a solid segment (the name is optional) or
            (paramak.LayerType.GAP, arc_length) for a gap that produces no
            solid. Arc lengths are measured along the plasma facing surface
            (the inner surface of the first solid layer after the plasma) for
            every layer, starting where the layer meets the centre column at
            the bottom and going along the bottom, up the outboard side and
            along the top back to the centre column. Each entry must sum to
            the arc length returned by paramak.spherical_poloidal_arc_length
            (within 0.1 percent). Cuts between segments are vertical along the
            top and bottom and follow the normal to the plasma surface on the
            outboard side, so layers given the same segments line up. Solid
            segments are named "<layer name>_<segment name>", unnamed solid
            segments are called "segment", and repeated names within a layer
            get a "_1", "_2" suffix. Defaults to None.
        toroidal_build: optional toroidal segmentation of the layers, for
            example into sectors separated by assembly gaps. A list with one
            entry per radial_build entry after the plasma, ordered from the
            plasma outwards, like poloidal_build. Entries are None for layers
            that are not segmented (and must be None for LayerType.GAP
            entries), otherwise a list of segments: (paramak.LayerType.SOLID,
            arc_length, name) for a sector (the name is optional) or
            (paramak.LayerType.GAP, width) for a gap. Arc lengths are measured
            around the plasma facing surface at the outboard midplane,
            starting at the XZ plane and going in the direction the reactor is
            revolved, and each entry must sum to the arc length returned by
            paramak.toroidal_arc_length (within 0.1 percent). Gaps are slots
            with parallel sides, so a gap has the same width at every radius.
            Sectors are named "<layer name>_<sector name>", or
            "<layer name>_<poloidal segment name>_<sector name>" when the
            layer also has a poloidal_build entry. Defaults to None.

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the spherical tokamak fusion reactor.
    """

    if extra_cut_shapes is None:
        extra_cut_shapes = []
    if extra_intersect_shapes is None:
        extra_intersect_shapes = []
    if colors is None:
        colors = {}

    vertical_build = spherical_vertical_build_from_radial_build(radial_build, elongation)

    return spherical_tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=extra_intersect_shapes,
        colors=colors,
        poloidal_build=poloidal_build,
        toroidal_build=toroidal_build,
    )


def spherical_tokamak(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    vertical_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    triangularity: float = 0.55,
    rotation_angle: float = 180.0,
    extra_cut_shapes: Sequence[cq.Workplane] | None = None,
    extra_intersect_shapes: Sequence[cq.Workplane] | None = None,
    colors: dict | None = None,
    poloidal_build: SegmentBuild | None = None,
    toroidal_build: SegmentBuild | None = None,
) -> Assembly:
    """Creates a spherical tokamak fusion reactor from a radial build and vertical build.

    Args:
        radial_build: sequence of tuples containing the radial build of the
            reactor. Each tuple should contain a LayerType, a float and the string is optional.
        vertical_build: sequence of tuples containing the vertical build of the
            reactor. Each tuple should contain a LayerType, a float and the string is optional.
        triangularity: The triangularity of the plasma. Defaults to 0.55.
        rotation_angle: The rotation angle of the reactor in degrees. Defaults to 180.0.
        extra_cut_shapes: A list of extra shapes to cut the reactor with. Defaults to [].
        extra_intersect_shapes: A list of extra shapes to intersect the reactor with. Defaults to [].
        colors: the colors to assign to the assembly parts. Defaults to {}.
            Each dictionary entry should be a key that matches the assembly part name
            (e.g. 'plasma', or 'layer_1') and a tuple of 3 or 4 floats between 0 and 1
            representing the RGB or RGBA values.
        poloidal_build: optional poloidal segmentation of the layers after
            the plasma. A list with one entry per radial_build entry after the
            plasma, ordered from the plasma outwards. Entries are None for
            layers that are not segmented (and must be None for
            LayerType.GAP entries), otherwise a list of segments in the same
            format as radial_build entries: (paramak.LayerType.SOLID,
            arc_length, name) for a solid segment (the name is optional) or
            (paramak.LayerType.GAP, arc_length) for a gap that produces no
            solid. Arc lengths are measured along the plasma facing surface
            (the inner surface of the first solid layer after the plasma) for
            every layer, starting where the layer meets the centre column at
            the bottom and going along the bottom, up the outboard side and
            along the top back to the centre column. Each entry must sum to
            the arc length returned by paramak.spherical_poloidal_arc_length
            (within 0.1 percent). Cuts between segments are vertical along the
            top and bottom and follow the normal to the plasma surface on the
            outboard side, so layers given the same segments line up. Solid
            segments are named "<layer name>_<segment name>", unnamed solid
            segments are called "segment", and repeated names within a layer
            get a "_1", "_2" suffix. Defaults to None.
        toroidal_build: optional toroidal segmentation of the layers, for
            example into sectors separated by assembly gaps. A list with one
            entry per radial_build entry after the plasma, ordered from the
            plasma outwards, like poloidal_build. Entries are None for layers
            that are not segmented (and must be None for LayerType.GAP
            entries), otherwise a list of segments: (paramak.LayerType.SOLID,
            arc_length, name) for a sector (the name is optional) or
            (paramak.LayerType.GAP, width) for a gap. Arc lengths are measured
            around the plasma facing surface at the outboard midplane,
            starting at the XZ plane and going in the direction the reactor is
            revolved, and each entry must sum to the arc length returned by
            paramak.toroidal_arc_length (within 0.1 percent). Gaps are slots
            with parallel sides, so a gap has the same width at every radius.
            Sectors are named "<layer name>_<sector name>", or
            "<layer name>_<poloidal segment name>_<sector name>" when the
            layer also has a poloidal_build entry. Defaults to None.

    Returns:
        CadQuery.Assembly: A CadQuery Assembly object representing the spherical tokamak fusion reactor.
    """

    if extra_cut_shapes is None:
        extra_cut_shapes = []
    if extra_intersect_shapes is None:
        extra_intersect_shapes = []
    if colors is None:
        colors = {}

    validate_vertical_build_names(vertical_build, "spherical_tokamak()")

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

    # validated before the blanket layers are built so errors are raised quickly
    poloidal_segment_positions = None
    if poloidal_build is not None:
        poloidal_segment_positions = get_spherical_poloidal_build_segment_positions(
            poloidal_build, radial_build, vertical_build, triangularity, layer_count=len(inner_radial_build)
        )
    toroidal_sectors = None
    if toroidal_build is not None:
        toroidal_sectors = get_toroidal_build_sectors(
            toroidal_build, get_spherical_layer_pairs(radial_build, vertical_build), radial_build, rotation_angle
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
        layer_count=len(inner_radial_build),
        poloidal_segment_positions=poloidal_segment_positions,
        toroidal_sectors=toroidal_sectors,
        toroidal_region_size=4 * max(sum(item[1] for item in radial_build), blanket_rear_wall_end_height),
    )

    cut_names, intersect_names, layer_names = get_assembly_names(
        extra_cut_shapes, extra_intersect_shapes, inner_radial_build, blanket_layers
    )

    validate_unique_assembly_names([*cut_names, *intersect_names, *layer_names, "plasma"], "spherical_tokamak()")

    my_assembly = Assembly()

    for entry, name in zip(extra_cut_shapes, cut_names):
        if not isinstance(entry, cq.Workplane):
            raise TypeError(f"extra_cut_shapes should only contain cadquery Workplanes, not {type(entry)}")
        my_assembly.add(entry, name=name, color=cq.Color(*colors.get(name, (0.5,0.5,0.5))))

    # builds up the intersect shapes
    segmented = poloidal_build is not None or toroidal_build is not None
    if len(extra_intersect_shapes) > 0:
        if not segmented:
            # makes a union of the the radial build to use as a base for the intersect shapes
            reactor_compound = inner_radial_build[0]
            for entry in inner_radial_build[1:] + blanket_layers:
                reactor_compound = reactor_compound.union(entry)

        # adds the extra intersect shapes to the assembly
        for entry, name in zip(extra_intersect_shapes, intersect_names):
            if not segmented:
                reactor_entry_intersection = entry.intersect(reactor_compound)
            else:
                # segments share many faces with their neighbours, which
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
