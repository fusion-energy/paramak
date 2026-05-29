import typing

import cadquery as cq

from ..utils import create_wire_workplane_from_points


def revolved_shape(
    points: typing.Sequence[typing.Tuple[float, float, str]],
    rotation_angle: float = 360.0,
    name: str = "revolved_shape",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.5,
        0.5,
        0.5,
    ),
    plane: str = "XZ",
    origin: typing.Tuple[float, float, float] = (0, 0, 0),
    obj=None,
) -> cq.Workplane:
    """Creates a solid by revolving an arbitrary closed 2D profile around the axis.

    The profile is described by a list of points where each point is a
    ``(R, Z, connection)`` tuple. ``connection`` is one of ``"straight"``,
    ``"spline"`` or ``"circle"`` and describes how that point joins to the next
    one. This is the same profile description used internally by paramak's
    blanket and dome components, so splines and arcs produce smooth curved
    profiles rather than blocky polylines.

    The profile is closed automatically, so the first point should not be
    repeated at the end of the list. This is convenient for building custom
    shapes to pass to the ``extra_intersect_shapes`` or ``extra_cut_shapes``
    arguments of the reactor assemblies, for example a curved divertor.

    Args:
        points: the profile points as ``(R, Z, connection)`` tuples, ordered
            around the outline. Do not repeat the first point; the profile is
            closed automatically.
        rotation_angle: the angle in degrees to revolve the profile around the
            axis. Defaults to 360.
        name: the name assigned to the resulting solid.
        color: the RGB(A) color assigned to the resulting solid.
        plane: the plane to build the profile on, e.g. "XZ".
        origin: the origin of the workplane.
        obj: an optional existing CadQuery object to build upon.

    Returns:
        A CadQuery Workplane containing the revolved solid.
    """

    if len(points) < 3:
        msg = f"revolved_shape requires at least 3 points to form a profile, got {len(points)}."
        raise ValueError(msg)

    # close the profile by repeating the first point at the end
    closed_points = list(points) + [points[0]]

    wire = create_wire_workplane_from_points(points=closed_points, plane=plane, origin=origin, obj=obj)

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = color
    return solid
