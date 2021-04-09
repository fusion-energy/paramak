
from typing import Optional, Tuple
from paramak import RotateMixedShape


class CenterColumnShieldHyperbola(RotateMixedShape):
    """A center column shield volume with a hyperbolic outer profile and
    constant cylindrical inner profile.

    Args:
        height: height of the center column shield.
        inner_radius: the inner radius of the center column shield.
        mid_radius: the inner radius of the outer hyperbolic profile of
            the center column shield.
        outer_radius: the outer radius of the center column shield.
        stp_filename: Defaults to "CenterColumnShieldHyperbola.stp".
        stl_filename: Defaults to "CenterColumnShieldHyperbola.stl".
        name: Defaults to "center_column".
        material_tag: Defaults to "center_column_shield_mat".
    """

    def __init__(
        self,
        height: float,
        inner_radius: float,
        mid_radius: float,
        outer_radius: float,
        stp_filename: Optional[str] = "CenterColumnShieldHyperbola.stp",
        stl_filename: Optional[str] = "CenterColumnShieldHyperbola.stl",
        name: Optional[str] = "center_column",
        material_tag: Optional[str] = "center_column_shield_mat",
        color: Optional[Tuple[float, float, float,
                              Optional[float]]] = (0., 0.333, 0.),
        **kwargs
    ) -> None:

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.height = height
        self.inner_radius = inner_radius
        self.mid_radius = mid_radius
        self.outer_radius = outer_radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius):
        self._inner_radius = inner_radius

    @property
    def mid_radius(self):
        return self._mid_radius

    @mid_radius.setter
    def mid_radius(self, mid_radius):
        self._mid_radius = mid_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius):
        self._outer_radius = outer_radius

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the center column shield shape."""

        if not self.inner_radius <= self.mid_radius <= self.outer_radius:
            raise ValueError("inner_radius must be less than mid radius. \
                mid_radius must be less than outer_radius.")

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (self.outer_radius, self.height / 2, "spline"),
            (self.mid_radius, 0, "spline"),
            (self.outer_radius, -self.height / 2, "straight"),
            (self.inner_radius, -self.height / 2, "straight")
        ]

        self.points = points
