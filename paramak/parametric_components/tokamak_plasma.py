import math
from pathlib import Path

import numpy as np
import scipy

from paramak import RotateSplineShape


class Plasma(RotateSplineShape):
    """Creates a double null tokamak plasma shape that is controlled
       by 4 shaping parameters.

    :param major_radius: the major radius of the plasma (cm)
    :type major_radius: float
    :param minor_radius: the minor radius of the plasma (cm)
    :type minor_radius: float
    :param triangularity: the triangularity of the plasma
    :type triangularity: float
    :param elongation: the elongation of the plasma
    :type elongation: float
    :param vertical_displacement: the vertical_displacement of the plasma (cm)
    :type vertical_displacement: float
    :param num_points: number of points to described the shape
    :type num_points: int
    :param configuration: plasma configuration
     ("non-null", "single-null", "double-null"). Defaults to "non-null")
    :type configuration: str
    :param x_point_shift: Shift parameters for locating the X points in [0, 1].
     Default to 0.1.
    :type x_point_shift: float

    :return: a shape object that has generic functionality with 4 attributes
       (outer_equatorial_point, inner_equatorial_point, high_point, low_point)
       as tuples of 2 floats
    :rtype: paramak shape object
    """

    def __init__(
        self,
        name='plasma',
        material_tag='DT_plasma',
        elongation=2.0,
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        vertical_displacement=0,
        num_points=50,
        configuration="non-null",
        x_point_shift=0.1,
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

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            cut=cut,
            **default_dict
        )

        # properties needed for plasma shapes
        self.elongation = elongation
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.vertical_displacement = vertical_displacement
        self.num_points = num_points
        # self.points = points
        self.configuration = configuration
        self.x_point_shift = x_point_shift

        self.outer_equatorial_point = None
        self.inner_equatorial_point = None
        self.high_point = None
        self.low_point = None
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
    def vertical_displacement(self):
        return self._vertical_displacement

    @vertical_displacement.setter
    def vertical_displacement(self, value):
        self._vertical_displacement = value

    @property
    def openmc_install_directory(self):
        return self._openmc_install_directory

    @openmc_install_directory.setter
    def openmc_install_directory(self, openmc_install_directory):
        if Path(openmc_install_directory).exists() is False:
            raise ValueError("openmc_install_directory is out of range")
        else:
            self._openmc_install_directory = openmc_install_directory

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, minor_radius):
        if minor_radius > 2000 or minor_radius < 1:
            raise ValueError("minor_radius is out of range")
        else:
            self._minor_radius = minor_radius

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, major_radius):
        if major_radius > 2000 or major_radius < 1:
            raise ValueError("major_radius is out of range")
        else:
            self._major_radius = major_radius

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, elongation):
        if elongation > 4 or elongation < 0:
            raise ValueError("elongation is out of range")
        else:
            self._elongation = elongation

    def compute_x_points(self, radii, elongation, triangularity, shift):
        """Computes the location of X points based on plasma parameters and
         configuration

        Args:
            radii ((float, float)): minor and major radii
            elongation (float): elongation
            triangularity (float): triangularity
            shift (float): shift for estimating X points locations

        Returns:
            ((float, float), (float, float)): lower and upper x points
             coordinates. None if no x points
        """
        lower_x_point, upper_x_point = None, None  # non-null config
        minor_radius, major_radius = radii

        if self.configuration == "single-null" or \
           self.configuration == "double-null":
            # no X points for non-null config
            lower_x_point = (
                1-(1+shift)*triangularity*minor_radius,
                (1+shift)*elongation*minor_radius
            )

            if self.configuration == "double-null":
                # upper_x_point is up-down symmetrical
                upper_x_point = (
                    lower_x_point[0],
                    -lower_x_point[1]
                )
        return lower_x_point, upper_x_point

    def find_points(self):
        """Finds the XZ points that describe the 2D profile of the plasma.
        """

        # create array of angles theta
        theta = np.linspace(0, 2*np.pi, num=self.num_points)

        # parametric equations for plasma
        def R(theta):
            return self.major_radius + self.minor_radius*np.cos(
                theta + self.triangularity*np.sin(theta))

        def Z(theta):
            return self.elongation*self.minor_radius*np.sin(theta) + \
                self.vertical_displacement

        # R and Z coordinates
        R_points, Z_points = R(theta), Z(theta)

        # create a 2D array for points coordinates
        points = np.stack((R_points, Z_points), axis=1)

        # set self.points
        self.points = list(points)

        # set the points of interest
        self.high_point = (
            self.major_radius-self.triangularity*self.minor_radius,
            self.elongation*self.minor_radius)
        self.low_point = (
            self.major_radius-self.triangularity*self.minor_radius,
            -self.elongation*self.minor_radius)
        self.outer_equatorial_point = (
            self.major_radius + self.minor_radius, 0)
        self.inner_equatorial_point = (
            self.major_radius - self.minor_radius, 0)
