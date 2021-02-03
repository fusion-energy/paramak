
import math
from typing import Optional, Tuple

from paramak import ExtrudeStraightShape


class HexagonPin(ExtrudeStraightShape):
    """Creates an extruded hexagon by a provided distance about a center point.

    Args:
        length_of_side: the length of one side of the hexagon (mm).
        distance: extruded distance along the y-direction (mm).
        center_point: the center of the hexagon on the x-z plane (mm).
        stp_filename: defaults to "HexagonPin.stp".
        stl_filename: defaults to "HexagonPin.stl".
        name: defaults to "hexagon_pin".
        material_tag: defaults to "hexagon_pin_mat".
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

        points = []
        for i in range(6):
            point = (self.length_of_side * math.cos(math.pi / 3 * i) +
                     self.center_point[0],
                     self.length_of_side * math.sin(math.pi / 3 * i) +
                     self.center_point[1])
            points.append(point)

        self.points = points
