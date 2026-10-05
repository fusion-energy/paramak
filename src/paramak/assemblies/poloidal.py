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


def get_poloidal_segment_angles(segments, arc_positions, arc_lengths, index, arc_length_function):
    """Converts a list of (name, arc_length) segments into a list of
    (name, start, stop) for the solid segments, where start and stop are
    positions along the segmented path (poloidal angles for a tokamak) found
    by interpolating the cumulative arc_lengths at arc_positions.

    Segments start at the outboard midplane and proceed counter clockwise.
    The arc lengths must sum to the total arc length of the loop (within
    POLOIDAL_ARC_LENGTH_RTOL), small differences are scaled out so the last
    segment always closes the loop.
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
        start = float(np.interp(start_position, arc_lengths, arc_positions))
        stop = float(np.interp(position, arc_lengths, arc_positions))
        segment_angles.append((name, start, stop))
    return segment_angles


def intersect_with_each_part(shape, parts):
    """Intersects a shape with each part and returns the non empty pieces
    together in a compound."""
    pieces = []
    for part in parts:
        intersection = shape.intersect(part).val()
        pieces.extend(intersection.Solids())
    return cq.Workplane().add(cq.Compound.makeCompound(pieces))
