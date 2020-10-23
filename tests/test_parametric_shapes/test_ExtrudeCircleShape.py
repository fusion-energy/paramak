import math
import unittest

import pytest

from paramak import ExtrudeCircleShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates extruded shapes using circles and checks the volumes are correct"""

        test_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(math.pi * 10 ** 2 * 20)

        test_shape2 = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=10
        )

        test_shape2.create_solid()

        assert test_shape2.solid is not None
        assert 2 * test_shape2.volume == pytest.approx(test_shape.volume)

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using
        circles and checks their relative volumes are correct"""

        test_shape1 = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20, azimuth_placement_angle=0
        )

        test_shape2 = ExtrudeCircleShape(
            points=[(30, 0)],
            radius=10,
            distance=20,
            azimuth_placement_angle=[0, 90, 180, 270],
        )

        assert test_shape1.volume * 4 == pytest.approx(test_shape2.volume)

    def test_cut_volume(self):
        """creates an extruded shape using circles with another shape cut out and
        checks that the volume is correct"""

        inner_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=20
        )

        outer_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20
        )

        outer_shape_with_cut = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20, cut=inner_shape
        )

        assert inner_shape.volume == pytest.approx(math.pi * 5 ** 2 * 20)
        assert outer_shape.volume == pytest.approx(math.pi * 10 ** 2 * 20)
        assert outer_shape_with_cut.volume == pytest.approx(
            (math.pi * 10 ** 2 * 20) - (math.pi * 5 ** 2 * 20)
        )

    def test_rotation_angle(self):
        """creates an extruded shape with a rotation_angle < 360 and checks that the
        correct cut is performed and the volume is correct"""

        test_shape = ExtrudeCircleShape(
            points=[(50, 0)],
            radius=10,
            distance=10,
            azimuth_placement_angle=[45, 135, 225, 315]
        )
        test_volume = test_shape.volume

        test_shape.rotation_angle = 180

        assert test_shape.volume == pytest.approx(test_volume * 0.5)


if __name__ == "__main__":
    unittest.main()
