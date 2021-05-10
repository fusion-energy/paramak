
from typing import Optional, Tuple

from cadquery import Workplane
from paramak import Shape


class RotateCircleShape(Shape):
    """Rotates a circular 3d CadQuery solid from a central point and a radius

    Args:
        radius: radius of the shape
        rotation_angle: The rotation_angle to use when revolving the solid
            (degrees). Defaults to 360.0.
        stp_filename:  Defaults to "RotateCircleShape.stp".
        stl_filename:  Defaults to "RotateCircleShape.stl".
    """

    def __init__(
        self,
        radius: float,
        rotation_angle: Optional[float] = 360.0,
        stp_filename: Optional[str] = "RotateCircleShape.stp",
        stl_filename: Optional[str] = "RotateCircleShape.stl",
        color: Optional[Tuple[float, float, float, Optional[float]]] = (1., 1., 0.6),
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )
        self.radius = radius
        self.rotation_angle = rotation_angle

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

        wire = (
            Workplane(self.workplane)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
        )

        self.wire = wire

        solid = wire.revolve(self.rotation_angle)

        solid = self.rotate_solid(solid)
        solid = self.perform_boolean_operations(solid)
        self.solid = solid
        return solid
