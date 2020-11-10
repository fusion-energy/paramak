from collections import Iterable

import cadquery as cq

from paramak import SweepMixedShape


class SweepSplineShape(SweepMixedShape):
    """Sweeps a 2D shape created from points connected with spline connections
    along a defined spline path to create a 3D CadQuery solid.

    Args:
        path_points (list of tuples each containing X (float), Z (float)): A
            list of XY, YZ or XZ coordinates connected by spline connections
            which define the path along which the 2D shape is swept.
        workplane (str, optional): Workplane in which the 2D shape to be swept
            is defined. Defaults to "XY".
        path_workplane (str, optional): Workplane in which the spline path is
            defined. Defaults to "XZ".
        stp_filename (str, optional): Defaults to "SweepSplineShape.stp".
        stl_filename (str, optional): Defaults to "SweepSplineShape.stl".
    """

    def __init__(
        self,
        path_points,
        force_area=False,
        workplane="XY",
        path_workplane="XZ",
        stp_filename="SweepSplineShape.stp",
        stl_filename="SweepSplineShape.stl",
        **kwargs
    ):

        super().__init__(
            path_points=path_points,
            workplane=workplane,
            path_workplane=path_workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="spline",
            force_area=force_area,
            **kwargs
        )
