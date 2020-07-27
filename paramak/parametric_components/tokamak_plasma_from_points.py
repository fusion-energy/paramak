import math
from pathlib import Path

import numpy as np
import scipy

from paramak import Plasma


class Plasma_from_points(Plasma):
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
        name='plasma',
        material_tag='DT_plasma',
        num_points=50,
        stp_filename="plasma.stp",
        color=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        cut=None,
        **kwargs
    ):
        default_dict = {'points':None,
                        'workplane':"XZ",
                        'solid':None,
                        'hash_value':None
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        minor_radius = (outer_equatorial_x_point - inner_equatorial_x_point) / 2.
        major_radius = inner_equatorial_x_point + minor_radius
        elongation = high_point[1] / minor_radius
        triangularity = high_point[0] / major_radius

        super().__init__(
            name='plasma',
            material_tag='DT_plasma',
            elongation=elongation,
            major_radius=major_radius,
            minor_radius=minor_radius,
            triangularity=triangularity,
            vertical_displacement=0,
            num_points=50,
            configuration="non-null",
            x_point_shift=0.1,
            stp_filename="plasma.stp",
            color=None,
            rotation_angle=360,
            azimuth_placement_angle=0,
            cut=None,
            **default_dict
        )
