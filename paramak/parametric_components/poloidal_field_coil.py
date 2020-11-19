
from paramak import RotateStraightShape


class PoloidalFieldCoil(RotateStraightShape):
    """Creates a rectangular poloidal field coil.

    Args:
        height (float): the vertical (z axis) height of the coil (cm).
        width (float): the horizontal (x axis) width of the coil (cm).
        center_point (tuple of floats): the center of the coil (x,z) values
            (cm).
        stp_filename (str, optional): defaults to "PoloidalFieldCoil.stp".
        stl_filename (str, optional): defaults to "PoloidalFieldCoil.stl".
        name (str, optional): defaults to "pf_coil".
        material_tag (str, optional): defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        height,
        width,
        center_point,
        stp_filename="PoloidalFieldCoil.stp",
        stl_filename="PoloidalFieldCoil.stl",
        name="pf_coil",
        material_tag="pf_coil_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.center_point = center_point
        self.height = height
        self.width = width

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

        self.points = points
