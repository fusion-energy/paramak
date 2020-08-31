import math
from pathlib import Path

import numpy as np
import scipy

from paramak import RotateSplineShape


class Plasma(RotateSplineShape):
    """Creates a double null tokamak plasma shape that is controlled by 4
    shaping parameters.

    Args:
        elongation (float, optional): the elongation of the plasma.
            Defaults to 2.0.
        major_radius (int, optional): the major radius of the plasma (cm).
            Defaults to 450.
        minor_radius (int, optional): the minor radius of the plasma (cm).
            Defaults to 150.
        triangularity (float, optional): the triangularity of the plasma.
            Defaults to 0.55.
        vertical_displacement (int, optional): the vertical_displacement
            of the plasma (cm). Defaults to 0.
        num_points (int, optional): number of points to described the
            shape. Defaults to 50.
        configuration (str, optional): plasma configuration
            ("non-null", "single-null", "double-null").
            Defaults to "non-null".
        x_point_shift (float, optional): Shift parameters for locating the
            X points in [0, 1]. Defaults to 0.1.
        Others: see paramak.RotateSplineShape() arguments.

    Keyword Args:
        elongation (float): the elongation of the plasma.
        major_radius (int): the major radius of the plasma (cm).
        minor_radius (int): the minor radius of the plasma (cm).
        triangularity (float): the triangularity of the plasma.
        vertical_displacement (int): the vertical_displacement
            of the plasma (cm).
        num_points (int): number of points to described the
            shape.
        configuration (str): plasma configuration
            ("non-null", "single-null", "double-null").
        x_point_shift (float): Shift parameters for locating the
            X points in [0, 1].
        outer_equatorial_point (float, float): coordinates for outer
            equatorial point
        inner_equatorial_point (float, float): coordinates for inner
            equatorial point
        high_point (float, float): coordinates for high point
        low_point (float, float): coordinates for low point
        lower_x_point (float, float): coordinates for lower x point (None
            if doesn't exist)
        upper_x_point (float, float): coordinates for upper x point (None
            if doesn't exist)
        Others: see paramak.RotateSplineShape() attributes.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        elongation=2.0,
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        vertical_displacement=0,
        num_points=50,
        configuration="non-null",
        x_point_shift=0.1,
        name="plasma",
        material_tag="DT_plasma",
        stp_filename="plasma.stp",
        stl_filename="plasma.stl",
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

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
        )

        # properties needed for plasma shapes
        self.elongation = elongation
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.vertical_displacement = vertical_displacement
        self.num_points = num_points
        self.configuration = configuration
        self.x_point_shift = x_point_shift

        self.outer_equatorial_point = None
        self.inner_equatorial_point = None
        self.high_point = None
        self.low_point = None
        self.lower_x_point, self.upper_x_point = self.compute_x_points()

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
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, value):
        if value > 2000 or value < 1:
            raise ValueError("minor_radius is out of range")
        else:
            self._minor_radius = value

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, value):
        if value > 2000 or value < 1:
            raise ValueError("major_radius is out of range")
        else:
            self._major_radius = value

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, value):
        if value > 10 or value < 0:
            raise ValueError("elongation is out of range")
        else:
            self._elongation = value

    def compute_x_points(self):
        """Computes the location of X points based on plasma parameters and
         configuration

        Returns:
            ((float, float), (float, float)): lower and upper x points
             coordinates. None if no x points
        """
        lower_x_point, upper_x_point = None, None  # non-null config
        minor_radius, major_radius = self.minor_radius, self.major_radius
        shift = self.x_point_shift
        elongation = self.elongation
        triangularity = self.triangularity
        if self.configuration == "single-null" or self.configuration == "double-null":
            # no X points for non-null config
            lower_x_point = (1 -
                             (1 +
                              shift) *
                             triangularity *
                             minor_radius, -
                             (1 +
                              shift) *
                             elongation *
                             minor_radius +
                             self.vertical_displacement, )

            if self.configuration == "double-null":
                # upper_x_point is up-down symmetrical
                upper_x_point = (
                    lower_x_point[0],
                    (1 + shift) * elongation * minor_radius
                    + self.vertical_displacement,
                )
        return lower_x_point, upper_x_point

    def find_points(self):
        """Finds the XZ points that describe the 2D profile of the plasma.
        """

        # create array of angles theta
        theta = np.linspace(0, 2 * np.pi, num=self.num_points)

        # parametric equations for plasma
        def R(theta):
            return self.major_radius + self.minor_radius * np.cos(
                theta + self.triangularity * np.sin(theta)
            )

        def Z(theta):
            return (
                self.elongation * self.minor_radius * np.sin(theta)
                + self.vertical_displacement
            )

        # R and Z coordinates
        R_points, Z_points = R(theta), Z(theta)

        # create a 2D array for points coordinates
        points = np.stack((R_points, Z_points), axis=1)

        # set self.points
        self.points = list(points)

        # set the points of interest
        self.high_point = (
            self.major_radius - self.triangularity * self.minor_radius,
            self.elongation * self.minor_radius,
        )
        self.low_point = (
            self.major_radius - self.triangularity * self.minor_radius,
            -self.elongation * self.minor_radius,
        )
        self.outer_equatorial_point = (
            self.major_radius + self.minor_radius, 0)
        self.inner_equatorial_point = (
            self.major_radius - self.minor_radius, 0)
