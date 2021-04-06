
from typing import List, Optional, Tuple

from paramak import SweepMixedShape


class SweepSplineShape(SweepMixedShape):
    """Sweeps a 2D shape created from points connected with spline connections
    along a defined spline path to create a 3D CadQuery solid. Note, some
    variation in the cross-section of the solid may occur.

    Args:
        path_points: A list of XY, YZ or XZ coordinates connected by spline
            connections which define the path along which the 2D shape is
            swept.
        workplane: Workplane in which the 2D shape to be swept is defined.
            Defaults to "XY".
        path_workplane: Workplane in which the spline path is defined. Defaults
            to "XZ".
        stp_filename: Defaults to "SweepSplineShape.stp".
        stl_filename: Defaults to "SweepSplineShape.stl".
        force_cross_section (bool, optional): If True, cross-setion of solid
            is forced to be shape defined by points in workplane at each
            path_point. Defaults to False.
    """

    def __init__(
        self,
        path_points: List[Tuple[float, float]],
        workplane: Optional[str] = "XY",
        path_workplane: Optional[str] = "XZ",
        stp_filename: Optional[str] = "SweepSplineShape.stp",
        stl_filename: Optional[str] = "SweepSplineShape.stl",
        force_cross_section: Optional[bool] = False,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.992, 0.749, 0.435),
        **kwargs
    ):

        super().__init__(
            path_points=path_points,
            workplane=workplane,
            path_workplane=path_workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="spline",
            force_cross_section=force_cross_section,
            color=color,
            **kwargs
        )
