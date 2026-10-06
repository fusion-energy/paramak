"""Functions shared by the reactors that support poloidal_build."""

from __future__ import annotations

import math
import numbers
from collections import Counter

import cadquery as cq
import numpy as np

from ..utils import LayerType

# relative tolerance allowed between the sum of the arc lengths in a
# poloidal_build entry and the actual arc length of that layer
POLOIDAL_ARC_LENGTH_RTOL = 1e-3


# name given to solid segments that are not named in the poloidal_build
DEFAULT_SEGMENT_NAME = "segment"


def validate_poloidal_build(poloidal_build, pairs):
    """Checks the structure of poloidal_build against the layer pairs.

    Each segment uses the same format as a radial_build entry: a
    (LayerType.SOLID, arc_length) or (LayerType.SOLID, arc_length, name) tuple
    for a solid segment, or a (LayerType.GAP, arc_length) tuple for a gap.
    """
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
                f"poloidal_build entry {index} must be None or a non empty list of segments such as "
                f"(paramak.LayerType.SOLID, arc_length) or (paramak.LayerType.GAP, arc_length), not {segments}."
            )
        for segment in segments:
            if (
                not isinstance(segment, (list, tuple))
                or len(segment) not in (2, 3)
                or not isinstance(segment[0], LayerType)
                or not isinstance(segment[1], numbers.Real)
                or isinstance(segment[1], bool)
                or (len(segment) == 3 and not isinstance(segment[2], str))
            ):
                raise TypeError(
                    f"Each segment in poloidal_build entry {index} must be a (paramak.LayerType, arc_length) "
                    f"or (paramak.LayerType, arc_length, name) tuple with a numeric arc_length and a string "
                    f"name, not {segment}."
                )
            layer_type, arc_length = segment[0], segment[1]
            if layer_type == LayerType.GAP:
                if len(segment) == 3:
                    raise ValueError(
                        f"LayerType.GAP segments in poloidal_build entry {index} produce no solid and can not "
                        f"be named, not {segment}."
                    )
                if arc_length < 0:
                    raise ValueError(
                        f"LayerType.GAP segments in poloidal_build entry {index} must have an arc_length of 0 "
                        f"or more, not {arc_length}."
                    )
            elif layer_type == LayerType.SOLID:
                if arc_length <= 0:
                    raise ValueError(
                        f"LayerType.SOLID segments in poloidal_build entry {index} must have a positive "
                        f"arc_length, not {arc_length}."
                    )
            else:
                raise ValueError(
                    f"Segments in poloidal_build entry {index} must be LayerType.SOLID or LayerType.GAP, "
                    f"not {layer_type}."
                )
        if all(segment[0] == LayerType.GAP for segment in segments):
            raise ValueError(f"poloidal_build entry {index} must contain at least one LayerType.SOLID segment.")


def get_poloidal_segment_angles(segments, arc_positions, arc_lengths, index, arc_length_function):
    """Converts a list of segments into a list of (name, start, stop) for the
    solid segments, where start and stop are positions along the segmented
    path (poloidal angles for a tokamak) found by interpolating the
    cumulative arc_lengths at arc_positions.

    The arc lengths must sum to the total arc length of the path (within
    POLOIDAL_ARC_LENGTH_RTOL), small differences are scaled out so the last
    segment always reaches the end of the path. Solid segments without a name
    are called DEFAULT_SEGMENT_NAME, and repeated names get a "_1", "_2"
    suffix.
    """
    total_arc_length = arc_lengths[-1]
    requested_arc_length = sum(segment[1] for segment in segments)
    if not math.isclose(requested_arc_length, total_arc_length, rel_tol=POLOIDAL_ARC_LENGTH_RTOL):
        raise ValueError(
            f"The arc lengths in poloidal_build entry {index} sum to {requested_arc_length}, but they must sum to "
            f"the poloidal arc length of the plasma facing surface, which is {total_arc_length}. Use "
            f"paramak.{arc_length_function}() to get this value."
        )
    scale = total_arc_length / requested_arc_length

    names = [
        (segment[2] if len(segment) == 3 else DEFAULT_SEGMENT_NAME) if segment[0] == LayerType.SOLID else None
        for segment in segments
    ]
    unique_names = make_unique_names(names, f"poloidal_build entry {index}")

    segment_angles = []
    position = 0.0
    for segment, name in zip(segments, names):
        start_position = position
        position += segment[1] * scale
        if name is None:
            continue
        name = unique_names.pop(0)
        start = float(np.interp(start_position, arc_lengths, arc_positions))
        stop = float(np.interp(position, arc_lengths, arc_positions))
        segment_angles.append((name, start, stop))
    return segment_angles


def make_unique_names(names, description):
    """Adds a "_1", "_2" suffix to names that are repeated, ignoring None
    entries (gaps), and returns the names of the solid segments in order.
    Raises an error if a suffixed name clashes with a name given directly."""
    counts = Counter(name for name in names if name is not None)
    seen = Counter()
    unique_names = []
    for name in names:
        if name is None:
            continue
        if counts[name] > 1:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        unique_names.append(name)
    duplicates = sorted(name for name, count in Counter(unique_names).items() if count > 1)
    if duplicates:
        raise ValueError(
            f"The segment names in {description} give the same name more than once ({', '.join(duplicates)}) "
            f"after repeated names get a _1, _2 suffix. Use names that do not end in such a suffix."
        )
    return unique_names


def check_not_empty(solid, description):
    """Raises an error if a segment has no volume, for example because its
    gaps are wider than the segment where it is cut."""
    if not solid.val().Solids():
        raise ValueError(
            f"{description} is empty, the gaps around it remove all of it. Use smaller gaps or fewer segments."
        )


def resolve_vertical_build(radial_build, elongation, vertical_build, vertical_build_from_radial_build):
    """Returns the vertical build used by the arc length helpers, made from
    the radial build and elongation when no vertical build is given."""
    if vertical_build is None:
        return vertical_build_from_radial_build(radial_build, 2.0 if elongation is None else elongation)
    if elongation is not None:
        raise ValueError(
            "elongation can not be set when a vertical_build is provided, "
            "the elongation is calculated from the radial_build and vertical_build."
        )
    return vertical_build


def bounding_boxes_overlap(first, second):
    """Whether two cadquery bounding boxes overlap."""
    return (
        first.xmin <= second.xmax
        and second.xmin <= first.xmax
        and first.ymin <= second.ymax
        and second.ymin <= first.ymax
        and first.zmin <= second.zmax
        and second.zmin <= first.zmax
    )


def intersect_with_each_part(shape, parts):
    """Intersects a shape with each part and returns the non empty pieces
    together in a compound. Parts whose bounding box does not overlap the
    shape are skipped."""
    shape_box = cq.Compound.makeCompound(shape.vals()).BoundingBox()
    pieces = []
    for part in parts:
        if not bounding_boxes_overlap(shape_box, cq.Compound.makeCompound(part.vals()).BoundingBox()):
            continue
        intersection = shape.intersect(part).val()
        pieces.extend(intersection.Solids())
    return cq.Workplane().add(cq.Compound.makeCompound(pieces))
