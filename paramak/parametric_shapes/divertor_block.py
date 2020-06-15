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

import scipy
import math

import numpy as np

from paramak import RotateMixedShape


class DivertorBlock(RotateMixedShape):
    def __init__(
        self,
        major_radius,
        minor_radius,
        triangularity,
        elongation,
        thickness,
        stop_angle,
        offset_from_plasma,
        start_x_value,
        workplane="XZ",
        points=None,
        name=None,
        rotation_angle=360,
        solid=None,
        stp_filename="divertor.stp",
        color=None,
        azimuth_placement_angle=0,
        material_tag=None,
        cut=None,
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
        )

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.elongation = elongation
        self.thickness = thickness
        self.stop_angle = stop_angle
        self.offset_from_plasma = offset_from_plasma
        self.start_x_value = start_x_value

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def solid(self):
        self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, solid):
        self._solid = solid

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, major_radius):
        self._major_radius = major_radius

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, minor_radius):
        self._minor_radius = minor_radius

    @property
    def triangularity(self):
        return self._triangularity

    @triangularity.setter
    def triangularity(self, triangularity):
        self._triangularity = triangularity

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, elongation):
        self._elongation = elongation

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        self._thickness = thickness

    @property
    def stop_angle(self):
        return self._stop_angle

    @stop_angle.setter
    def stop_angle(self, stop_angle):
        self._stop_angle = stop_angle

    @property
    def offset_from_plasma(self):
        return self._offset_from_plasma

    @offset_from_plasma.setter
    def offset_from_plasma(self, offset_from_plasma):
        self._offset_from_plasma = offset_from_plasma

    @property
    def start_x_value(self):
        return self._start_x_value

    @start_x_value.setter
    def start_x_value(self, start_x_value):
        self._start_x_value = start_x_value

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the blanket shape."""

        # This section finds the points on the front face of the divertor
        radius_of_front_curve = (
            0.5
            * scipy.sqrt(
                (
                    self.minor_radius ** 2
                    * ((self.triangularity + 1) ** 2 + self.elongation ** 2) ** 2
                )
                / ((self.triangularity + 1) ** 2)
            )
            + self.offset_from_plasma
        )

        x_position_for_outside_arc = (
            2 * self.major_radius * (1 + self.triangularity)
            - self.minor_radius * (self.triangularity ** 2 + self.elongation ** 2 - 1)
        ) / (2 * (1 + self.triangularity))

        # this is the distance between the x_limit and the x_position_for_outside_arc
        triangle_adjacent = x_position_for_outside_arc - self.start_x_value
        triangle_hyp = radius_of_front_curve

        start_angle = math.acos(triangle_adjacent / triangle_hyp)  # this is in radians
        if self.stop_angle > 180:
            start_angle = math.radians(360) - start_angle

        # stop angle is converted from degrees to radians
        angles = np.linspace(
            min(start_angle, math.radians(self.stop_angle)),
            max(start_angle, math.radians(self.stop_angle)),
            10,
        )

        xs = -(radius_of_front_curve * scipy.cos(angles) - x_position_for_outside_arc)
        zs = radius_of_front_curve * scipy.sin(angles)

        points = []
        connections = []
        for x, z, in zip(xs, zs):
            points.append([x, z, "spline"])

        points[-1][-1] = "straight"

        # This section finds the points on the rear face of the divertor
        radius_of_back_curve = radius_of_front_curve + self.thickness

        # this is the distnace between the x_limit and the x_position_for_outside_arc
        triangle_hyp = radius_of_back_curve
        print("triangle_adjacent/triangle_hyp", triangle_adjacent, triangle_hyp)
        start_angle = math.acos(triangle_adjacent / triangle_hyp)
        if self.stop_angle > 180:
            start_angle = math.radians(360) - start_angle

        # stop angle is converted from degrees to radians
        angles = np.linspace(
            min(start_angle, math.radians(self.stop_angle)),
            max(start_angle, math.radians(self.stop_angle)),
            10,
        )
        # angles = np.linspace(start_angle,math.radians(self.stop_angle),100)

        xs = -(radius_of_back_curve * scipy.cos(angles) - x_position_for_outside_arc)
        zs = radius_of_back_curve * scipy.sin(angles)

        for x, z, in zip(reversed(xs), reversed(zs)):
            points.append([x, z, "spline"])

        # changes the last point to a straght conenctor
        points[-1][-1] = "straight"

        self.points = points
