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

import unittest

import pytest

from paramak import RotateSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates a rotated shape using spline connections and checks \
                the volume is correct"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
        )

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 100

    def test_cut_volume(self):
        """creates a rotated shape using spline connections with another shape \
                cut out and checks the volume is correct"""

        inner_shape = RotateSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5), (5, 5)], rotation_angle=180
        )

        outer_shape = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3), (3, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3), (3, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(900.8867073)
        assert outer_shape.volume == pytest.approx(2881.75624)
        assert outer_shape_with_cut.volume == pytest.approx(
            2881.75624 - 900.8867073, abs=0.1
        )


if __name__ == "__main__":
    unittest.main()
