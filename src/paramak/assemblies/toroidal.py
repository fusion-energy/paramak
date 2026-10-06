"""Functions shared by the reactors that support toroidal_build."""

from __future__ import annotations

import math
from typing import Sequence

import cadquery as cq

from ..utils import LayerType, get_plasma_index
from .poloidal import (
    DEFAULT_SEGMENT_NAME,
    POLOIDAL_ARC_LENGTH_RTOL,
    check_not_empty,
    make_unique_names,
    validate_segment_build,
)

# sector regions wider than this (in degrees) are split in two, as a region
# made from two half spaces must be less than 180 degrees wide
MAX_SECTOR_REGION_ANGLE = 170.0


def toroidal_reference_radius(radial_build) -> float:
    """Returns the radius of the plasma facing surface (the inner surface of
    the first solid layer after the plasma) at the outboard midplane."""
    plasma_index = get_plasma_index(radial_build)
    radius = sum(item[1] for item in radial_build[: plasma_index + 1])
    for item in radial_build[plasma_index + 1 :]:
        if item[0] == LayerType.SOLID:
            return radius
        radius += item[1]
    raise ValueError("The radial_build has no LayerType.SOLID entries after the plasma to segment.")


def validate_rotation_angle(rotation_angle):
    """Toroidal segments need a rotation angle above 0 and up to 360 degrees."""
    if not 0 < rotation_angle <= 360:
        raise ValueError(
            f"rotation_angle must be above 0 and at most 360 degrees to use toroidal segments, not {rotation_angle}."
        )


def toroidal_arc_length(
    radial_build: Sequence[tuple[LayerType, float] | tuple[LayerType, float, str]],
    rotation_angle: float = 180.0,
) -> float:
    """Returns the toroidal arc length that the segments in a toroidal_build
    must sum to.

    The arc length is measured around the plasma facing surface (the inner
    surface of the first solid layer after the plasma) at the outboard
    midplane, over the rotation_angle of the reactor. This works for all the
    reactor types, as the outboard midplane radius only depends on the
    radial_build.

    Args:
        radial_build: the radial build of the reactor, as passed to the
            reactor function.
        rotation_angle: the rotation angle of the reactor in degrees, as
            passed to the reactor function. Defaults to 180.0.

    Returns:
        float: the toroidal arc length.
    """
    validate_rotation_angle(rotation_angle)
    return toroidal_reference_radius(radial_build) * math.radians(rotation_angle)


def get_toroidal_sectors(segments, reference_radius, rotation_angle, index):
    """Converts a toroidal_build entry into a list of
    (name, (start_angle, start_offset), (stop_angle, stop_offset)) for each
    solid segment.

    The angles are in degrees, measured from the XZ plane towards the Y axis
    (the direction the reactor is revolved in). Each boundary of a segment is
    the plane through the Z axis at that angle, moved by the offset (a
    distance) into the segment. A gap between two segments is a slot of
    constant width centred on the plane at the middle of the gap, so each
    side is moved by half the gap width. A gap at the start or end of the
    rotation is measured from the plane at the start or end of the rotation.
    """
    total_arc_length = reference_radius * math.radians(rotation_angle)
    requested_arc_length = sum(segment[1] for segment in segments)
    if not math.isclose(requested_arc_length, total_arc_length, rel_tol=POLOIDAL_ARC_LENGTH_RTOL):
        raise ValueError(
            f"The arc lengths in toroidal_build entry {index} sum to {requested_arc_length}, but they must sum to "
            f"the toroidal arc length of the plasma facing surface at the outboard midplane, which is "
            f"{total_arc_length}. Use paramak.toroidal_arc_length() to get this value."
        )
    scale = total_arc_length / requested_arc_length

    # (layer_type, start, stop, name) with consecutive gaps merged
    items = []
    position = 0.0
    for segment in segments:
        start = position
        position += segment[1] * scale
        if segment[0] == LayerType.GAP and items and items[-1][0] == LayerType.GAP:
            items[-1] = (LayerType.GAP, items[-1][1], position, None)
            continue
        name = (segment[2] if len(segment) == 3 else DEFAULT_SEGMENT_NAME) if segment[0] == LayerType.SOLID else None
        items.append((segment[0], start, position, name))

    unique_names = make_unique_names([item[3] for item in items], f"toroidal_build entry {index}")
    tolerance = 1e-9 * total_arc_length

    def angle(arc_position):
        return math.degrees(arc_position / reference_radius)

    sectors = []
    for item_index, (layer_type, start, stop, name) in enumerate(items):
        if layer_type != LayerType.SOLID:
            continue
        name = unique_names.pop(0)

        previous_item = items[item_index - 1] if item_index > 0 else None
        if previous_item is None or previous_item[0] == LayerType.SOLID:
            start_boundary = (angle(start), 0.0)
        elif previous_item[1] <= tolerance:
            start_boundary = (0.0, previous_item[2] - previous_item[1])
        else:
            start_boundary = (angle((previous_item[1] + previous_item[2]) / 2), (previous_item[2] - previous_item[1]) / 2)

        next_item = items[item_index + 1] if item_index + 1 < len(items) else None
        if next_item is None or next_item[0] == LayerType.SOLID:
            stop_boundary = (angle(stop), 0.0)
        elif next_item[2] >= total_arc_length - tolerance:
            stop_boundary = (float(rotation_angle), next_item[2] - next_item[1])
        else:
            stop_boundary = (angle((next_item[1] + next_item[2]) / 2), (next_item[2] - next_item[1]) / 2)

        sectors.append((name, start_boundary, stop_boundary))
    return sectors


def get_toroidal_build_sectors(toroidal_build, pairs, radial_build, rotation_angle):
    """Validates toroidal_build and converts each entry into sectors."""
    validate_rotation_angle(rotation_angle)
    validate_segment_build(toroidal_build, pairs, build_name="toroidal_build")
    if all(segments is None for segments in toroidal_build):
        return list(toroidal_build)
    reference_radius = toroidal_reference_radius(radial_build)
    return [
        None if segments is None else get_toroidal_sectors(segments, reference_radius, rotation_angle, index)
        for index, segments in enumerate(toroidal_build)
    ]


def half_space(angle, offset, side, size):
    """A large box covering the points on one side of the plane through the Z
    axis at angle (degrees). side=1 keeps points at least offset in front of
    the plane (towards larger angles), side=-1 keeps points at least offset
    behind it."""
    if side > 0:
        y_start, y_stop = offset, offset + size
    else:
        y_start, y_stop = -offset - size, -offset
    box = (
        cq.Workplane("XY")
        .box(2 * size, y_stop - y_start, 2 * size, centered=(True, False, True))
        .translate((0, y_start, 0))
    )
    return box.rotate((0, 0, 0), (0, 0, 1), angle)


def sector_region(start_boundary, stop_boundary, size):
    """The region between two sector boundaries, each an (angle, offset)."""
    start_angle, stop_angle = start_boundary[0], stop_boundary[0]
    if stop_angle - start_angle > MAX_SECTOR_REGION_ANGLE:
        middle = ((start_angle + stop_angle) / 2, 0.0)
        return sector_region(start_boundary, middle, size).union(sector_region(middle, stop_boundary, size))
    return half_space(*start_boundary, 1, size).intersect(half_space(*stop_boundary, -1, size))


def apply_toroidal_sectors(solids, sectors, rotation_angle, size):
    """Splits each solid into its toroidal sectors, named
    "<solid name>_<sector name>"."""
    full_rotation = (
        len(sectors) == 1
        and sectors[0][1] == (0.0, 0.0)
        and math.isclose(sectors[0][2][0], rotation_angle)
        and sectors[0][2][1] == 0.0
    )
    # the regions only depend on the sectors, so they are made once
    regions = None if full_rotation else [sector_region(start, stop, size) for _, start, stop in sectors]

    result = []
    for solid in solids:
        for sector_index, (name, _, _) in enumerate(sectors):
            if full_rotation:
                # a single sector covering the whole rotation is the full solid
                piece = solid
            else:
                piece = solid.intersect(regions[sector_index])
            piece_name = f"{solid.name}_{name}"
            check_not_empty(piece, f"Toroidal sector {piece_name}")
            piece.name = piece_name
            result.append(piece)
    return result
