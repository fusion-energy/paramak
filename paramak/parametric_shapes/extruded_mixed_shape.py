from collections import Iterable

import cadquery as cq

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeMixedShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with a mixture of
    straight and spline connections.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        extrude_both (bool, optional): If set to True, the extrusion will
            occur in both directions. Defaults to True.
        rotation_angle (float, optional): rotation angle of solid created. A
            cut is performed from rotation_angle to 360 degrees. Defaults to
            360.0.
        stp_filename (str, optional): Defaults to "ExtrudeMixedShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeMixedShape.stl".

    """

    def __init__(
        self,
        distance,
        extrude_both=True,
        rotation_angle=360.0,
        stp_filename="ExtrudeMixedShape.stp",
        stl_filename="ExtrudeMixedShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )
        self.distance = distance
        self.extrude_both = extrude_both
        self.rotation_angle = rotation_angle

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
        """Creates an extruded 3d solid using points connected with straight
        and spline edges.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        solid = super().create_solid()

        # performs extrude in both directions, hence distance / 2
        solid = solid.close().extrude(
            distance=-self.distance / 2.0,
            both=self.extrude_both)

        solid = self.rotate_solid(solid)
        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)
        self.solid = solid   # not necessarily required as set in boolean_operations

        return solid
