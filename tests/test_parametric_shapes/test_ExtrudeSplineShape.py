import unittest

import pytest

from paramak import ExtrudeSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates an extruded shape using spline connections and checks that
        the volume is correct"""

        test_shape = ExtrudeSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=30
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 20 * 20 * 30

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using spline
        connections and checks that their relative volumes are correct"""

        test_shape_1 = ExtrudeSplineShape(
            points=[(13, 0), (13, 20), (16, 20), (20, 10), (16, 0)], distance=5
        )
        test_shape_1.azimuth_placement_angle = 0

        # test_shape_2 is test_shape_1 extruded 4 times

        test_shape_2 = ExtrudeSplineShape(
            points=[(13, 0), (13, 20), (16, 20), (20, 10), (16, 0)], distance=5
        )
        test_shape_2.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape_1.volume * \
            4 == pytest.approx(test_shape_2.volume, rel=0.01)

    def test_cut_volume(self):
        """creates an extruded shape using spline connections with another shape cut
        out and checks that the volume is correct"""

        inner_shape = ExtrudeSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], distance=30
        )

        outer_shape = ExtrudeSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], distance=30
        )

        outer_shape_with_cut = ExtrudeSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], cut=inner_shape, distance=30,
        )

        assert inner_shape.volume == pytest.approx(1165, abs=2)
        assert outer_shape.volume == pytest.approx(3775, abs=2)
        assert outer_shape_with_cut.volume == pytest.approx(3775 - 1165, abs=2)

    def test_rotation_angle(self):
        """creates an extruded shape with a rotation_angle < 360 and checks that the
        correct cut is performed and the volume is correct"""

        test_shape = ExtrudeSplineShape(
            points=[(50, 0), (50, 20), (70, 20), (70, 0)],
            distance=50,
            azimuth_placement_angle=[45, 135, 225, 315]
        )
        test_volume = test_shape.volume

        test_shape.rotation_angle = 180

        assert test_shape.volume == pytest.approx(test_volume * 0.5)


if __name__ == "__main__":
    unittest.main()
