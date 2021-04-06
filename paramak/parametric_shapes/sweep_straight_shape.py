
from typing import Optional, List, Tuple

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
        stp_filename: Defaults to "SweepStraightShape.stp".
        stl_filename: Defaults to "SweepStraightShape.stl".
        force_cross_section: If True, cross-section of solid is forced to be
            shape defined by points in workplane at each path_point. Defaults
            to False.
    """

    def __init__(
        self,
        path_points: List[Tuple[float, float]],
        workplane: Optional[str] = "XY",
        path_workplane: Optional[str] = "XZ",
        stp_filename: Optional[str] = "SweepStraightShape.stp",
        stl_filename: Optional[str] = "SweepStraightShape.stl",
        force_cross_section: Optional[bool] = False,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.698, 0.8745, 0.541),
        **kwargs
    ):

        super().__init__(
            path_points=path_points,
            workplane=workplane,
            path_workplane=path_workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="straight",
            force_cross_section=force_cross_section,
            color=color,
            **kwargs
        )
