from typing import List, Optional, Tuple

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
        radius: float,
        path_points: List[Tuple[float, float]],
        workplane: str = "XY",
        path_workplane: str = "XZ",
        force_cross_section: bool = False,
        color: Tuple[float, float, float, Optional[float]] = (
            0.651,
            0.808,
            0.89,
        ),
        name: str = "sweepcircleshape",
        translate: Optional[Tuple[float, float, float]] = None,
        **kwargs
    ):

        super().__init__(workplane=workplane, color=color, name=name, **kwargs)

        self.radius = radius
        self.path_points = path_points
        self.workplane = workplane
        self.path_workplane = path_workplane
        self.force_cross_section = force_cross_section
        self.color = color
        self.name = name
        self.translate = translate

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
            raise ValueError("workplane and path_workplane must start with the same letter")
        elif value == self.workplane:
            raise ValueError("workplane and path_workplane must be different")
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
                wire = wire.workplane(offset=point[1] * factor).center(point[0], 0).circle(self.radius)

                wires.append(wire)

                wire = wire.center(-point[0], 0).workplane(offset=-point[1] * factor)

            self.wire = wires

            solid = (
                wire.workplane(offset=self.path_points[-1][1] * factor)
                .center(self.path_points[-1][0], 0)
                .circle(self.radius)
                .sweep(path, multisection=True)
            )

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

        if self.translate:
            solid = solid.translate(self.translate)

        self.solid = solid
        return solid
