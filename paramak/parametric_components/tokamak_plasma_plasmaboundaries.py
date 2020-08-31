import math
from pathlib import Path

import numpy as np
import scipy
from plasmaboundaries import get_separatrix_coordinates

from paramak import Plasma


class PlasmaBoundaries(Plasma):
    """Creates a double null tokamak plasma shape that is controlled
       by 5 shaping parameters using the plasmaboundaries package to calculate
       points. For more details see:
       http://github.com/RemiTheWarrior/plasma-boundaries
        Args:
            A (float, optional): plasma parameter see plasmaboundaries doc.
                Defaults to 0.05.
            elongation (float, optional): the elongation of the plasma.
                Defaults to 2.0.
            major_radius (float, optional): the major radius of the plasma (cm).
                Defaults to 450.
            minor_radius (float, optional): the minor radius of the plasma (cm).
                Defaults to 150.
            triangularity (float, optional): the triangularity of the plasma.
                Defaults to 0.55.
            vertical_displacement (float, optional): the vertical_displacement
                of the plasma (cm). Defaults to 0.
            num_points (int, optional): number of points to described the
                shape. Defaults to 50.
            configuration (str, optional): plasma configuration
                ("non-null", "single-null", "double-null").
                Defaults to "non-null".
            x_point_shift (float, optional): Shift parameters for locating the
                X points in [0, 1]. Defaults to 0.1.
            Others: see paramak.RotateSplineShape() arguments.

        Attributes:
            A: plasma parameter see plasmaboundaries doc.
            Others: see paramak.RotateSplineShape() and paramak.Plasma()
                attributes.
    """

    def __init__(
        self,
        A=0.05,
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
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
        )

        # properties needed for plasma shapes
        self.A = A
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

    def find_points(self):
        """Finds the XZ points that describe the 2D profile of the plasma.
        """
        aspect_ratio = self.minor_radius / self.major_radius
        params = {
            "A": self.A,
            "aspect_ratio": aspect_ratio,
            "elongation": self.elongation,
            "triangularity": self.triangularity,
        }
        points = get_separatrix_coordinates(params, self.configuration)
        # add vertical displacement
        points[:, 1] += self.vertical_displacement
        # rescale to cm
        points[:] *= self.major_radius

        # remove unnecessary points
        lower_x_point, upper_x_point = self.compute_x_points()
        # if non-null these are the y bounds
        lower_point_y = (
            -self.elongation * self.minor_radius + self.vertical_displacement
        )
        upper_point_y = self.elongation * self.minor_radius + self.vertical_displacement
        # else use x points
        if self.configuration == "single-null" or self.configuration == "double-null":
            lower_point_y = lower_x_point[1]
            if self.configuration == "double-null":
                upper_point_y = upper_x_point[1]
        points2 = []
        for p in points:
            if p[1] >= lower_point_y and p[1] <= upper_point_y:
                points2.append(p)
        points = points2

        self.points = points

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
