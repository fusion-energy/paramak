from typing import Optional, Tuple

from paramak import RotateStraightShape, PoloidalFieldCoil


class PoloidalFieldCoilCaseFC(RotateStraightShape):
    """Creates a casing for a rectangular poloidal field coil by building
    around an existing coil (which is passed as an argument on construction).

    Args:
        pf_coil: a pf coil object with a set width, height and center point.
        casing_thickness: the thickness of the coil casing (cm).
    """

    def __init__(
        self,
        pf_coil: PoloidalFieldCoil,
        casing_thickness: float,
        color: Tuple[float, float, float, Optional[float]] = (1.0, 1.0, 0.498),
        **kwargs
    ):

        super().__init__(color=color, **kwargs)

        self.pf_coil = pf_coil
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
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
        ]

        self.points = points

    def create_solid(self):

        # creates a small box that surrounds the geometry
        inner_box = self.pf_coil

        # creates a large box that surrounds the smaller box
        outer_box = RotateStraightShape(
            points=self.points[5:9],
            rotation_axis=inner_box.rotation_axis,
            rotation_angle=inner_box.rotation_angle,
            azimuth_placement_angle=inner_box.azimuth_placement_angle,
            workplane=inner_box.workplane,
            cut=self.cut,
            intersect=self.intersect,
            union=self.union,
        )

        # subtracts the two boxes to leave a hollow box
        new_shape = outer_box.solid.cut(inner_box.solid)

        self.solid = new_shape

        return new_shape
