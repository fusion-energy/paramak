
from typing import Optional, Tuple
from paramak import RotateStraightShape


class PoloidalFieldCoilCase(RotateStraightShape):
    """Creates a casing for a rectangular coil from inputs that
    describe the existing coil and the thickness of the casing required.

    Args:
        coil_height: the vertical (z axis) height of the coil (cm).
        coil_width: the horizontal (x axis) width of the coil (cm).
        center_point: the center of the coil (x,z) values (cm).
        casing_thickness: the thickness of the coil casing (cm).
        stp_filename: defaults to "PoloidalFieldCoilCase.stp".
        stl_filename: defaults to "PoloidalFieldCoilCase.stl".
        material_tag: defaults to "pf_coil_case_mat".
    """

    def __init__(
        self,
        casing_thickness: Tuple[float, float],
        coil_height: float,
        coil_width: float,
        center_point: Tuple[float, float],
        stp_filename: Optional[str] = "PoloidalFieldCoilCase.stp",
        stl_filename: Optional[str] = "PoloidalFieldCoilCase.stl",
        material_tag: Optional[str] = "pf_coil_case_mat",
        **kwargs
    ) -> None:

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.center_point = center_point
        self.height = coil_height
        self.width = coil_width
        self.casing_thickness = casing_thickness

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, value):
        self._center_point = value

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
        the 2D profile of the poloidal field coil case shape."""

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
            ),  # upper left
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper right
            (
                self.center_point[0] + \
                (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + \
                (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + \
                (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - \
                (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - \
                (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - \
                (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - \
                (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + \
                (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + \
                (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + \
                (self.casing_thickness + self.height / 2.0),
            )
        ]

        self.points = points
