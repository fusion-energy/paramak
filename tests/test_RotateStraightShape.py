"""
This file is part of PARAMAK which is a design tool capable
of creating 3D CAD models compatible with automated neutronics
analysis.

PARAMAK is released under GNU General Public License v3.0.
Go to https://github.com/Shimwell/paramak/blob/master/LICENSE
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

import os
import unittest
from pathlib import Path

import pytest

from paramak import RotateStraightShape


class test_object_properties(unittest.TestCase):
    def test_shape_rotation_angle_default(self):
        """"checks that the default rotation angle for a RotateStraightShape \
                is 360 degrees"""

        test_shape = RotateStraightShape(points=None)
        assert test_shape.rotation_angle == 360

    def test_shape_rotation_angle_setting_getting(self):
        """checks that the rotation angle for a RotateStraightShape \
                can be set"""
        test_shape = RotateStraightShape(points=None)
        test_shape.rotation_angle = 180
        assert test_shape.rotation_angle == 180
        test_shape.rotation_angle = 90
        assert test_shape.rotation_angle == 90

    def test_shape_azimuth_placement_angle_default(self):
        """checks that the default azimuth placement angle for a RotateStraightShape \
                is 0"""

        test_shape = RotateStraightShape(points=None)
        assert test_shape.azimuth_placement_angle == 0

    def test_shape_azimuth_placement_angle_setting_getting(self):
        """checks that the default azimuth placement angle for a RotateStraightShape \
                can be set to single values or to a list of values"""

        test_shape = RotateStraightShape(points=None)
        test_shape.azimuth_placement_angle = 180
        assert test_shape.azimuth_placement_angle == 180
        test_shape.azimuth_placement_angle = 90
        assert test_shape.azimuth_placement_angle == 90
        test_shape.azimuth_placement_angle = [0, 90, 180, 360]
        assert test_shape.azimuth_placement_angle == [0, 90, 180, 360]

    def test_absolute_shape_volume(self):
        """creates a rotated shape using straight connections and checks that the \
                volume is correct"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(3.141592654 * 20 * 20 * 20)

    def test_relative_shape_volume(self):
        """creates a rotated shape using straight connections and checks the volume \
                is half the volume of a shape which is double its size"""

        test_shape_1 = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape_1.rotation_angle = 180
        test_shape_1.create_solid()

        test_shape_2 = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape_2.rotation_angle = 360
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(test_shape_2.volume * 0.5)

    def test_export_stp(self):
        """checks that export_stp() exports stp files with the correct suffix"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape.rotation_angle = 360
        os.system("rm filename.stp filename.step")
        test_shape.export_stp("filename.stp")
        test_shape.export_stp("filename.step")
        assert Path("filename.stp").exists() is True
        assert Path("filename.step").exists() is True
        os.system("rm filename.stp filename.step")
        test_shape.export_stp("filename")
        assert Path("filename.stp").exists() is True
        os.system("rm filename.stp")

    def test_export_stl(self):
        """checks that export_stl() exports stl files with the correct suffix"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape.rotation_angle = 360
        os.system("rm filename.stl")
        test_shape.export_stl("filename")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")
        test_shape.export_stl("filename.stl")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")

    def test_export_svg(self):
        """checks that export_svg() exports svg files with the correct suffix"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape.rotation_angle = 360
        os.system("rm filename.svg")
        test_shape.export_svg("filename")
        assert Path("filename.svg").exists() is True
        os.system("rm filename.svg")
        test_shape.export_svg("filename.svg")
        assert Path("filename.svg").exists() is True
        os.system("rm filename.svg")

    def test_cut_volume(self):
        """creates a rotated shape from straight connections with another shape \
                cut out and checks the volume is correct"""

        inner_shape = RotateStraightShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], rotation_angle=180
        )

        outer_shape = RotateStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(589.048622)
        assert outer_shape.volume == pytest.approx(1908.517537)
        assert outer_shape_with_cut.volume == pytest.approx(1908.517537 - 589.048622)


if __name__ == "__main__":
    unittest.main()
