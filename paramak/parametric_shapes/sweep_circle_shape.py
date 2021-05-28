
from typing import Optional, List, Tuple

from cadquery import Workplane
from paramak import Shape


class SweepCircleShape(Shape):
    """Sweeps a 2D circle of a defined radius along a defined spline path to
    create a 3D CadQuery solid. Note, some variation in the cross-section of
    the solid may occur.

    Args:
        radius: Radius of 2D circle to be swept.
        path_points: A list of XY, YZ or XZ coordinates connected by spline
            connections which define the path along which the 2D shape is swept
        workplane: Workplane in which the circle to be swept
            is defined. Defaults to "XY".
        path_workplane: Workplane in which the spline path is
            defined. Defaults to "XZ".
        stp_filename: Defaults to "SweepCircleShape.stp".
        stl_filename: Defaults to "SweepCircleShape.stl".
        force_cross_section: If True, cross-section of solid is forced to be
            shape defined by points in workplane at each path_point. Defaults
            to False.
    """

    def __init__(
        self,
        radius: float,
        path_points: List[Tuple[float, float]],
        workplane: Optional[str] = "XY",
        path_workplane: Optional[str] = "XZ",
        stp_filename: Optional[str] = "SweepCircleShape.stp",
        stl_filename: Optional[str] = "SweepCircleShape.stl",
        force_cross_section: Optional[bool] = False,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.651, 0.808, 0.89),
        **kwargs
    ):

        super().__init__(
            workplane=workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.radius = radius
        self.path_points = path_points
        self.path_workplane = path_workplane
        self.force_cross_section = force_cross_section

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

        path = Workplane(self.path_workplane).spline(self.path_points)

        factor = 1
        if self.workplane in ["XZ", "YX", "ZY"]:
            factor *= -1

        wires = []
        if self.force_cross_section:
            wire = Workplane(self.workplane).center(0, 0)
            for point in self.path_points[:-1]:
                wire = (
                    wire.workplane(offset=point[1] * factor)
                    .center(point[0], 0)
                    .circle(self.radius)
                )

                wires.append(wire)

                wire = (
                    wire.center(-point[0], 0)
                    .workplane(offset=-point[1] * factor)
                )

            self.wire = wires

            solid = wire.workplane(
                offset=self.path_points[-1][1] * factor) \
                .center(self.path_points[-1][0], 0) \
                .circle(self.radius) \
                .sweep(path, multisection=True)

        else:

            wire = (
                Workplane(self.workplane)
                .workplane(offset=self.path_points[0][1] * factor)
                .center(self.path_points[0][0], 0)
                .workplane()
                .circle(self.radius)
                .center(-self.path_points[0][0], 0)
                .workplane(offset=-self.path_points[0][1] * factor)
                .workplane(offset=self.path_points[-1][1] * factor)
                .center(self.path_points[-1][0], 0)
                .workplane()
                .circle(self.radius)
            )

            self.wire = wire

            solid = wire.sweep(path, multisection=True)

        solid = self.rotate_solid(solid)
        solid = self.perform_boolean_operations(solid)
        self.solid = solid
        return solid
