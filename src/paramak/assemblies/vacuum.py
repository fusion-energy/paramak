"""The vacuum volume that fills the space between the plasma and the parts
around it.

DAGMC transport is quicker when particles stay out of the implicit
complement, so the space around the plasma is given its own volume. The
vacuum is made as part of the reactor's 2D cross section (see
cross_section.py): it is the region the parts around the plasma close off,
less the plasma. It is revolved with the other parts, so it shares its faces
with the plasma and with its neighbours.
"""

from __future__ import annotations

import cadquery as cq

from .cross_section import rectangle_face

VACUUM_NAME = "vacuum"


def vacuum_profile(plasma_faces, enclosing_faces, tolerance: float = 1e-6) -> list[cq.Face]:
    """Returns the 2D profile of the vacuum around the plasma.

    The profiles of the plasma and the parts that enclose it are cut from a
    rectangle around them, and the pieces left touching the plasma are kept.
    A pocket that the parts close off from the plasma (for example under a
    divertor) is not part of the vacuum.

    Args:
        plasma_faces: the faces of the plasma profile.
        enclosing_faces: the faces of the profiles of the parts that enclose
            the plasma, for example the first wall.
        tolerance: the distance (cm) within which a piece is taken as touching
            the plasma or the edge of the rectangle.

    Raises:
        ValueError: if the parts do not enclose the plasma.
    """
    # fused into one shape, so parts that only touch along an edge (such as
    # a first wall meeting a centre column) close off the space between them
    faces = [*enclosing_faces, *plasma_faces]
    shapes = faces[0].fuse(*faces[1:]) if len(faces) > 1 else faces[0]
    box = shapes.BoundingBox()
    margin = 0.05 * box.DiagonalLength
    region = rectangle_face(max(box.xmin - margin, 0.0), box.xmax + margin, box.zmin - margin, box.zmax + margin)
    outline = region.outerWire()
    plasma = cq.Compound.makeCompound(plasma_faces)

    pieces = [piece for piece in region.cut(shapes).Faces() if piece.distance(plasma) < tolerance]
    if not pieces or any(piece.distance(outline) < tolerance for piece in pieces):
        raise ValueError("The parts around the plasma do not enclose it, so there is no vacuum to fill.")
    return pieces


def cut_vacuum(solids, cutters, plasma, tolerance: float = 1e-3) -> list[cq.Solid]:
    """Cuts shapes from the revolved vacuum and keeps the solids that still
    touch the plasma.

    Shapes such as extra_cut_shapes are added whole and can reach into the
    vacuum, so they are cut from it. A pocket they cut off from the plasma is
    left to the implicit complement.

    Args:
        solids: the solids of the revolved vacuum.
        cutters: the shapes to cut from the vacuum, Workplanes or Shapes.
        plasma: the plasma, a Workplane or Shape.
        tolerance: the distance (cm) from the plasma within which a solid is
            taken as touching it.
    """

    def shape(item):
        return item.val() if isinstance(item, cq.Workplane) else item

    if not cutters:
        return list(solids)
    plasma = shape(plasma)
    vacuum = solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids)
    # one shape at a time, cutting them all at once also intersects the
    # cutters with each other, which is much slower
    for cutter in cutters:
        vacuum = vacuum.cut(shape(cutter))
    kept = [solid for solid in vacuum.Solids() if solid.distance(plasma) < tolerance]
    if not kept:
        raise RuntimeError("Cutting the extra shapes from the vacuum left no solid next to the plasma.")
    return kept
