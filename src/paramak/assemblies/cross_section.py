"""Builds the axisymmetric parts of a reactor from one 2D cross section.

Each part is described by its profile, one or more faces in the XZ plane (R
along X, Z up). The profiles of all the parts are split against each other in
one go, so where two parts touch they share the same edges. The whole cross
section is then revolved around the Z axis in one operation, which turns each
shared edge into a face shared by the solids on either side of it.

Neighbouring parts therefore share their faces exactly, rather than having
separately made faces that only coincide. DAGMC needs shared faces, and when
they are only coincident they have to be found and matched by imprinting,
which does not work for every surface (for example a face made separately
from the plasma surface leaves a zero volume solid when imprinted).
"""

from __future__ import annotations

import math

import cadquery as cq
from OCP.BOPAlgo import BOPAlgo_Builder
from OCP.BRep import BRep_Builder
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt
from OCP.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosedEdges
from OCP.TopoDS import TopoDS_Compound, TopoDS_Iterator

from ..utils import create_wire_workplane_from_points


def profile_face(points) -> cq.Face:
    """Returns a face in the XZ plane from a closed profile of
    (R, Z, connection) points, with the first point repeated at the end, as
    used by create_wire_workplane_from_points. Every face is given the same
    orientation, so the profiles split against each other consistently."""
    wire = create_wire_workplane_from_points(points=points, plane="XZ").val()
    face = cq.Face.makeFromWires(wire)
    if face.normalAt().y < 0:
        face = cq.Face(face.wrapped.Reversed())
    return face


def rectangle_face(r_min: float, r_max: float, z_min: float, z_max: float) -> cq.Face:
    """Returns a rectangular profile in the XZ plane."""
    corners = [(r_min, z_max), (r_max, z_max), (r_max, z_min), (r_min, z_min)]
    return profile_face([(r, z, "straight") for r, z in corners + corners[:1]])


def _compound(shapes) -> TopoDS_Compound:
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    return compound


def _children(shape) -> list:
    iterator = TopoDS_Iterator(shape)
    children = []
    while iterator.More():
        children.append(iterator.Value())
        iterator.Next()
    return children


def _area(faces) -> float:
    return sum(face.Area() for face in faces)


def _split(names, faces):
    """Splits the faces against each other with a general fuse.

    Returns the pieces in order with the name of the part each belongs to,
    and the pairs of parts (earlier, later) whose profiles overlap. A piece
    in an overlap is given to the part listed first."""
    if len(faces) == 1:
        return [faces[0].wrapped], [names[0]], set()
    builder = BOPAlgo_Builder()
    for face in faces:
        builder.AddArgument(face.wrapped)
    builder.Perform()
    if builder.HasErrors():
        raise RuntimeError("Splitting the 2D profiles of the reactor parts against each other failed.")
    pieces, owners, overlaps = [], [], set()
    for name, face in zip(names, faces):
        if builder.IsDeleted(face.wrapped):
            continue
        modified = builder.Modified(face.wrapped)
        for piece in list(modified) if modified.Size() else [face.wrapped]:
            earlier = next((i for i, other in enumerate(pieces) if piece.IsSame(other)), None)
            if earlier is None:
                pieces.append(piece)
                owners.append(name)
            elif owners[earlier] != name:
                overlaps.add((owners[earlier], name))
    return pieces, owners, overlaps


def revolve_cross_section(
    parts: dict[str, list[cq.Face]], rotation_angle: float, rotation_start_angle: float = 0.0
) -> dict[str, list[cq.Solid]]:
    """Revolves the profiles of the parts together, so neighbouring parts
    share their faces.

    Args:
        parts: the faces of the profile of each part in the XZ plane, keyed
            by part name. Where two profiles overlap, the part listed first
            keeps the overlap and it is cut from the later part.
        rotation_angle: the angle in degrees to revolve the profiles by,
            around the Z axis.
        rotation_start_angle: the angle in degrees the revolution starts
            from, measured around the Z axis from the XZ plane.

    Returns:
        the solids of each part, keyed by part name.
    """
    parts = {name: list(faces) for name, faces in parts.items()}

    def flatten():
        names = [name for name, faces in parts.items() for _ in faces]
        faces = [face for faces in parts.values() for face in faces]
        return names, faces

    pieces, owners, overlaps = _split(*flatten())
    if overlaps:
        # the profiles were made separately and can overlap slightly, for
        # example where a curved layer meets a straight centre column, so the
        # overlap is cut from the later part and the profiles split again
        for earlier, later in overlaps:
            cutter = cq.Compound.makeCompound(parts[earlier])
            remaining = cq.Compound.makeCompound(parts[later]).cut(cutter).Faces()
            if _area(remaining) <= 0:
                raise ValueError(f"The profile of {later} lies inside the profile of {earlier}.")
            parts[later] = remaining
        pieces, owners, overlaps = _split(*flatten())
        if overlaps:
            raise RuntimeError(f"The 2D profiles of these parts still overlap: {sorted(overlaps)}")

    compound = _compound(pieces)
    if rotation_angle >= 360:
        # a closed edge, such as the plasma outline, revolved through 360
        # degrees gives a surface that is periodic in both directions, which
        # can not be meshed, so closed edges are split in two. This is done on
        # the whole compound so the edges stay shared.
        divider = ShapeUpgrade_ShapeDivideClosedEdges(compound)
        divider.SetNbSplitPoints(1)
        divider.Perform()
        compound = divider.Result()
    revolved_faces = _children(compound)
    for piece, face in zip(pieces, revolved_faces):
        # the pieces keep their order, which is how the solids are matched
        # to their parts, this checks it
        before, after = cq.Shape.cast(piece).BoundingBox(), cq.Shape.cast(face).BoundingBox()
        if any(abs(getattr(before, a) - getattr(after, a)) > 1e-6 for a in ("xmin", "xmax", "zmin", "zmax")):
            raise RuntimeError("The 2D profiles changed order while splitting closed edges.")

    axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    revolved = BRepPrimAPI_MakeRevol(compound, axis, math.radians(min(rotation_angle, 360.0)), False).Shape()
    solids = _children(revolved)
    if len(solids) != len(pieces):
        raise RuntimeError(f"Revolving {len(pieces)} profiles gave {len(solids)} solids.")

    # a location keeps the shared faces shared, rotating each solid would copy them
    rotation = cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rotation_start_angle)
    result = {name: [] for name in parts}
    for name, solid in zip(owners, solids):
        result[name].append(cq.Solid(solid).moved(rotation))
    return result


def named_part(solids, name, layer_name=None):
    """Returns a Workplane holding the solids of a part, with the name and
    layer_name attributes that paramak sets on the parts of a reactor."""
    part = cq.Workplane("XY").add(solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids))
    part.name = name
    if layer_name is not None:
        part.layer_name = layer_name
    return part


def moved_part(part, location):
    """Moves a part by a location, keeping its name and layer_name. Moving
    keeps the faces it shares with its neighbours, rotating would copy them."""
    moved = cq.Workplane("XY").add([shape.moved(location) for shape in part.vals()])
    for attribute in ("name", "layer_name"):
        if hasattr(part, attribute):
            setattr(moved, attribute, getattr(part, attribute))
    return moved
