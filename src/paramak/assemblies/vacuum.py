"""The vacuum volume that fills the gap between the plasma and the first wall.

DAGMC transport is quicker when particles stay out of the implicit complement,
so the gap is given its own volume. The vacuum is made by cutting the plasma,
the first wall and anything else that reaches into the gap (such as a divertor
added with extra_cut_shapes) out of an envelope that reaches into the first
wall. It then shares the faces of its neighbours, as DAGMC needs, and does not
overlap them.
"""

from __future__ import annotations

import math

import cadquery as cq

from ..utils import resolve_assembly_color, rotate_about_z

VACUUM_NAME = "vacuum"


def revolved_profile(curves, rotation_angle: float, rotation_start_angle: float = 0.0) -> cq.Workplane:
    """Revolves a closed profile around the Z axis.

    Args:
        curves: a list of curves, each a list of (R, Z) points. Curves with
            two points are straight lines, longer curves are splines through
            the points. Each curve should start where the previous one ends
            and the last should end where the first starts.

    The envelope only needs a few faces, which keeps the booleans with the
    rest of the reactor quick.
    """
    edges = []
    for curve in curves:
        points = [cq.Vector(float(r), 0.0, float(z)) for r, z in curve]
        edges.append(cq.Edge.makeLine(*points) if len(points) == 2 else cq.Edge.makeSpline(points))
    face = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    solid = cq.Solid.revolve(face, rotation_angle, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    return rotate_about_z(cq.Workplane("XZ").add(solid), rotation_start_angle)


def _as_shape(shape) -> cq.Shape:
    if isinstance(shape, cq.Workplane):
        solids = [value for value in shape.vals() if isinstance(value, cq.Shape)]
        return solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids)
    return shape


def _overlap(box_a, box_b) -> bool:
    return all(
        getattr(box_a, f"{axis}min") <= getattr(box_b, f"{axis}max")
        and getattr(box_b, f"{axis}min") <= getattr(box_a, f"{axis}max")
        for axis in "xyz"
    )


def _box_envelope(shapes, rotation_angle: float) -> cq.Workplane:
    """A revolved rectangle, from the Z axis outwards, around the shapes."""
    box = cq.Compound.makeCompound(shapes).BoundingBox()
    margin = 0.05 * box.DiagonalLength
    radius = math.hypot(max(abs(box.xmin), abs(box.xmax)), max(abs(box.ymin), abs(box.ymax))) + margin
    bottom, top = box.zmin - margin, box.zmax + margin
    corners = [(0.0, bottom), (radius, bottom), (radius, top), (0.0, top)]
    return revolved_profile([[corners[i], corners[(i + 1) % 4]] for i in range(4)], rotation_angle)


def add_vacuum(
    assembly,
    cutters,
    envelope: cq.Workplane | None = None,
    colors: dict | None = None,
    rotation_angle: float = 360.0,
    tolerance: float = 1e-3,
):
    """Adds a part called "vacuum" that fills the space around the plasma.

    The plasma and the cutters are cut from the envelope one at a time and the
    solids left touching the plasma are kept, so pockets cut off from the
    plasma (for example by a divertor) are left to the implicit complement.

    Args:
        assembly: the assembly, it must contain a part named "plasma".
        cutters: the shapes to cut from the envelope, this must include
            everything that the envelope reaches into other than the plasma.
        envelope: a solid around the plasma. Defaults to a revolved
            rectangle around the cutters, in which case the cutters must
            enclose the plasma.
        colors: user colors keyed by part name.
        rotation_angle: the angle the default envelope is revolved by.
        tolerance: the distance (cm) from the plasma within which a solid is
            taken as touching it.
    """
    plasma = next(shape.moved(loc) for shape, name, loc, _color in assembly if name.split("/")[-1] == "plasma")
    cutters = [plasma, *(_as_shape(cutter) for cutter in cutters)]
    vacuum = (envelope if envelope is not None else _box_envelope(cutters, rotation_angle)).val()
    # one shape at a time, cutting them all at once also intersects the
    # cutters with each other, which is much slower
    for cutter in cutters:
        if _overlap(vacuum.BoundingBox(), cutter.BoundingBox()):
            vacuum = vacuum.cut(cutter)
    solids = [solid for solid in vacuum.Solids() if solid.distance(plasma) < tolerance]
    if not solids:
        raise RuntimeError("Making the vacuum around the plasma left no solid next to the plasma.")
    shape = solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids)
    color = resolve_assembly_color(VACUUM_NAME, None, colors)
    assembly.add(cq.Workplane("XZ").add(shape), name=VACUUM_NAME, color=cq.Color(*color))
    return assembly
