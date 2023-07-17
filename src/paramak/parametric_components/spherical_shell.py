from typing import Optional, Tuple

from paramak import RotateMixedShape, Shape
from paramak.utils import patch_workplane
import cadquery as cq

patch_workplane()


class SphericalShell(RotateMixedShape):

    """Create a 3d CadQuery solid spherical shell from an inner radius and a shell thickness

    Args:
        inner_radius: inner radius of the spherical shell (needs to be >= 0)
        shell_thickness: thickness of the spherical shell (needs to be > 0)
        rotation_angle: rotation_angle of solid created. a cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.
        color: the color to use when exporting the shape to CAD formats that
            support color. A tuple of three floats each ranging between 0
            and 1. Defaults to (0.09,0.58,0.71)
        name: the name of the shape, used to name files when exporting and
            as a legend in plots. Defaults to 'sphericalshellshape'
        translate: (optional) distance to translate / move the shape by. Specified as
            a vector of (X,Y,Z) directions.
    """

    def __init__(
        self,
        inner_radius: float,
        shell_thickness: float,
        name: str = "sphericalshell",
        color: Tuple[float, float, float, Optional[float]] = (
            0.09,
            0.58,
            0.71,
        ),
        **kwargs
    ):

        super().__init__(color=color, name=name, **kwargs)

        self.inner_radius = inner_radius
        self.shell_thickness = shell_thickness
        self.name = name
        self.color = color

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        if value is None:
            raise ValueError("Inner radius of SphericalShell cannot be None")
        if value < 0:
            raise ValueError("Inner radius of SphericalShell cannot be negative")
        self._inner_radius = value

    @property
    def shell_thickness(self):
        return self._shell_thickness

    @shell_thickness.setter
    def shell_thickness(self, value):
        if value is None:
            raise ValueError("Shell thickness of SphericalShell cannot be None")
        if value <= 0:
            raise ValueError("Shell thickness of SphericalShell needs to be > 0")
        self._shell_thickness = value

    def find_points(self):

        if not 0 <= self.inner_radius:
            raise ValueError("inner_radius must be 0 or greater.less than outer_radius.")

        if not 0 < self.shell_thickness:
            raise ValueError("shell_tickness must be greater than 0.")

        if self.inner_radius == 0:
            # solid sphere
            self.points = [
                (0, -self.shell_thickness, "straight"),
                (0, self.shell_thickness, "circle"),
                (self.shell_thickness, 0, "circle"),
            ]
        else:
            # shell
            self.points = [
                (0, -self.inner_radius, "straight"),
                (0, -self.inner_radius - self.shell_thickness, "circle"),
                (self.inner_radius + self.shell_thickness, 0, "circle"),
                (0, self.inner_radius + self.shell_thickness, "straight"),
                (0, self.inner_radius, "circle"),
                (self.inner_radius, 0, "circle"),
            ]

    def create_solid(self):
        """Creates a extruded 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        if self.rotation_angle == 360.0:
            "The prevents a 360 sphere from getting additional surfaces from the rotation"
            self.solid = (
                cq.Workplane()
                .sphere(self.inner_radius + self.shell_thickness)
                .cut(cq.Workplane().sphere(self.inner_radius))
            )
            return self
        else:
            return super().create_solid()
