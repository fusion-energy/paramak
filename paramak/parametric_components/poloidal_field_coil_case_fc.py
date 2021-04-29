
from typing import Optional, Tuple

from paramak import RotateStraightShape


class PoloidalFieldCoilCaseFC(RotateStraightShape):
    """Creates a casing for a rectangular poloidal field coil by building
    around an existing coil (which is passed as an argument on construction).

    Args:
        pf_coil (paramak.PoloidalFieldCoil): a pf coil object with a set width,
            height and center point.
        casing_thickness (float): the thickness of the coil casing (cm).
        stp_filename (str, optional): defaults to
            "PoloidalFieldCoilCaseFC.stp".
        stl_filename (str, optional): defaults to
            "PoloidalFieldCoilCaseFC.stl".
        material_tag (str, optional): defaults to "pf_coil_case_mat".
    """

    def __init__(
        self,
        pf_coil,
        casing_thickness,
        stp_filename="PoloidalFieldCoilCaseFC.stp",
        stl_filename="PoloidalFieldCoilCaseFC.stl",
        material_tag="pf_coil_case_mat",
        color: Optional[Tuple[int, int, int]] = (1., 1., 0.498),
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.center_point = pf_coil.center_point
        self.height = pf_coil.height
        self.width = pf_coil.width
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
