import unittest

import pytest

from paramak import ExtrudeStraightShape


class test_object_properties(unittest.TestCase):
    def test_intersect_volume_2_shapes(self):
        """creates two extruded shapes using straight connections with the second shape
        intersecting the first and checks that the volume is correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=30
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=test_shape1,
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25)

    def test_intersect_volume_3_shapes(self):
        """creates three extruded shapes using straight connections with the second and
        third shapes intersecting the first and checks that the volume is correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=30
        )
        test_shape2 = ExtrudeStraightShape(
            points=[(0, 15), (0, 30), (30, 30), (30, 15)], distance=30
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=[test_shape1, test_shape2],
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25 * 0.5)

    def test_intersect_volume_3_extruded_shapes(self):
        """creates three different extruded shapes using straight connections with the
        second and third shapes intersecting the first and checks that the volume is
        correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=10
        )
        test_shape2 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=3
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=[test_shape1, test_shape2],
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25 * 0.1)

    def test_absolute_shape_volume(self):
        """creates an extruded shape at one placement angle using straight connections
        and checks that the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=30
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30)

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using straight
        connections and checks that their relative volumes are correct"""

        test_shape = ExtrudeStraightShape(
            points=[(5, 0), (5, 20), (15, 20), (15, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = 0

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 1)

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 4)

    def test_extruded_shape_with_overlap_volume(self):
        """creates two overlapping extruded shapes at different placement angles using
        straight connections and checks that their volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (10, 20), (10, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(
            (10 * 20 * 10 * 4) - (5 * 20 * 5 * 4))

    def test_cut_volume(self):
        """creates an extruded shape using straight connections with another shape cut
        out and checks that the volume is correct"""

        inner_shape = ExtrudeStraightShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], distance=30
        )

        outer_shape = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], distance=30
        )

        outer_shape_with_cut = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], cut=inner_shape, distance=30,
        )

        assert inner_shape.volume == pytest.approx(5 * 5 * 30)
        assert outer_shape.volume == pytest.approx(9 * 9 * 30)
        assert outer_shape_with_cut.volume == pytest.approx(
            (9 * 9 * 30) - (5 * 5 * 30), abs=0.1
        )

    def test_rotation_angle(self):
        """creates an extruded shape with a rotation_angle < 360 and checks that the
        correct cut is performed and the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(50, 0), (50, 20), (70, 20), (70, 0)],
            distance=50,
            azimuth_placement_angle=[0, 45, 90, 135, 180, 225, 270, 315, 360]
        )
        test_volume = test_shape.volume

        test_shape.rotation_angle = 180

        assert test_shape.volume == pytest.approx(test_volume * 0.5)


if __name__ == "__main__":
    unittest.main()
