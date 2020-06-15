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

from paramak import ExtrudeSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates an extruded shape with one placement angle using spline \
                connections and checks the volume is correct"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=30
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 20 * 20 * 30

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes with different placement angles using spline \
                connections and checks their relative volumes are correct"""

        test_shape_1 = ExtrudeSplineShape(
            points=[(13, 0), (13, 20), (16, 20), (20, 10), (16, 0)], distance=5
        )
        test_shape_1.azimuth_placement_angle = 0

        # test_shape_2 is test_shape_1 extruded 4 times

        test_shape_2 = ExtrudeSplineShape(
            points=[(13, 0), (13, 20), (16, 20), (20, 10), (16, 0)], distance=5
        )
        test_shape_2.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape_1.volume * 4 == pytest.approx(test_shape_2.volume, rel=0.01)

    def test_cut_volume(self):
        """creates an extruded shape with one placement angle using spline \
                connections with another shape cut out and checks the volume \
                is correct"""

        inner_shape = ExtrudeSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], distance=30
        )

        outer_shape = ExtrudeSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], distance=30
        )

        outer_shape_with_cut = ExtrudeSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            distance=30,
        )

        assert inner_shape.volume == pytest.approx(1068, abs=2)
        assert outer_shape.volume == pytest.approx(3462, abs=2)
        assert outer_shape_with_cut.volume == pytest.approx(
            3462 - 1068, abs=2
        )

    def test_initial_solid_construction(self):
        """tests that a cadquery solid with a unique hash is constructed when .solid is called"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)],
            distance=20
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """tests that the same cadquery solid with the same unique hash is returned when shape.solid is called again when no changes have been made to the shape"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """tests that a new cadquery solid with a new unique hash is constructed when .solid is called again after changes have been made to the shape"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (0, 0)],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """tests that the hash_value of the shape is not updated until a new solid has been created"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (0, 0)],
            distance=20
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
