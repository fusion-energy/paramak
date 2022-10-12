from typing import Optional, Tuple

from cadquery import Workplane

from paramak import Shape


class RotateCircleShape(Shape):
    """Rotates a circular 3d CadQuery solid from a central point and a radius

    Args:
        radius: radius of the shape
        rotation_angle: The rotation_angle to use when revolving the solid
            (degrees). Defaults to 360.0.
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
        rotation_angle: float = 360.0,
        color: Tuple[float, float, float, Optional[float]] = (1.0, 1.0, 0.6),
        name: str = "rotatecircleshape",
        translate: Optional[Tuple[float, float, float]] = None,
        **kwargs
    ):

        super().__init__(color=color, name=name, **kwargs)
        self.radius = radius
        self.rotation_angle = rotation_angle
        self.color = color
        self.name = name
        self.translate = translate

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        wire = Workplane(self.workplane).moveTo(self.points[0][0], self.points[0][1]).circle(self.radius)

        self.wire = wire

        solid = wire.revolve(self.rotation_angle)

        solid = self.rotate_solid(solid)
        solid = self.perform_boolean_operations(solid)

        if self.translate:
            solid = solid.translate(self.translate)

        self.solid = solid
        return solid
