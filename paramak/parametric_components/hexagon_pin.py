
import math
from typing import Optional, Tuple

from paramak import ExtrudeStraightShape


class HexagonPin(ExtrudeStraightShape):
    """Creates an extruded hexagon by a provided distance about a center point.

    Args:
        length_of_side: the vertical (z axis) height of the coil (cm).
        width: the horizontal (x axis) width of the coil (cm).
        center_point: the center of the coil (x,z) values (cm).
        stp_filename: defaults to "PoloidalFieldCoil.stp".
        stl_filename: defaults to "PoloidalFieldCoil.stl".
        name: defaults to "pf_coil".
        material_tag: defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        length_of_side: float,
        distance: float,
        center_point: Tuple[float, float] = (0, 0),
        stp_filename: Optional[str] = "HexagonPin.stp",
        stl_filename: Optional[str] = "HexagonPin.stl",
        name: Optional[str] = "hexagon_pin",
        material_tag: Optional[str] = "hexagon_pin_mat",
        **kwargs
    ) -> None:

        super().__init__(
            name=name,
            distance=distance,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.center_point = center_point
        self.length_of_side = length_of_side

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, center_point):
        self._center_point = center_point

    @property
    def length_of_side(self):
        return self._length_of_side

    @length_of_side.setter
    def length_of_side(self, length_of_side):
        self._length_of_side = length_of_side

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the hexagon faced shape."""

        # map of points
        #     p3 ---- p2
        #    -           -
        #   -             -
        #  -               -
        # p4                p1
        #  -               -
        #   -             -
        #    -          -
        #     p5 ---- p6

        point_1 = (self.length_of_side, 0)

        point_2 = self.length_of_side*math.cos(math.radians(60)), \
                    self.length_of_side * math.sin(math.radians(60))

        point_3 = self.length_of_side*math.cos(math.radians(120)), \
                    self.length_of_side * math.sin(math.radians(120))

        point_4 = (-self.length_of_side, 0)

        point_5 = self.length_of_side*math.cos(math.radians(240)), \
                    self.length_of_side * math.sin(math.radians(240))
    
        point_6 = self.length_of_side*math.cos(math.radians(300)), \
                    self.length_of_side * math.sin(math.radians(300))

        # TODO translate points to center around the self.center_point

        points = [point_1, point_2, point_3, point_4, point_5, point_6]

        self.points = points
