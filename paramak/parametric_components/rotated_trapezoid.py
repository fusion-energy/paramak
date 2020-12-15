
import math

from paramak import RotateStraightShape
from paramak.utils import rotate


class RotatedTrapezoid(RotateStraightShape):
    """Creates a rotated trapezoid (truncated triangle) shape.

    Args:
        length_1 (float): the length of the top parrallel edge of the trapezoid
            (cm).
        length_2 (float): the length of the base parrallel edge of the
            trapezoid (cm).
        length_3 (float): the height of the trapezoid, the distances from top
            to base (cm).
        pivot_point ((float, float)): the coordinates of the center of
            rotation (x,z). The piviot point is located in the center of the
            length_1 edge (cm).
        pivot_angle (float, optional): the angle (in degrees) to pivot (rotate)
            the shape by around the pivot point. Defaults to 0.
        stp_filename (str, optional): defaults to "RotatedTrapezoid.stp".
        stl_filename (str, optional): defaults to "RotatedTrapezoid.stl".
        name (str, optional): defaults to "rotated_trapezoid".
        material_tag (str, optional): defaults to "rotated_trapezoid_mat".
    """

    def __init__(
        self,
        length_1,
        length_2,
        length_3,
        pivot_point,
        pivot_angle=0.,
        stp_filename="RotatedTrapezoid.stp",
        stl_filename="RotatedTrapezoid.stl",
        name="rotated_trapezoid",
        material_tag="rotated_trapezoid_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

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
            (
                self.pivot_point[0] + self.length_1 / 2.0,
                self.pivot_point[1]
            ),
            (
                self.pivot_point[0] - self.length_1 / 2.0,
                self.pivot_point[1]
            ),
            (
                self.pivot_point[0] - self.length_2 / 2.0,
                self.pivot_point[1] - self.length_3
            ),
            (
                self.pivot_point[0] + self.length_2 / 2.0,
                self.pivot_point[1] - self.length_3
            ),
        ]

        points = []

        for point in non_rotated_points:
            x, y = rotate(
                origin=self.pivot_point,
                point=point,
                angle=math.radians(self.pivot_angle)
            )
            points.append((x, y))

        self.points = points
