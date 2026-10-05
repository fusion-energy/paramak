from __future__ import annotations

import math
import numbers
from collections import Counter
from typing import Sequence

import cadquery as cq
import numpy as np

from ..utils import (
    LayerType,
    get_assembly_names,
    get_layer_name,
    get_plasma_index,
    validate_unique_assembly_names,
    validate_vertical_build_names,
)
from ..workplanes.blanket_from_plasma import blanket_from_plasma, poloidal_arc_length_table
from ..workplanes.center_column_shield_cylinder import center_column_shield_cylinder
from ..workplanes.plasma_simplified import plasma_simplified
from .assembly import Assembly
from .spherical_tokamak import get_plasma_value, sum_up_to_plasma

# relative tolerance allowed between the sum of the arc lengths in a
# poloidal_build entry and the actual arc length of that layer
POLOIDAL_ARC_LENGTH_RTOL = 1e-3


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
    clockwise from the outboard midplane) that varies linearly between the
    values at the outboard midplane, top, inboard midplane and bottom. This
    matches the interpolation used when a layer is built without poloidal
    segments."""

    angles = [0.0, 90.0, 180.0, 270.0, 360.0]
    values = [outer, upper, inner, lower, outer]

    def profile(theta):
        return np.interp(np.mod(theta, 360.0), angles, values)

    return profile


def validate_poloidal_build(poloidal_build, pairs):
    """Checks the structure of poloidal_build against the layer pairs."""
    if not isinstance(poloidal_build, (list, tuple)):
        raise TypeError(f"poloidal_build must be a list, not {type(poloidal_build)}")
    if len(poloidal_build) != len(pairs):
        raise ValueError(
            f"poloidal_build must have one entry per radial_build entry after the plasma "
            f"(ordered from the plasma outwards), expected {len(pairs)} entries but got {len(poloidal_build)}."
        )
    for index, (pair, segments) in enumerate(zip(pairs, poloidal_build)):
        if segments is None:
            continue
        if pair["type"] == LayerType.GAP:
            raise ValueError(
                f"poloidal_build entry {index} corresponds to a LayerType.GAP in the radial_build "
                f"and must be None, not {segments}."
            )
        if not isinstance(segments, (list, tuple)) or len(segments) == 0:
            raise TypeError(
                f"poloidal_build entry {index} must be None or a non empty list of (name, arc_length) tuples, "
                f"not {segments}."
            )
        for segment in segments:
            if (
                not isinstance(segment, (list, tuple))
                or len(segment) != 2
                or not isinstance(segment[0], str)
                or not isinstance(segment[1], numbers.Real)
            ):
                raise TypeError(
                    f"Each segment in poloidal_build entry {index} must be a (name, arc_length) tuple "
                    f"with a string name and a numeric arc_length, not {segment}."
                )
            name, arc_length = segment
            if name == "gap":
                if arc_length < 0:
                    raise ValueError(
                        f"gap segments in poloidal_build entry {index} must have an arc_length of 0 or more, "
                        f"not {arc_length}."
                    )
            elif arc_length <= 0:
                raise ValueError(
                    f"Segment '{name}' in poloidal_build entry {index} must have a positive arc_length, "
                    f"not {arc_length}."
                )
        if all(segment[0] == "gap" for segment in segments):
            raise ValueError(f"poloidal_build entry {index} must contain at least one segment that is not a gap.")


def get_poloidal_segment_angles(segments, arc_thetas, arc_lengths, index):
    """Converts a list of (name, arc_length) segments into a list of
    (name, start_angle, stop_angle) for the solid segments.

    Segments start at the outboard midplane and proceed counter clockwise.
    The arc lengths must sum to the total arc length of the loop (within
    POLOIDAL_ARC_LENGTH_RTOL), small differences are scaled out so the last
    segment always closes the loop.
    """
    total_arc_length = arc_lengths[-1]
    requested_arc_length = sum(segment[1] for segment in segments)
    if not math.isclose(requested_arc_length, total_arc_length, rel_tol=POLOIDAL_ARC_LENGTH_RTOL):
        raise ValueError(
            f"The arc lengths in poloidal_build entry {index} sum to {requested_arc_length}, but the arc length "
            f"of the inner surface of that layer is {total_arc_length}. Use paramak.poloidal_arc_lengths() to "
            "get the arc length of each layer."
        )
    scale = total_arc_length / requested_arc_length

    name_counts = Counter(segment[0] for segment in segments if segment[0] != "gap")
    name_seen = Counter()

    segment_angles = []
    position = 0.0
    for name, arc_length in segments:
        start_position = position
        position += arc_length * scale
        if name == "gap":
            continue
        if name_counts[name] > 1:
            name_seen[name] += 1
            name = f"{name}_{name_seen[name]}"
        start_angle = float(np.interp(start_position, arc_lengths, arc_thetas))
        stop_angle = float(np.interp(position, arc_lengths, arc_thetas))
        segment_angles.append((name, start_angle, stop_angle))
    return segment_angles


def create_poloidal_segments(
    pair, segment_angles, minor_radius, major_radius, triangularity, elongation, rotation_angle
):
    """Builds one solid per poloidal segment of a layer pair."""
    offset = poloidal_profile(*pair["offsets"])
    thickness = poloidal_profile(*pair["thicknesses"])

    solids = []
    for segment_name, start_angle, stop_angle in segment_angles:
        name = f"{pair['name']}_{segment_name}"
        # a single segment covering the full loop would give a profile whose
        # start and end faces coincide, so it is built in two halves
        if stop_angle - start_angle >= 360.0 - 1e-9:
            angle_ranges = [(start_angle, start_angle + 180.0), (start_angle + 180.0, stop_angle)]
        else:
            angle_ranges = [(start_angle, stop_angle)]

        pieces = []
        for piece_start, piece_stop in angle_ranges:
            pieces.append(
                blanket_from_plasma(
                    minor_radius=minor_radius,
                    major_radius=major_radius,
                    triangularity=triangularity,
                    elongation=elongation,
                    thickness=thickness,
                    offset_from_plasma=offset,
                    start_angle=piece_start,
                    stop_angle=piece_stop,
                    # keeps the point density of an unsegmented layer (200 points per 180 degrees)
                    num_points=max(10, math.ceil(200 * (piece_stop - piece_start) / 180)),
                    rotation_angle=rotation_angle,
                    color=(0.5, 0.5, 0.5),
                    name=name,
                    allow_overlapping_shape=True,
                )
            )
        solid = pieces[0]
        for piece in pieces[1:]:
            solid = solid.union(piece)
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

        outer_offset, upper_offset, inner_offset, lower_offset = pair["offsets"]
        outer_thickness, upper_thickness, inner_thickness, lower_thickness = pair["thicknesses"]
        outer_layer = blanket_from_plasma(
            minor_radius=minor_radius,
            major_radius=major_radius,
            triangularity=triangularity,
            elongation=elongation,
            thickness=[upper_thickness, outer_thickness, lower_thickness],
            offset_from_plasma=[upper_offset, outer_offset, lower_offset],
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
            thickness=[lower_thickness, inner_thickness, upper_thickness],
            offset_from_plasma=[lower_offset, inner_offset, upper_offset],
            start_angle=-90,
            stop_angle=-270,
            rotation_angle=rotation_angle,
            color=(0.5, 0.5, 0.5),
            name=pair["name"],
            allow_overlapping_shape=True,
        )
        layer = outer_layer.union(inner_layer)
        layer.name = pair["name"]
        layers.append(layer)

    return layers


def get_plasma_geometry(radial_build, vertical_build):
    """Returns the major radius, minor radius and elongation of the plasma
    defined by the radial and vertical builds."""
    inner_equatorial_point = sum_up_to_plasma(radial_build)
    outer_equatorial_point = inner_equatorial_point + get_plasma_value(radial_build)
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point
    elongation = (get_plasma_value(vertical_build) / 2) / minor_radius
    return major_radius, minor_radius, elongation


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


def get_poloidal_build_segment_angles(
    poloidal_build, radial_build, vertical_build, triangularity, layer_count=0
):
    """Validates poloidal_build and converts the segment arc lengths into
    poloidal angles for each layer pair."""
    pairs = get_layer_pairs(radial_build, vertical_build, layer_count)
    validate_poloidal_build(poloidal_build, pairs)
    major_radius, minor_radius, elongation = get_plasma_geometry(radial_build, vertical_build)

    all_segment_angles = []
    for index, (pair, segments) in enumerate(zip(pairs, poloidal_build)):
        if segments is None:
            all_segment_angles.append(None)
            continue
        arc_thetas, arc_lengths = poloidal_arc_length_table(
            major_radius=major_radius,
            minor_radius=minor_radius,
            triangularity=triangularity,
            elongation=elongation,
            offset=poloidal_profile(*pair["offsets"]),
        )
        all_segment_angles.append(get_poloidal_segment_angles(segments, arc_thetas, arc_lengths, index))
    return all_segment_angles


def poloidal_arc_lengths(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    elongation: float | None = None,
    triangularity: float = 0.55,
    vertical_build: Sequence[tuple[LayerType, float]] | None = None,
) -> list[float | None]:
    """Returns the poloidal arc length of the inner surface of each layer of a
    tokamak, for use when designing a poloidal_build.

    The values are ordered from the plasma outwards, in the same order as
    poloidal_build, so there is one value per radial_build entry after the
    plasma. Entries that correspond to a LayerType.GAP are None. The arc
    length is measured around the full poloidal loop of the inner surface of
    the layer (the surface closest to the plasma).

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
        list of float or None: the arc length of each layer pair.
    """
    tables = get_arc_length_tables(radial_build, elongation, triangularity, vertical_build)
    return [None if table is None else float(table[1][-1]) for table in tables]


def get_arc_length_tables(radial_build, elongation, triangularity, vertical_build):
    """Returns the (angles, cumulative arc lengths) table of the inner surface
    of each layer pair, or None for GAP pairs, ordered from the plasma
    outwards."""
    if vertical_build is None:
        vertical_build = vertical_build_from_radial_build(radial_build, 2.0 if elongation is None else elongation)
    elif elongation is not None:
        raise ValueError(
            "elongation can not be set when a vertical_build is provided, "
            "the elongation is calculated from the radial_build and vertical_build."
        )

    major_radius, minor_radius, elongation = get_plasma_geometry(radial_build, vertical_build)

    tables = []
    for pair in get_layer_pairs(radial_build, vertical_build):
        if pair["type"] == LayerType.GAP:
            tables.append(None)
            continue
        tables.append(
            poloidal_arc_length_table(
                major_radius=major_radius,
                minor_radius=minor_radius,
                triangularity=triangularity,
                elongation=elongation,
                offset=poloidal_profile(*pair["offsets"]),
            )
        )
    return tables


def aligned_poloidal_build(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    segments: Sequence[tuple[str, float]],
    layers: Sequence[int],
    reference_layer: int | None = None,
    elongation: float | None = None,
    triangularity: float = 0.55,
    vertical_build: Sequence[tuple[LayerType, float]] | None = None,
) -> list[list[tuple[str, float]] | None]:
    """Makes a poloidal_build where several layers share the same segment
    boundaries, so the gaps between segments line up through the layers.

    The segments are defined by arc length on the inner surface of the
    reference layer. Each segment boundary is converted to a poloidal angle,
    and the arc lengths of the other layers are calculated so their segments
    start and stop at the same angles. As the cuts between segments follow
    the normal to the plasma surface, this gives gaps that run straight
    through the layers. The arc length of a gap is therefore slightly larger
    on layers further from the plasma.

    Args:
        radial_build: the radial build of the reactor, as passed to
            tokamak_from_plasma or tokamak.
        segments: list of (name, arc_length) tuples for the reference layer,
            in the same format as a poloidal_build entry. The arc lengths must
            sum to the arc length of the reference layer, which
            paramak.poloidal_arc_lengths returns.
        layers: the poloidal_build indexes (ordered from the plasma outwards,
            one per radial_build entry after the plasma) of the layers to
            segment.
        reference_layer: the poloidal_build index of the layer the segment
            arc lengths are measured on. Defaults to the first of layers.
        elongation: the elongation of the plasma, as passed to
            tokamak_from_plasma. Defaults to 2.0. Must not be set when a
            vertical_build is provided.
        triangularity: the triangularity of the plasma. Defaults to 0.55.
        vertical_build: the vertical build of the reactor, as passed to
            tokamak. Leave as None for tokamak_from_plasma.

    Returns:
        list: a poloidal_build to pass to tokamak_from_plasma or tokamak.
    """
    tables = get_arc_length_tables(radial_build, elongation, triangularity, vertical_build)

    if len(layers) == 0:
        raise ValueError("layers must contain at least one poloidal_build index.")
    if reference_layer is None:
        reference_layer = layers[0]
    for index in [*layers, reference_layer]:
        if not isinstance(index, numbers.Integral) or isinstance(index, bool):
            raise TypeError(f"layers and reference_layer must be integers, not {index!r}.")
        if not 0 <= index < len(tables):
            raise ValueError(
                f"Layer index {index} is out of range, the poloidal_build for this radial_build has "
                f"{len(tables)} entries (indexes 0 to {len(tables) - 1})."
            )
        if tables[index] is None:
            raise ValueError(f"Layer index {index} corresponds to a LayerType.GAP and can not be segmented.")

    # reuses the poloidal_build checks on the reference layer segments
    placeholder_build = [None] * len(tables)
    placeholder_build[reference_layer] = segments
    validate_poloidal_build(placeholder_build, [{"type": LayerType.SOLID}] * len(tables))

    reference_thetas, reference_arc_lengths = tables[reference_layer]
    total_arc_length = reference_arc_lengths[-1]
    requested_arc_length = sum(segment[1] for segment in segments)
    if not math.isclose(requested_arc_length, total_arc_length, rel_tol=POLOIDAL_ARC_LENGTH_RTOL):
        raise ValueError(
            f"The arc lengths in segments sum to {requested_arc_length}, but the arc length of the inner surface "
            f"of reference layer {reference_layer} is {total_arc_length}. Use paramak.poloidal_arc_lengths() to "
            "get the arc length of each layer."
        )
    scale = total_arc_length / requested_arc_length

    # poloidal angle of each segment boundary
    boundaries = np.concatenate([[0.0], np.cumsum([segment[1] * scale for segment in segments])])
    boundary_angles = np.interp(boundaries, reference_arc_lengths, reference_thetas)

    poloidal_build = [None] * len(tables)
    for index in layers:
        thetas, arc_lengths = tables[index]
        layer_boundaries = np.interp(boundary_angles, thetas, arc_lengths)
        poloidal_build[index] = [
            (segment[0], float(length)) for segment, length in zip(segments, np.diff(layer_boundaries))
        ]
    return poloidal_build


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
            otherwise a list of (name, arc_length) tuples. Arc lengths are
            measured along the inner surface of the layer, starting at the
            outboard midplane and proceeding counter clockwise (upwards on
            the outboard side), and must sum to the arc length of that layer
            (within 0.1 percent), which paramak.poloidal_arc_lengths returns.
            Segments named "gap" produce no solid, all other segments produce
            a solid named "<layer name>_<segment name>". Repeated segment
            names within a layer get a "_1", "_2" suffix. To give several
            layers the same segment boundaries, so gaps line up through the
            layers, make the poloidal_build with
            paramak.aligned_poloidal_build. Defaults to None.

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
            otherwise a list of (name, arc_length) tuples. Arc lengths are
            measured along the inner surface of the layer, starting at the
            outboard midplane and proceeding counter clockwise (upwards on
            the outboard side), and must sum to the arc length of that layer
            (within 0.1 percent), which paramak.poloidal_arc_lengths returns.
            Segments named "gap" produce no solid, all other segments produce
            a solid named "<layer name>_<segment name>". Repeated segment
            names within a layer get a "_1", "_2" suffix. To give several
            layers the same segment boundaries, so gaps line up through the
            layers, make the poloidal_build with
            paramak.aligned_poloidal_build. Defaults to None.

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
        # makes a union of the the radial build to use as a base for the intersect shapes
        reactor_compound = inner_radial_build[0]
        for entry in inner_radial_build[1:] + blanket_layers:
            reactor_compound = reactor_compound.union(entry)

        # adds the extra intersect shapes to the assembly
        for entry, name in zip(extra_intersect_shapes, intersect_names):
            reactor_entry_intersection = entry.intersect(reactor_compound)
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
