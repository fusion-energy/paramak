
from typing import Optional, Tuple

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeMixedShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with a mixture of
    straight and spline connections.

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics)
        extrude_both: If set to True, the extrusion will occur in both
            directions. Defaults to True.
        rotation_angle: rotation angle of solid created. A cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.0.
        stp_filename: Defaults to "ExtrudeMixedShape.stp".
        stl_filename: Defaults to "ExtrudeMixedShape.stl".

    """

    def __init__(
        self,
        distance: float,
        extrude_both: Optional[bool] = True,
        rotation_angle: Optional[float] = 360.0,
        extrusion_start_offset: Optional[float] = 0.0,
        stp_filename: Optional[str] = "ExtrudeMixedShape.stp",
        stl_filename: Optional[str] = "ExtrudeMixedShape.stl",
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.2, 0.627, 0.172),
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )
        self.distance = distance
        self.extrude_both = extrude_both
        self.rotation_angle = rotation_angle
        self.extrusion_start_offset = extrusion_start_offset

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
        """Creates an extruded 3d solid using points connected with straight
        and spline edges.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        solid = super().create_solid()

        if not self.extrude_both:
            extrusion_distance = -self.distance
        else:
            extrusion_distance = -self.distance / 2.0

        wire = solid.close()

        self.wire = wire

        solid = wire.extrude(
            distance=extrusion_distance,
            both=self.extrude_both)

        # filleting rectangular port cutter edges
        # must be done before azimuthal placement
        if hasattr(self, "add_fillet"):
            solid = self.add_fillet(solid)

        solid = self.rotate_solid(solid)
        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)
        self.solid = solid

        return solid
