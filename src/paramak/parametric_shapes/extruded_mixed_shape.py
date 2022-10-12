from typing import Optional, Tuple

from paramak import Shape
from paramak.utils import calculate_wedge_cut, patch_workplane

patch_workplane()


class ExtrudeMixedShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with a mixture of
    straight and spline connections.

    Args:
        distance: the extrusion distance to use
        extrude_both: If set to True, the extrusion will occur in both
            directions. Defaults to True.
        rotation_angle: rotation angle of solid created. A cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.0.
        extrusion_start_offset:
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
        distance: float,
        extrude_both: bool = True,
        rotation_angle: float = 360.0,
        extrusion_start_offset: float = 0.0,
        color: Tuple[float, float, float, Optional[float]] = (
            0.2,
            0.627,
            0.172,
        ),
        name: str = "extrudemixedshape",
        translate: Optional[Tuple[float, float, float]] = None,
        **kwargs
    ):

        super().__init__(color=color, name=name, **kwargs)
        self.distance = distance
        self.extrude_both = extrude_both
        self.rotation_angle = rotation_angle
        self.extrusion_start_offset = extrusion_start_offset
        self.color = color
        self.name = name
        self.translate = translate

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

        solid = wire.extrude(until=extrusion_distance, both=self.extrude_both)

        # filleting rectangular port cutter edges
        # must be done before azimuthal placement
        if hasattr(self, "add_fillet"):
            solid = self.add_fillet(solid)

        solid = self.rotate_solid(solid)
        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        if self.translate:
            solid = solid.translate(self.translate)

        self.solid = solid

        return solid
