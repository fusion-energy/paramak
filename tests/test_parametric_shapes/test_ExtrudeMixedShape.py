import unittest

import pytest

from paramak import ExtrudeMixedShape
import os
from pathlib import Path


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates an extruded shape at one placement angle using straight
        and spline connections and checks the volume is correct"""

        test_shape = ExtrudeMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "straight"),
                (20, 20, "spline"),
                (20, 0, "spline"),
            ],
            distance=30,
        )

        assert test_shape.solid is not None
        print(test_shape.volume)
        assert test_shape.volume >= 20 * 20 * 30

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using
        straight and spline connections and checks their relative volumes are
        correct"""

        test_shape_1 = ExtrudeMixedShape(
            points=[
                (5, 0, "straight"),
                (5, 20, "straight"),
                (10, 20, "spline"),
                (20, 10, "spline"),
                (10, 0, "straight"),
            ],
            distance=10,
        )

        test_shape_1.azimuth_placement_angle = 0

        test_shape_2 = ExtrudeMixedShape(
            points=[
                (5, 0, "straight"),
                (5, 20, "straight"),
                (10, 20, "spline"),
                (20, 10, "spline"),
                (10, 0, "straight"),
            ],
            distance=10,
        )
        test_shape_2.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape_1.volume * 4 == pytest.approx(test_shape_2.volume)

    def test_cut_volume(self):
        """creates an extruded shape using straight and spline connections with
        another shape cut out and checks that the volume is correct"""

        inner_shape = ExtrudeMixedShape(
            points=[
                (5, 5, "straight"),
                (5, 10, "spline"),
                (10, 10, "spline"),
                (10, 5, "spline"),
            ],
            distance=30,
        )

        outer_shape = ExtrudeMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            distance=30,
        )

        outer_shape_with_cut = ExtrudeMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            cut=inner_shape,
            distance=30,
        )

        assert inner_shape.volume == pytest.approx(1068, abs=2)
        assert outer_shape.volume == pytest.approx(3462, abs=2)
        assert outer_shape_with_cut.volume == pytest.approx(3462 - 1068, abs=2)

    def test_mixed_shape_with_straight_and_circle(self):
        """checks that an ExtrudeMixedShape can be created with a combination of straight and
        circular connections"""

        test_shape = ExtrudeMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (22, 15, "circle"),
                (20, 20, "straight"),
            ],
            distance=10,
        )
        assert test_shape.volume > 10 * 10 * 10

    def test_export_stp(self):
        """creates an ExtrudeMixedShape and checks that an stp file of the shape can be exported
        using the export_stp method"""

        test_shape = ExtrudeMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (22, 15, "circle"),
                (20, 20, "straight"),
            ],
            distance=10,
        )
        os.system("rm tests/test.stp")
        test_shape.export_stp("tests/test.stp")
        assert Path("tests/test.stp").exists() is True
        os.system("rm tests/test.stp")

        test_shape.stp_filename = "tests/test.stp"
        test_shape.export_stp()
        assert Path("tests/test.stp").exists() is True
        os.system("rm tests/test.stp")

    def test_export_stl(self):
        """creates an ExtrudeMixedShape and checks that an stl file of the shape can be exported
        using the export_stl method"""

        test_shape = ExtrudeMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (22, 15, "circle"),
                (20, 20, "straight"),
            ],
            distance=10,
        )
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test.stl")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")

    def test_rotation_angle(self):
        """creates an extruded shape with a rotation_angle < 360 and checks that the
        correct cut is performed and the volume is correct"""

        test_shape = ExtrudeMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (22, 15, "circle"),
                (20, 20, "straight"),
            ],
            distance=10,
            azimuth_placement_angle=[45, 135, 225, 315]
        )
        test_volume = test_shape.volume

        test_shape.rotation_angle = 180

        assert test_shape.volume == pytest.approx(test_volume * 0.5)


if __name__ == "__main__":
    unittest.main()
