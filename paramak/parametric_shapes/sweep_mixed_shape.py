from collections import Iterable

import cadquery as cq

from paramak import Shape


class SweepMixedShape(Shape):
    """Sweeps a 2D shape created from points connected with straight, spline
    or circle connections along a defined spline path to create a 3D CadQuery
    solid.

    Args:
        path_points (list of tuples each containing X (float), Z (float)): A
            list of XY, YZ or XZ coordinates connected by spline connections
            which define the path along which the 2D shape is swept.
        workplane (str, optional): Workplane in which the 2D shape to be swept
            is defined. Defaults to "XY".
        path_workplane (str, optional): Workplane in which the spline path is
            defined. Defaults to "XZ".
        stp_filename (str, optional): Defaults to "SweepMixedShape.stp".
        stl_filename (str, optional): Defaults to "SweepMixedShape.stl".
    """

    def __init__(
        self,
        path_points,
        flag=False,
        workplane="XY",
        path_workplane="XZ",
        stp_filename="SweepMixedShape.stp",
        stl_filename="SweepMixedShape.stl",
        **kwargs
    ):

        super().__init__(
            workplane=workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.path_points = path_points
        self.path_workplane = path_workplane
        self.flag = flag

    @property
    def path_points(self):
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._path_points = value

    @property
    def path_workplane(self):
        return self._path_workplane

    @path_workplane.setter
    def path_workplane(self, value):
        if value[0] != self.workplane[0]:
            raise ValueError(
                "workplane and path_workplane must start with the same letter"
            )
        elif value == self.workplane:
            raise ValueError(
                "workplane and path_workplane must be different"
            )
        else:
            self._path_workplane = value

    def create_solid(self):
        """Creates a swept 3D solid from a 2D shape with mixed connections.

        Returns:
            A CadQuery solid: A 3D solid volume
        """

        solid = super().create_solid()
        path = cq.Workplane(self.path_workplane).spline(self.path_points)
        solid = solid.sweep(path, multisection=True)

        solid = self.rotate_solid(solid)
        solid = self.perform_boolean_operations(solid)
        self.solid = solid
        return solid
