"""
This file is part of PARAMAK which is a design tool capable
of creating 3D CAD models compatible with automated neutronics
analysis.

PARAMAK is released under GNU General Public License v3.0.
Go to https://github.com/ukaea/paramak/blob/master/LICENSE
for full license details.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Copyright (C) 2019  UKAEA

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""
import math
from pathlib import Path

import numpy as np
import scipy

from paramak import RotateSplineShape


class PlasmaShape(RotateSplineShape):
    """Creates a tokamak plasma shape that is controlled by 4 shaping parameters.

    :param major_radius: the major radius of the plasma (cm)
    :type major_radius: float
    :param minor_radius: the minor radius of the plasma (cm)
    :type minor_radius: float
    :param triangularity: the triangularity of the plasma
    :type triangularity: float
    :param elongation: the elongation of the plasma
    :type elongation: float

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        points=None,
        name=None,
        material_tag=None,
        workplane="XZ",
        elongation=2.0,
        major_radius=450,
        minor_radius=150,
        single_null=True,
        triangularity=0.55,
        solid=None,
        stp_filename="plasma.stp",
        color=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        cut=None,
        hash_value=None,
    ):

        super().__init__(
            points,
            workplane,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            solid,
            rotation_angle,
            cut,
            hash_value,
        )

        # properties needed for plasma shapes
        self.elongation = elongation
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.single_null = single_null
        self.triangularity = triangularity
        self.azimuth_placement_angle = azimuth_placement_angle
        self.rotation_angle = rotation_angle
        self.color = color
        self.solid = solid
        self.points = points
        self.stp_filename = stp_filename

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            print('hash values are different')
            self.create_solid()
        if self.get_hash() == self.hash_value:
            print('hash values are equal')
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

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
    def single_null(self):
        return self._single_null

    @single_null.setter
    def single_null(self, single_null):
        if type(single_null) != bool:
            raise ValueError("single_null must be True or False")
        else:
            self._single_null = single_null

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

    def find_inside_and_outside_arc_positions(self):
        """Finds the X axis value of the center point of the two arcs that make
        up the plasma.

        :return: the X postion of the ouside arc and the X position of the inside arc
        :rtype: floats
        """
        # x position of outside arc
        x_position_for_outside_arc = (
            2 * self.major_radius * (1 + self.triangularity)
            - self.minor_radius * (self.triangularity ** 2 + self.elongation ** 2 - 1)
        ) / (2 * (1 + self.triangularity))

        # x position of inside arc
        x_position_for_inside_arc = (
            2 * self.major_radius * (self.triangularity - 1)
            - self.minor_radius * (self.triangularity ** 2 + self.elongation ** 2 - 1)
        ) / (2 * (self.triangularity - 1))

        self.x_position_for_outside_arc = x_position_for_outside_arc
        self.x_position_for_inside_arc = x_position_for_inside_arc

        return x_position_for_outside_arc, x_position_for_inside_arc

    def find_inside_outside_radius(self):
        """Finds the radius of the the two arcs used to create the plasma surfaces.

        :return: the radius of the ouside arc and the radius of the inside arc
        :rtype: floats
        """

        # Radius of outside arc
        radius_of_outside_arc = 0.5 * scipy.sqrt(
            (
                self.minor_radius ** 2
                * ((self.triangularity + 1) ** 2 + self.elongation ** 2) ** 2
            )
            / ((self.triangularity + 1) ** 2)
        )
        # Radius of inside arc
        radius_of_inside_arc = 0.5 * scipy.sqrt(
            (
                self.minor_radius ** 2
                * ((self.triangularity - 1) ** 2 + self.elongation ** 2) ** 2
            )
            / ((self.triangularity - 1) ** 2)
        )

        self.radius_of_outside_arc = radius_of_outside_arc
        self.radius_of_inside_arc = radius_of_inside_arc

        return radius_of_outside_arc, radius_of_inside_arc

    def find_x_point(self):
        """Finds the point on the X axis where the inner arc and outer arc meet

        :return: the X value of the intersection
        :rtype: float
        """

        # uses the cosin rule with the inner angle set to C

        width_of_base = self.x_position_for_inside_arc - self.x_position_for_outside_arc

        angle_of_C = math.acos(
            (
                (
                    math.pow(self.radius_of_inside_arc, 2)
                    - (
                        math.pow(self.radius_of_outside_arc, 2)
                        + math.pow(width_of_base, 2)
                    )
                )
                / -(2 * self.radius_of_outside_arc * width_of_base)
            )
        )

        partial_width_of_base = math.cos(angle_of_C) * self.radius_of_outside_arc

        x_point = self.x_position_for_outside_arc + partial_width_of_base

        self.x_point = x_point

        return x_point

    def find_points_on_outer_arc(self):
        """Finds the XZ points on the outer arc of the plasma

        :return: the XZ points that make up the outer arc
        :rtype: float
        """

        intercept_angle = math.acos(
            (
                (-self.x_point + self.x_position_for_outside_arc)
                / self.radius_of_outside_arc
            )
        )

        angles = np.linspace(
            intercept_angle, 2 * math.pi - intercept_angle, 50, endpoint=False
        )

        xs = -(
            self.radius_of_outside_arc * scipy.cos(angles)
            - self.x_position_for_outside_arc
        )
        zs = self.radius_of_outside_arc * scipy.sin(angles)

        self.xs_outer_arc = xs
        self.zs_outer_arc = zs

        return xs, zs

    def find_points_on_inner_arc(self):
        """Finds the XZ points on the inner arc of the plasma

        :return: the XZ points that make up the inner arc
        :rtype: float
        """

        intercept_angle = math.acos(
            (
                (-self.x_point + self.x_position_for_inside_arc)
                / self.radius_of_inside_arc
            )
        )

        lower_angles = np.linspace(
            2 * math.pi - intercept_angle, math.radians(360), 25, endpoint=False
        )
        upper_angles = np.linspace(math.radians(0), intercept_angle, 25)
        angles = np.concatenate((lower_angles, upper_angles), axis=0)

        xs = -(
            self.radius_of_inside_arc * scipy.cos(angles)
            - self.x_position_for_inside_arc
        )
        zs = self.radius_of_inside_arc * scipy.sin(angles)

        self.xs_inner_arc = xs
        self.zs_inner_arc = zs

        return xs, zs

    def find_points(self):
        """Finds the XZ points that describe the 2D profile of the blanket shape.

        :return: the XZ points that make up the outer arc
        :rtype: list of tuples each with two floats
        """

        self.find_inside_and_outside_arc_positions()

        self.find_inside_outside_radius()

        self.find_x_point()

        self.find_points_on_outer_arc()

        self.find_points_on_inner_arc()

        points = []

        for x, z, in zip(self.xs_outer_arc, self.zs_outer_arc):
            points.append([x, z])

        for x, z, in zip(self.xs_inner_arc, self.zs_inner_arc):
            points.append([x, z])

        # points.append([self.xs_outer_arc[0], self.zs_outer_arc[0]])

        self.points = points

        return points
