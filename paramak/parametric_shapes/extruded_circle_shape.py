
import cadquery as cq
from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeCircleShape(Shape):
    """Extrudes a circular 3d CadQuery solid from a central point and a radius

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        radius (float): radius of the shape.
        rotation_angle (float): rotation_angle of solid created. a cut is
            performed from rotation_angle to 360 degrees. Defaults to 360.
        extrude_both (bool, optional): if set to True, the extrusion will
            occur in both directions. Defaults to True.
        stp_filename (str, optional): Defaults to "ExtrudeCircleShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeCircleShape.stl".
    """

    def __init__(
        self,
        distance,
        radius,
        extrusion_start_offset=0.0,
        rotation_angle=360,
        extrude_both=True,
        stp_filename="ExtrudeCircleShape.stp",
        stl_filename="ExtrudeCircleShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
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
        """Creates an extruded 3d solid using points connected with circular
        edges.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # so a positive offset moves extrusion further from axis of azimuthal
        # placement rotation
        extrusion_offset = -self.extrusion_start_offset

        if not self.extrude_both:
            extrusion_distance = -self.distance
        else:
            extrusion_distance = -self.distance / 2.0

        wire = (
            cq.Workplane(self.workplane)
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
