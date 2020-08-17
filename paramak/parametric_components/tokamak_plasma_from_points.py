import math
from pathlib import Path

import numpy as np
import scipy

from paramak import Plasma


class PlasmaFromPoints(Plasma):
    """Creates a double null tokamak plasma shape that is controlled
       by 3 coordinates.

    Args:
        outer_equatorial_x_point (float): the x value of the outer equatorial of the
            plasma (cm).
        inner_equatorial_x_point (float): the x value of the inner equatorial of the
            plasma (cm).
        heigh_point (tuple of 2 floats): the (x,z) coordinate values of the top of the
            plasma (cm).

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to use when
            exportin as html graphs or png images.
        material_tag (str): The material name to use when exporting the neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
            rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a boolean intersect with
            this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        outer_equatorial_x_point,
        inner_equatorial_x_point,
        high_point,
        x_point_shift=0.1,
        configuration="non-null",
        name="plasma",
        material_tag="DT_plasma",
        num_points=50,
        stp_filename="plasma.stp",
        color=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        **kwargs
    ):
        default_dict = {
            "points": None,
            "workplane": "XZ",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        minor_radius = (outer_equatorial_x_point -
                        inner_equatorial_x_point) / 2.0
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
            hash_value=None,
            **default_dict
        )

        self.outer_equatorial_x_point = outer_equatorial_x_point
        self.inner_equatorial_x_point = inner_equatorial_x_point
        self.high_point = high_point
        self.lower_x_point, self.upper_x_point = self.compute_x_points()

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
