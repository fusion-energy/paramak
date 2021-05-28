
from typing import Optional, Tuple

from cadquery import Workplane
from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeCircleShape(Shape):
    """Extrudes a circular 3d CadQuery solid from a central point and a radius

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics)
        radius: radius of the shape.
        rotation_angle: rotation_angle of solid created. a cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.
        extrude_both: if set to True, the extrusion will occur in both
            directions. Defaults to True.
        stp_filename: Defaults to "ExtrudeCircleShape.stp".
        stl_filename: Defaults to "ExtrudeCircleShape.stl".
    """

    def __init__(
        self,
        distance: float,
        radius: float,
        extrusion_start_offset: Optional[float] = 0.0,
        rotation_angle: Optional[float] = 360,
        extrude_both: Optional[bool] = True,
        stp_filename: Optional[str] = "ExtrudeCircleShape.stp",
        stl_filename: Optional[str] = "ExtrudeCircleShape.stl",
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.984, 0.603, 0.6),
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.radius = radius
        self.distance = distance
        self.rotation_angle = rotation_angle
        self.extrude_both = extrude_both
        self.extrusion_start_offset = extrusion_start_offset

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    @property
    def extrusion_start_offset(self):
        return self._extrusion_start_offset

    @extrusion_start_offset.setter
    def extrusion_start_offset(self, value):
        self._extrusion_start_offset = value

    def create_solid(self):
        """Creates a extruded 3d solid using points with circular edges.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        # so a positive offset moves extrusion further from axis of azimuthal
        # placement rotation
        extrusion_offset = -self.extrusion_start_offset

        if not self.extrude_both:
            extrusion_distance = -self.distance
        else:
            extrusion_distance = -self.distance / 2.0

        wire = (
            Workplane(self.workplane)
            .workplane(offset=extrusion_offset)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
        )

        self.wire = wire

        solid = wire.extrude(
            distance=extrusion_distance,
            both=self.extrude_both)

        solid = self.rotate_solid(solid)
        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)
        self.solid = solid

        return solid
