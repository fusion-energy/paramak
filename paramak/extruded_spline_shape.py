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


class ExtrudeSplineShape(Shape):
    """Extrude a 3d CadQuery solid from points connected with
       a spline connections

        :param points: A list of XZ coordinates and connection types where the last
            entry has the same XZ coordinates as the first entry. For example [(2.,1.),
            (2.,2.), (1.,2., (1.,1., (2.,1.]
        :type points: a list of tuples each containing X (float), Z (float)
        :param stp_filename: the filename used when saving stp files as part of a reactor
        :type stp_filename: str
        :param color: the color to use when exporting as html graphs or png images
        :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
        3 or 4 floats respectively each in the range 0-1
        :param distance: The extrude distance to use (cm units if used for neutronics)
        :type distance: float
        :param azimuth_placement_angle: the angle or angles to use when rotating the 
        shape on the azimuthal axis
        :type azimuth_placement_angle: float or iterable of floats
        :param cut: An optional cadquery object to perform a boolean cut with this object
        :type cut: cadquery object
        :param material_tag: The material name to use when exporting the neutronics description
        :type material_tag: str
        :param name: The legend name used when exporting a html graph of the shape
        :type name: str
    """

    def __init__(
        self,
        points,
        distance,
        workplane="XZ",
        stp_filename=None,
        solid=None,
        color=None,
        azimuth_placement_angle=0,
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

        self.distance = distance
        self.solid = solid
        self.cut = cut

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, value):
        self._cut = value

    @property
    def solid(self):
        self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    def create_solid(self):
        """Creates a 3d solid using points with spline
           edges, azimuth_placement_angle and distance.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # Creates a cadquery solid from points and extrudes
        solid = (
            cq.Workplane(self.workplane)
            .spline(self.points)
            .close()
            .extrude(distance=-1 * self.distance / 2.0, both=True)
        )

        # Checks if the azimuth_placement_angle is a list of angles
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
            solid = solid.cut(self.cut.solid)

        self.solid = solid

        return solid
