from __future__ import annotations

from collections.abc import Sequence
import math

import cadquery as cq
import numpy as np

from .blanket_from_plasma import blanket_from_plasma, offset_curve_coordinates


def divertor(
    poloidal_start_angle: float,
    poloidal_extent_angle: float,
    divertor_layer_names: Sequence[str],
    divertor_layer_thicknesses: Sequence[float],
    *,
    major_radius: float,
    minor_radius: float,
    triangularity: float,
    elongation: float,
    plasma_facing_offset,
    rotation_angle: float,
) -> list[cq.Workplane]:
    """Builds the layered solids for a poloidal divertor.

    The new divertor starts at the model's plasma-facing surface and extends
    outward. The returned solids define both the replacement layers and the
    volume removed from existing reactor layers.
    """
    if not isinstance(poloidal_start_angle, (int, float)):
        raise TypeError("poloidal_start_angle must be a number")
    if not isinstance(poloidal_extent_angle, (int, float)) or not 0 < poloidal_extent_angle <= 360:
        raise ValueError("poloidal_extent_angle must be greater than 0 and at most 360 degrees")
    if len(divertor_layer_names) == 0 or len(divertor_layer_names) != len(divertor_layer_thicknesses):
        raise ValueError("divertor_layer_names and divertor_layer_thicknesses must have the same non-zero length")
    if any(not isinstance(name, str) or not name for name in divertor_layer_names):
        raise ValueError("each divertor layer name must be a non-empty string")
    if any(not isinstance(value, (int, float)) or value <= 0 for value in divertor_layer_thicknesses):
        raise ValueError("each divertor layer thickness must be a positive number")

    start = float(poloidal_start_angle)
    stop = start + float(poloidal_extent_angle)
    common = dict(
        major_radius=major_radius,
        minor_radius=minor_radius,
        triangularity=triangularity,
        elongation=elongation,
        rotation_angle=rotation_angle,
        allow_overlapping_shape=True,
    )

    if poloidal_extent_angle == 360:
        cutting_region = None
    else:
        margin = 0.05 * minor_radius
        thetas = np.linspace(start, stop, max(10, math.ceil(400 * poloidal_extent_angle / 360)))
        inner_r, inner_z = offset_curve_coordinates(
            major_radius,
            minor_radius,
            triangularity,
            elongation,
            0.0,
            thetas,
            np.asarray([plasma_facing_offset(theta) if callable(plasma_facing_offset) else plasma_facing_offset for theta in thetas])
            - margin,
        )
        outer_thetas = thetas[::-1]
        outer_r, outer_z = offset_curve_coordinates(
            major_radius,
            minor_radius,
            triangularity,
            elongation,
            0.0,
            outer_thetas,
            np.asarray(
                [
                    (plasma_facing_offset(theta) if callable(plasma_facing_offset) else plasma_facing_offset)
                    + sum(divertor_layer_thicknesses)
                    + margin
                    for theta in outer_thetas
                ]
            ),
        )
        points = list(zip(np.maximum(np.concatenate([inner_r, outer_r]), 0.0), np.concatenate([inner_z, outer_z])))
        cutting_region = cq.Workplane("XZ").polyline(points).close().revolve(360)

    layers = []
    cumulative_thickness = 0.0
    for name, thickness in zip(divertor_layer_names, divertor_layer_thicknesses):
        if callable(plasma_facing_offset):
            layer_offset = lambda theta, base=plasma_facing_offset, extra=cumulative_thickness: base(theta) + extra
        else:
            layer_offset = plasma_facing_offset + cumulative_thickness
        outer_half = blanket_from_plasma(
            thickness=thickness,
            offset_from_plasma=layer_offset,
            start_angle=90,
            stop_angle=-90,
            name=name,
            **common,
        )
        inner_half = blanket_from_plasma(
            thickness=thickness,
            offset_from_plasma=layer_offset,
            start_angle=-90,
            stop_angle=-270,
            name=name,
            **common,
        )
        layer = outer_half.union(inner_half)
        if cutting_region is not None:
            layer = layer.intersect(cutting_region)
        layer.name = name
        layer.color = (0.333, 0.0, 0.0)
        if not layer.val().isValid():
            raise ValueError(f"divertor: generated layer {name!r} is not a valid closed CAD shape")
        layers.append(layer)
        cumulative_thickness += thickness

    return layers
