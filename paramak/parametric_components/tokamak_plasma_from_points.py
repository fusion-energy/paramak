
from paramak import Plasma


class PlasmaFromPoints(Plasma):
    """Creates a double null tokamak plasma shape that is controlled by 3
    coordinates.

    Args:
        outer_equatorial_x_point (float): the x value of the outer equatorial
            of the plasma (cm).
        inner_equatorial_x_point (float): the x value of the inner equatorial
            of the plasma (cm).
        high_point (tuple of 2 floats): the (x,z) coordinate values of the top
            of the plasma (cm).
    """

    def __init__(
        self,
        outer_equatorial_x_point,
        inner_equatorial_x_point,
        high_point,
        **kwargs
    ):

        minor_radius = (outer_equatorial_x_point -
                        inner_equatorial_x_point) / 2.0
        major_radius = inner_equatorial_x_point + minor_radius
        elongation = high_point[1] / minor_radius
        triangularity = (major_radius - high_point[0]) / minor_radius

        super().__init__(
            elongation=elongation,
            major_radius=major_radius,
            minor_radius=minor_radius,
            triangularity=triangularity,
            **kwargs
        )

        self.outer_equatorial_x_point = outer_equatorial_x_point
        self.inner_equatorial_x_point = inner_equatorial_x_point
        self.high_point = high_point

    @property
    def outer_equatorial_x_point(self):
        return self._outer_equatorial_x_point

    @outer_equatorial_x_point.setter
    def outer_equatorial_x_point(self, value):
        self._outer_equatorial_x_point = value

    @property
    def inner_equatorial_x_point(self):
        return self._inner_equatorial_x_point

    @inner_equatorial_x_point.setter
    def inner_equatorial_x_point(self, value):
        self._inner_equatorial_x_point = value

    @property
    def high_point(self):
        return self._high_point

    @high_point.setter
    def high_point(self, value):
        self._high_point = value
