
from collections import Iterable

import cadquery as cq

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeCircleShape(Shape):
    """Extrudes a circular 3d CadQuery solid from a central point and a radius

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        radius (float): radius of the shape.
        rotation_angle (float): rotation_angle of solid created. a cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.
        extrude_both (bool, optional): if set to True, the extrusion will
            occur in both directions. Defaults to True.
        stp_filename (str, optional): Defaults to "ExtrudeCircleShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeCircleShape.stl".
    """

    def __init__(
        self,
        distance,
        radius,
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

    def create_solid(self):
        """Creates an extruded 3d solid using points connected with circular
        edges.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # Creates a cadquery solid from points and revolves
        solid = (
            cq.Workplane(self.workplane)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
            .extrude(distance=-self.distance / 2.0, both=self.extrude_both)
        )

        solid = self.rotate_solid(solid)
        calculate_wedge_cut(self)
        self.perform_boolean_operations(solid)

        return solid
