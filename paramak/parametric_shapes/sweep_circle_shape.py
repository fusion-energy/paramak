from collections import Iterable

import cadquery as cq

from paramak import Shape


class SweepCircleShape(Shape):
    """Sweeps a 2D circle of a defined radius along a defined spline path to create a
    3D CadQuery solid.

    Args:
        radius (float): Radius of 2D circle to be swept.
        path_points (list of tuples each containing X (float), Z (float)): A list of XY,
            YZ or XZ coordinates connected by spline connections which define the path
            along which the 2D shape is swept.
        workplane (str, optional): Workplane in which the circle to be swept is defined.
            Defaults to "XY".
        path_workplane (str, optional): Workplane in which the spline path is defined.
            Defaults to "XZ".
        stp_filename (str, optional): Defaults to "SweepCircleShape.stp".
        stl_filename (str, optional): Defaults to "SweepCircleShape.stl".
    """

    def __init__(
        self,
        radius,
        path_points,
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

        self.radius = radius
        self.path_points = path_points
        self.path_workplane = path_workplane

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def path_points(self):
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._points = value
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
        """Creates a swept 3D solid from a 2D circle.

        Returns:
            A CadQuery solid: A 3D solid volume
        """

        path = cq.Workplane(self.path_workplane).spline(self.path_points)
        distance = float(self.path_points[-1][1] - self.path_points[0][1])

        if self.workplane in ["XZ", "YX", "ZY"]:
            distance *= -1

        solid = (
            cq.Workplane(self.workplane)
            .workplane(offset=self.path_points[0][1])
            .moveTo(self.path_points[0][0], 0)
            .workplane()
            .circle(self.radius)
            .moveTo(-self.path_points[0][0], 0)
            .workplane(offset=distance)
            .moveTo(self.path_points[-1][0], 0)
            .workplane()
            .circle(self.radius)
            .sweep(path, multisection=True)
        )

        solid = self.rotate_solid(solid)
        self.perform_boolean_operations(solid)

        return solid
