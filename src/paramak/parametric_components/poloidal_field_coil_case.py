from typing import List, Optional, Tuple, Union

from cadquery import Plane
from paramak import RotateStraightShape


class PoloidalFieldCoilCase(RotateStraightShape):
    """Creates a casing for a rectangular coil from inputs that
    describe the existing coil and the thickness of the casing required.

    Args:
        coil_height: the vertical (z axis) height of the coil (cm).
        coil_width: the horizontal (x axis) width of the coil (cm).
        center_point: the center of the coil (x,z) values (cm).
        casing_thickness: the thickness of the coil casing (cm).
    """

    def __init__(
        self,
        casing_thickness: Tuple[float, float],
        coil_height: float,
        coil_width: float,
        center_point: Tuple[float, float],
        name: str = "poloidal_field_coil",
        color: Tuple[float, float, float, Optional[float]] = (1.0, 1.0, 0.498),
        rotation_axis: Optional[str] = None,
        rotation_angle: float = 360.0,
        azimuth_placement_angle: Optional[Union[float, List[float]]] = 0.0,
        workplane: Optional[Union[str, Plane]] = "XZ",
        cut=None,
        intersect=None,
        union=None,
        **kwargs
    ) -> None:

        super().__init__(color=color, **kwargs)

        super().__init__(
            name=name,
            rotation_axis=rotation_axis,
            rotation_angle=rotation_angle,
            color=color,
            azimuth_placement_angle=azimuth_placement_angle,
            workplane=workplane,
            cut=cut,
            intersect=intersect,
            union=union,
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
        inner_box = RotateStraightShape(
            points=self.points[:4],
            rotation_axis=self.rotation_axis,
            # rotation_angle=self.rotation_angle,
            azimuth_placement_angle=self.azimuth_placement_angle,
            workplane=self.workplane,
            cut=self.cut,
            intersect=self.intersect,
            union=self.union,
        )

        # creates a large box that surrounds the smaller box
        outer_box = RotateStraightShape(
            points=self.points[5:9],
            rotation_axis=self.rotation_axis,
            rotation_angle=self.rotation_angle,
            azimuth_placement_angle=self.azimuth_placement_angle,
            workplane=self.workplane,
            cut=self.cut,
            intersect=self.intersect,
            union=self.union,
        )

        # subtracts the two boxes to leave a hollow box
        new_shape = outer_box.solid.cut(inner_box.solid)

        self.solid = new_shape

        return new_shape
