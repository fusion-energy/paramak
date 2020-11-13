import os
import unittest
from pathlib import Path

import pytest

from paramak import RotateMixedShape


class test_object_properties(unittest.TestCase):

    def setUp(self):
        self.test_shape = RotateMixedShape(
            points=[(50, 0, "straight"), (50, 50, "spline"), (60, 70, "spline"),
                (70, 50, "circle"), (60, 25, "circle"), (70, 0, "straight")]
        )
    
    def test_default_parameters(self):
        """Checks that the default parameters of a RotateMixedShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "RotateMixedShape.stp"
        assert self.test_shape.stl_filename == "RotateMixedShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0

    def test_relative_shape_volume_rotation_angle(self):
        """Creates two RotateMixedShapes with different rotation_angles and checks
        that their relative volumes are correct."""

        assert self.test_shape.volume > 100
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert test_volume == pytest.approx(self.test_shape.volume * 2)

    def test_relative_shape_volume_azimuth_placement_angle(self):
        """Creates two RotateMixedShapes with different azimuth_placement_angles and
        checks that their relative volumes are correct."""

        self.test_shape.rotation_angle = 10
        self.test_shape.azimuth_placement_angle = 0
        test_volume_1 = self.test_shape.volume

        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert self.test_shape.volume == pytest.approx(test_volume_1 * 4)
        
    def test_shape_face_areas(self):
        """Creates RotateMixedShapes and checks that the face areas are expected."""

        assert len(self.test_shape.areas) == 4
        assert len(set(self.test_shape.areas)) == 4

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 5

    # here
    def test_union_volume_addition(self):
        """Fuses two RotateMixedShapes and checks that their fused volume
        is correct."""

        inner_box = RotateMixedShape(
            points=[
                (100, 100, "straight"),
                (100, 200, "straight"),
                (200, 200, "straight"),
                (200, 100, "straight"),
            ],
            rotation_angle=20,
        )

        outer_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ],
            rotation_angle=20,
        )

        outer_box_and_inner_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ],
            rotation_angle=20,
            union=inner_box,
        )

        assert inner_box.volume + outer_box.volume == pytest.approx(
            outer_box_and_inner_box.volume
        )

    def test_incorrect_connections(self):
        """Creates rotated straight shapes to check errors are correctly raised
        when specifying connections."""

        def incorrect_string_for_connection_type():
            """Checks ValueError is raised when an invalid connection type is
            specified."""

            RotateMixedShape(
                points=[
                    (0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    (20, 0, "not_a_valid_entry"),
                ]
            )

        self.assertRaises(ValueError, incorrect_string_for_connection_type)

        def incorrect_number_of_connections_function():
            """Checks ValueError is raised when an incorrect number of
            connections is specified."""

            test_shape = RotateMixedShape(
                points=[(0, 200, "straight"), (200, 100), (0, 0, "spline"), ]
            )

            test_shape.create_solid()

        self.assertRaises(ValueError, incorrect_number_of_connections_function)

    def test_cut_volume(self):
        """Creates a rotated shape using mixed connections with another shape
        cut out and checks that the volume is correct."""

        inner_shape = RotateMixedShape(
            points=[
                (5, 5, "straight"),
                (5, 10, "spline"),
                (10, 10, "spline"),
                (10, 5, "spline"),
            ],
            rotation_angle=180,
        )

        outer_shape = RotateMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            rotation_angle=180,
        )

        outer_shape_cut = RotateMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(862.5354)
        assert outer_shape.volume == pytest.approx(2854.5969)
        assert outer_shape_cut.volume == pytest.approx(2854.5969 - 862.5354)

    def test_mixed_shape_with_straight_and_circle(self):
        """Creates a rotated shape with straight and circular connections and
        checks the volume is correct."""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
        )
        assert test_shape.volume > 10 * 10

    def test_export_stp(self):
        """Creates a RotateMixedShape and checks that a stp file of the shape
        can be exported using the export_stp method."""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
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
        """Creates a RotateMixedShape and checks that a stl file of the shape
        can be exported using the export_stl method."""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
        )
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test.stl")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")


if __name__ == "__main__":
    unittest.main()
