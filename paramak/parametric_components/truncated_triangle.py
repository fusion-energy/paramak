
import math

from paramak import RotateStraightShape
from paramak.utils import rotate


class TruncatedTriangle(RotateStraightShape):
    """Creates a rectangular poloidal field coil.

    Args:
        length_1 (float): the (cm).
        length_2 (float): the horizontal (x axis) width of the coil (cm).
        length_3 (float): the center of the coil (x,z) values
        pivot_point (tuple of floats): the coordinates of the center of
            rotation (x,z) (cm).
        pivot_angle (float, optional): the angle (in degrees) to pivot (rotate)
            the shape by on the XY plane. Defaults to 0.
        stp_filename (str, optional): defaults to "TruncatedTriangle.stp".
        stl_filename (str, optional): defaults to "TruncatedTriangle.stl".
        name (str, optional): defaults to "truncated_tri".
        material_tag (str, optional): defaults to "truncated_tri_mat".
    """

    def __init__(
        self,
        length_1,
        length_2,
        length_3,
        pivot_point,
        pivot_angle=0.,
        stp_filename="TruncatedTriangle.stp",
        stl_filename="TruncatedTriangle.stl",
        name="truncated_tri",
        material_tag="truncated_tri_mat",
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
        the 2D profile of the poloidal field coil shape."""

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
