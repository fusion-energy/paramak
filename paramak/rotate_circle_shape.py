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

from collections import Iterable

import cadquery as cq

from paramak import Shape


class RotateCircleShape(Shape):
    """Rotates a circular 3d CadQuery solid from a central point and a radius

       :param points: A list of a single XZ coordinate which is the central
            point of the circle. For example, [(10, 10)]
       :type points: a list of tuples each containing X (float), Z (float)
       :param radius: The radius of the circle
       :type radius: float
       :param name: The legend name used when exporting a html graph of the shape
       :type name: str
       :param color: the color to use when exporting as html graphs or png images
       :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
            3 or 4 floats respectively each in the range 0-1
       :param material_tag: The material name to use when exporting the neutronics description
       :type material_tag: str
       :param stp_filename: the filename used when saving stp files as part of a reactor
       :type stp_filename: str
       :param azimuth_placement_angle: the angle or angles to use when rotating the 
            shape on the azimuthal axis
       :type azimuth_placement_angle: float or iterable of floats
       :param rotation_angle: The rotation_angle to use when revoling the solid (degrees)
       :type rotation_angle: float
       :param cut: An optional cadquery object to perform a boolean cut with this object
       :type cut: cadquery object
    """

    def __init__(
        self,
        points,
        radius,
        workplane="XZ",
        stp_filename=None,
        solid=None,
        color=None,
        azimuth_placement_angle=0,
        rotation_angle=360,
        cut=None,
        material_tag=None,
        name=None,
    ):

        super().__init__(
            points,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            workplane,
        )

        self.radius = radius
        self.solid = solid
        self.rotation_angle = rotation_angle
        self.cut = cut

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, value):
        self._cut = value

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    @property
    def solid(self):
        self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    def create_solid(self):
        """Creates a 3d solid using points, radius, azimuth_placement_angle and
        rotation_angle.
        
        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        solid = (
            cq.Workplane(self.workplane)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
            # .close()
            .revolve(self.rotation_angle)
        )

        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(solid.rotate((0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate((0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            # Allows for multiple cuts to be applied
            if isinstance(self.cut, Iterable):
                for cutting_solid in self.cut:
                    solid = solid.cut(cutting_solid.solid)
            else:
                solid = solid.cut(self.cut.solid)

        self.solid = solid

        return solid
