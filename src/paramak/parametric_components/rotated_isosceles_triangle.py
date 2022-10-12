import math
from typing import Tuple
from paramak import RotateStraightShape
from paramak.utils import rotate


class RotatedIsoscelesTriangle(RotateStraightShape):
    """Creates a rotated triangle (truncated triangle) shape.

    Args:
        base_length: the length of the base of the triangle (cm).
        height: the height of the triangle (cm).
        pivot_point: the coordinates of the tip of the triangle at the opposite
            side to the base of the triangle.
        pivot_angle: the angle (in degrees) to pivot (rotate) the shape by
            around the pivot point. Defaults to 0.
        name: defaults to "rotated_triangle".
    """

    def __init__(
        self,
        base_length: float,
        height: float,
        pivot_point: Tuple[float, float],
        pivot_angle: float = 0.0,
        name: str = "rotated_triangle",
        **kwargs
    ):

        super().__init__(name=name, **kwargs)

        self.base_length = base_length
        self.height = height
        self.pivot_point = pivot_point
        self.pivot_angle = pivot_angle

    @property
    def pivot_point(self):
        return self._pivot_point

    @pivot_point.setter
    def pivot_point(self, pivot_point):
        self._pivot_point = pivot_point

    @property
    def base_length(self):
        return self._base_length

    @base_length.setter
    def base_length(self, base_length):
        self._base_length = base_length

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def pivot_angle(self):
        return self._pivot_angle

    @pivot_angle.setter
    def pivot_angle(self, pivot_angle):
        self._pivot_angle = pivot_angle

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the triangle shape."""

        non_rotated_points = [
            self.pivot_point,
            (
                self.pivot_point[0] - self.base_length / 2.0,
                self.pivot_point[1] - self.height,
            ),
            (
                self.pivot_point[0] + self.base_length / 2.0,
                self.pivot_point[1] - self.height,
            ),
        ]

        points = []

        for point in non_rotated_points:
            x, y = rotate(
                origin=self.pivot_point,
                point=point,
                angle=math.radians(self.pivot_angle),
            )
            points.append((x, y))

        self.points = points
