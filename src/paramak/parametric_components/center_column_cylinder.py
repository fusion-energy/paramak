from typing import Optional, Tuple, Union

from paramak import RotateStraightShape


class CenterColumnShieldCylinder(RotateStraightShape):
    """A cylindrical center column shield volume with constant thickness.

    Args:
        height: height of the center column shield.
        inner_radius: the inner radius of the center column shield.
        outer_radius: the outer radius of the center column shield.
        center_height: the vertical height of the center of the component.
    """

    def __init__(
        self,
        height: float,
        inner_radius: float,
        outer_radius: float,
        center_height: float = 0.0,
        name: str = "CenterColumnShieldCylinder",
        color: Tuple[float, float, float, Optional[float]] = (
            0.0,
            0.333,
            0.0,
        ),
        **kwargs,
    ) -> None:

        super().__init__(color=color, name=name, **kwargs)

        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.center_height = center_height

    @property
    def center_height(self):
        return self._center_height

    @center_height.setter
    def center_height(self, value: Union[float, int]):
        if not isinstance(value, (int, float)):
            msg = f"CenterColumnShieldBlock.center_height should be a float or int. Not a {type(value)}"
            raise TypeError(msg)

        self._center_height = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: float):
        if value is None:
            raise ValueError("height of the CenterColumnShieldBlock cannot be None")
        self._height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value: float):
        if hasattr(self, "outer_radius"):
            if value >= self.outer_radius:
                msg = f"inner_radius ({value}) is larger than outer_radius " "({self.outer_radius})"
                raise ValueError(msg)
        self._inner_radius = value

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, value: float):
        if hasattr(self, "inner_radius"):
            if value <= self.inner_radius:
                msg = f"inner_radius ({self.inner_radius}) is larger than " "outer_radius ({value})"
                raise ValueError(msg)

        self._outer_radius = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
        2D profile of the center column shield shape."""

        points = [
            (self.inner_radius, self.center_height + self.height / 2),
            (self.outer_radius, self.center_height + self.height / 2),
            (self.outer_radius, self.center_height + (-self.height / 2)),
            (self.inner_radius, self.center_height + (-self.height / 2)),
        ]

        self.points = points
