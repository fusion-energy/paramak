import math
from pathlib import Path

import numpy as np
import scipy

from paramak import Plasma


class PlasmaFromPoints(Plasma):
    """Creates a double null tokamak plasma shape that is controlled
       by 3 coordinates.

    :param outer_equatorial_x_point: the x value of the outer equatorial of the plasma (cm)
    :type outer_equatorial_x_point: float
    :param inner_equatorial_x_point: the x value of the inner equatorial of the plasma (cm)
    :type inner_equatorial_x_point: float
    :param high_point: the (x,z) coordinates value of the top of the plasma (cm)
    :type high_point: tuple of 2 floats

    :return: a shape object that has generic functionality with 4 positional attributes
       (outer_equatorial_point, inner_equatorial_point, high_point, low_point)
        as tuples of 2 floats and 4 attributes of the plasma (major_radius, minor_radius,
        elongation, triangularity) as floats

    :rtype: paramak shape object
    """

    def __init__(
        self,
        outer_equatorial_x_point,
        inner_equatorial_x_point,
        high_point,
        x_point_shift=0.1,
        configuration="non-null",
        name='plasma',
        material_tag='DT_plasma',
        num_points=50,
        stp_filename="plasma.stp",
        color=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        **kwargs
    ):
        default_dict = {'points':None,
                        'workplane':"XZ",
                        'solid':None,
                        'hash_value':None,
                        'intersect':None,
                        'cut':None
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        minor_radius = (outer_equatorial_x_point - inner_equatorial_x_point) / 2.
        major_radius = inner_equatorial_x_point + minor_radius
        elongation = high_point[1] / minor_radius
        triangularity = (major_radius - high_point[0]) / minor_radius

        super().__init__(
            name=name,
            material_tag=material_tag,
            elongation=elongation,
            major_radius=major_radius,
            minor_radius=minor_radius,
            triangularity=triangularity,
            vertical_displacement=0,
            num_points=50,
            configuration=configuration,
            x_point_shift=x_point_shift,
            stp_filename="plasma.stp",
            color=None,
            rotation_angle=rotation_angle,
            azimuth_placement_angle=azimuth_placement_angle,
            **default_dict
        )

        self.outer_equatorial_x_point = outer_equatorial_x_point
        self.inner_equatorial_x_point = inner_equatorial_x_point
        self.high_point = high_point
        self.lower_x_point, self.upper_x_point = self.compute_x_points(
            (minor_radius, major_radius), elongation, triangularity,
            x_point_shift
        )

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

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
