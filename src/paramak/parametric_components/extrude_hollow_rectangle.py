from typing import List, Optional, Tuple, Union

from cadquery import Plane
from paramak import ExtrudeStraightShape


class ExtrudeHollowRectangle(ExtrudeStraightShape):
    """Creates a rectangular with a hollow section extrusion.

    Args:
        height: the height of the internal hollow section.
        width: the width of the internal hollow section.
        distance: the depth of the internal hollow section.
        casing_thickness: the thickness of the casing around the hollow section.
        name: defaults to "extrude_rectangle".
        center_point: the center of the rectangle (x,z) values (cm).
    """

    def __init__(
        self,
        height: float,
        width: float,
        distance: float,
        casing_thickness: float,
        name: str = "extrude_hollow_rectangle",
        center_point: Tuple[float, float] = (0, 0),
        extrude_both: bool = True,
        color: Tuple[float, float, float, Optional[float]] = (0.5, 0.5, 0.5),
        azimuth_placement_angle: Union[float, List[float]] = 0.0,
        workplane: Union[str, Plane] = "XZ",
        cut=None,
        intersect=None,
        union=None,
        extrusion_start_offset: float = 0.0,
        **kwargs
    ) -> None:

        super().__init__(
            name=name,
            distance=distance,
            extrude_both=extrude_both,
            color=color,
            azimuth_placement_angle=azimuth_placement_angle,
            workplane=workplane,
            cut=cut,
            intersect=intersect,
            union=union,
            extrusion_start_offset=extrusion_start_offset,
            **kwargs
        )

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
        #   | |   cp    | |
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

    def create_solid(self):

        # creates a small box that surrounds the geometry
        inner_box = ExtrudeStraightShape(
            distance=self.distance,
            points=self.points[:4],
            extrude_both=self.extrude_both,
            azimuth_placement_angle=self.azimuth_placement_angle,
            workplane=self.workplane,
            cut=self.cut,
            intersect=self.intersect,
            union=self.union,
            extrusion_start_offset=self.extrusion_start_offset,
        )

        # creates a large box that surrounds the smaller box
        outer_box = ExtrudeStraightShape(
            distance=self.distance,
            points=self.points[5:9],
            extrude_both=self.extrude_both,
            azimuth_placement_angle=self.azimuth_placement_angle,
            workplane=self.workplane,
            cut=self.cut,
            intersect=self.intersect,
            union=self.union,
            extrusion_start_offset=self.extrusion_start_offset,
        )

        # subtracts the two boxes to leave a hollow box
        new_shape = outer_box.solid.cut(inner_box.solid)

        self.solid = new_shape

        return new_shape
