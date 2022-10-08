from typing import List, Optional, Tuple

from paramak import SweepMixedShape


class SweepStraightShape(SweepMixedShape):
    """Sweeps a 2D shape created from points connected with straight lines
    along a defined spline path to create a 3D CadQuery solid. Note, some
    variation in the cross-section of the solid may occur.

    Args:
        path_points: A list of XY, YZ or XZ coordinates connected by spline
            connections which define the path along which the 2D shape is swept
        workplane: Workplane in which the 2D shape to be swept is defined.
            Defaults to "XY".
        path_workplane: Workplane in which the spline path is defined. Defaults
            to "XZ".
        force_cross_section: If True, cross-section of solid is forced to be
            shape defined by points in workplane at each path_point. Defaults
            to False.
        color: the color to use when exporting the shape to CAD formats that
            support color. A tuple of three floats each ranging between 0
            and 1.
        name: the name of the shape, used to name files when exporting and
            as a legend in plots.
        translate: distance to translate / move the shape by. Specified as
            a vector of (X,Y,Z) directions.
    """

    def __init__(
        self,
        path_points: List[Tuple[float, float]],
        workplane: str = "XY",
        path_workplane: str = "XZ",
        force_cross_section: bool = False,
        color: Tuple[float, float, float, Optional[float]] = (
            0.698,
            0.8745,
            0.541,
        ),
        name: str = "sweepstraightshape",
        **kwargs
    ):

        super().__init__(
            path_points=path_points,
            workplane=workplane,
            path_workplane=path_workplane,
            connection_type="straight",
            force_cross_section=force_cross_section,
            color=color,
            name=name,
            **kwargs
        )
