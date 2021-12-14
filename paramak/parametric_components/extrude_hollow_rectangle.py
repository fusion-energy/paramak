from typing import Tuple

from paramak import ExtrudeStraightShape


class ExtrudeHollowRectangle(ExtrudeStraightShape):
    """Creates a rectangular with a hollow section extrusion.

    Args:
        height: the vertical (z axis) height of the rectangle (cm).
        width: the horizontal (x axis) width of the rectangle (cm).
        casing_thickness: the thickness of the casing (cm).
        center_point: the center of the rectangle (x,z) values (cm).
        name: defaults to "extrude_rectangle".
    """

    def __init__(
        self,
        height: float,
        width: float,
        distance: float,
        casing_thickness: float,
        center_point: Tuple[float, float] = (0, 0),
        name: str = "extrude_hollow_rectangle",
        **kwargs
    ) -> None:

        self.distance = distance
        super().__init__(name=name, distance=self.distance, **kwargs)

        self.center_point = center_point
        self.height = height
        self.width = width
        self.casing_thickness = casing_thickness

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
        the 2D profile of the shape."""

        #   9-------------6
        #   | 4 -------5,1|
        #   | |         | |
        #   | |  (0,0)  | |
        #   | |         | |
        #   | 3 ------- 2 |
        #   8-------------7

        points = [
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),
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
