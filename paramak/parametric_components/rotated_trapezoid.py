import math
from typing import Tuple
from paramak import RotateStraightShape
from paramak.utils import rotate


class RotatedTrapezoid(RotateStraightShape):
    """Creates a rotated trapezoid (truncated triangle) shape.

    Args:
        length_1: the length of the top parallel edge of the trapezoid (cm).
        length_2: the length of the base parallel edge of the trapezoid (cm).
        length_3: the height of the trapezoid, the distances from top to base (cm).
        pivot_point: the coordinates of the center of rotation (x,z). The
            pivot point is located in the center of the length_1 edge (cm).
        pivot_angle: the angle (in degrees) to pivot (rotate) the shape by
            around the pivot point. Defaults to 0.
        name: defaults to "rotated_trapezoid".
    """

    def __init__(
        self,
        length_1: float,
        length_2: float,
        length_3: float,
        pivot_point: Tuple[float, float],
        pivot_angle: float = 0.0,
        name: str = "rotated_trapezoid",
        **kwargs
    ):

        super().__init__(name=name, **kwargs)

        self.length_1 = length_1
        self.length_2 = length_2
        self.length_3 = length_3
        self.pivot_point = pivot_point
        self.pivot_angle = pivot_angle

    @property
    def pivot_point(self):
        return self._pivot_point

    @pivot_point.setter
    def pivot_point(self, pivot_point):
        self._pivot_point = pivot_point

    @property
    def length_1(self):
        return self._length_1

    @length_1.setter
    def length_1(self, length_1):
        self._length_1 = length_1

    @property
    def length_2(self):
        return self._length_2

    @length_2.setter
    def length_2(self, length_2):
        self._length_2 = length_2

    @property
    def length_3(self):
        return self._length_3

    @length_3.setter
    def length_3(self, length_3):
        self._length_3 = length_3

    @property
    def pivot_angle(self):
        return self._pivot_angle

    @pivot_angle.setter
    def pivot_angle(self, pivot_angle):
        self._pivot_angle = pivot_angle

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the trapezoid shape."""

        non_rotated_points = [
            (self.pivot_point[0] + self.length_1 / 2.0, self.pivot_point[1]),
            (self.pivot_point[0] - self.length_1 / 2.0, self.pivot_point[1]),
            (
                self.pivot_point[0] - self.length_2 / 2.0,
                self.pivot_point[1] - self.length_3,
            ),
            (
                self.pivot_point[0] + self.length_2 / 2.0,
                self.pivot_point[1] - self.length_3,
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
