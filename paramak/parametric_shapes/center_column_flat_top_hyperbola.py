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

from paramak import RotateMixedShape


class CenterColumnShieldFlatTopHyperbola(RotateMixedShape):
    def __init__(
        self,
        height,
        arc_height,
        inner_radius,
        mid_radius,
        outer_radius,
        workplane="XZ",
        rotation_angle=360,
        solid=None,
        stp_filename="center_column.stp",
        color=None,
        points=None,
        name="center_column",
        material_tag="center_column_material",
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

        self.height = height
        self.arc_height = arc_height
        self.mid_radius = mid_radius
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            print('hash values are different')
            self.create_solid()
        if self.get_hash() == self.hash_value:
            print('hash values are equal')
        return self._solid

    @solid.setter
    def solid(self, solid):
        self._solid = solid

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def arc_height(self):
        return self._arc_height

    @arc_height.setter
    def arc_height(self, arc_height):
        self._arc_height = arc_height

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius):
        self._inner_radius = inner_radius

    @property
    def mid_radius(self):
        return self._mid_radius

    @mid_radius.setter
    def mid_radius(self, mid_radius):
        self._mid_radius = mid_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius):
        self._outer_radius = outer_radius

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the blanket shape."""

        if self.inner_radius >= self.outer_radius:
            raise ValueError(
                "inner_radius ({}) is larger than outer_radius ({})".format(
                    self.inner_radius, self.outer_radius
                )
            )

        if self.mid_radius >= self.outer_radius:
            raise ValueError(
                "mid_radius ({}) is larger than outer_radius ({})".format(
                    self.mid_radius, self.outer_radius
                )
            )

        if self.arc_height >= self.height:
            raise ValueError(
                "arc_height ({}) is larger than height ({})".format(
                    self.arc_height, self.height
                )
            )

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (self.outer_radius, self.height / 2, "straight"),
            (self.outer_radius, self.arc_height / 2, "spline"),
            (self.mid_radius, 0, "spline"),
            (self.outer_radius, -self.arc_height / 2, "straight"),
            (self.outer_radius, -self.height / 2, "straight"),
            (self.inner_radius, -self.height / 2, "straight"),
            (self.inner_radius, 0),
        ]

        self.points = points
