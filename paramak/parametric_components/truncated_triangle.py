
from paramak import RotateStraightShape
from paramak.utils import rotate


class TruncatedTriangle(RotateStraightShape):
    """Creates a rectangular poloidal field coil.

    Args:
        l1 (float): the (cm).
        l2 (float): the horizontal (x axis) width of the coil (cm).
        l3 (float): the center of the coil (x,z) values
        pivot_point (tuple of floats): the coordinates of the center of
            rotation (x,z) (cm).
        pivot_angle (float, optional): the angle to pivot (rotate) the shape by
            on the XY plane. Defaults to 0.
        stp_filename (str, optional): defaults to "TruncatedTriangle.stp".
        stl_filename (str, optional): defaults to "TruncatedTriangle.stl".
        name (str, optional): defaults to "truncated_tri".
        material_tag (str, optional): defaults to "truncated_tri_mat".
    """

    def __init__(
        self,
        l1,
        l2,
        l3,
        pivot_point,
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

        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.pivot_point = pivot_point

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, center_point):
        self._center_point = center_point

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        points = [
            (
                self.pivot_point
            )
        ]
        points = [
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper right
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),  # lower right
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),  # lower left
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            )
        ]

        rotate

        self.points = points
