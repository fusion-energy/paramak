from typing import Optional, Tuple

from paramak import RotateMixedShape


class CenterColumnShieldFlatTopHyperbola(RotateMixedShape):
    """A center column shield volume with a hyperbolic outer profile joined to
    flat profiles at the top and bottom of the shield, and a constant
    cylindrical inner profile.

    Args:
        height: height of the center column shield.
        arc_height: height of the outer hyperbolic profile of the center column
            shield.
        inner_radius: the inner radius of the center column shield.
        mid_radius: the inner radius of the outer hyperbolic profile of the
            center column shield.
        outer_radius: the outer_radius of the center column shield.
        name: Defaults to "center_column".
    """

    def __init__(
        self,
        height: float,
        arc_height: float,
        inner_radius: float,
        mid_radius: float,
        outer_radius: float,
        name: str = "center_column",
        color: Tuple[float, float, float, Optional[float]] = (
            0.0,
            0.333,
            0.0,
        ),
        **kwargs
    ) -> None:

        super().__init__(name=name, color=color, **kwargs)

        self.height = height
        self.arc_height = arc_height
        self.mid_radius = mid_radius
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: float):
        self._height = height

    @property
    def arc_height(self):
        return self._arc_height

    @arc_height.setter
    def arc_height(self, arc_height: float):
        self._arc_height = arc_height

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius: float):
        self._inner_radius = inner_radius

    @property
    def mid_radius(self):
        return self._mid_radius

    @mid_radius.setter
    def mid_radius(self, mid_radius: float):
        self._mid_radius = mid_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius: float):
        self._outer_radius = outer_radius

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the center column shield shape."""

        if not self.inner_radius <= self.mid_radius <= self.outer_radius:
            raise ValueError(
                "inner_radius must be less than mid_radius. \
                mid_radius must be less than outer_radius."
            )

        if self.arc_height >= self.height:
            msg = "arc_height ({self.arc_height}) is larger than height " "({self.height})"
            raise ValueError(msg)

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (self.outer_radius, self.height / 2, "straight"),
            (self.outer_radius, self.arc_height / 2, "spline"),
            (self.mid_radius, 0, "spline"),
            (self.outer_radius, -self.arc_height / 2, "straight"),
            (self.outer_radius, -self.height / 2, "straight"),
            (self.inner_radius, -self.height / 2, "straight"),
        ]

        self.points = points
