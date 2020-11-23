
from paramak import PoloidalFieldCoil


class PoloidalFieldCoilFP(PoloidalFieldCoil):
    """Creates a rectangular poloidal field coil.

    Args:
        corner_points (list of float tuples): the coordinates of the opposite
            corners of the rectangular shaped coil e.g [(x1, y1), (x2, y2)]
    """

    def __init__(
        self,
        corner_points,
        **kwargs
    ):

        height = abs(corner_points[0][1] - corner_points[1][1])
        width = abs(corner_points[0][0] - corner_points[1][0])

        center_width = (corner_points[0][1] + corner_points[1][1]) / 2.
        center_height = (corner_points[0][1] + corner_points[1][1]) / 2.
        center_point = (center_width, center_height)

        super().__init__(
            height=height,
            width=width,
            center_point=center_point,
            **kwargs
        )

        self.corner_points = corner_points

    @property
    def corner_points(self):
        return self._corner_points

    @corner_points.setter
    def corner_points(self, value):
        # ToDo check the corner points are a list with two entries
        # and each entry is a tuple with two floats
        self._corner_points = value
