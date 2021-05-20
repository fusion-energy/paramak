
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateMixedShape


class TestRotateMixedShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = RotateMixedShape(
            points=[(50, 0, "straight"), (50, 50, "spline"), (60, 70, "spline"),
                    (70, 50, "circle"), (60, 25, "circle"), (70, 0, "straight")]
        )

        self.test_shape_2 = RotateMixedShape(
            rotation_angle=1,
            points=[
                (100, 0, "straight"),
                (200, 0, "circle"),
                (250, 50, "circle"),
                (200, 100, "straight"),
                (150, 100, "straight"),
                (140, 75, "straight"),
                (110, 45, "straight"),
            ]
        )

        self.test_shape_3 = RotateMixedShape(
            rotation_angle=180,
            points=[
                (100, 0, "straight"),
                (200, 0, "circle"),
                (250, 50, "circle"),
                (200, 100, "straight"),
                (150, 100, "straight"),
                (140, 75, "circle"),
                (110, 45, "circle"),
            ]
        )

    def test_export_2d_image(self):
        """Creates a RotateMixedShape object and checks that a png file of the
        object with the correct suffix can be exported using the
        export_2d_image method."""

        os.system("rm filename.png")
        self.test_shape.export_2d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        self.test_shape.export_2d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")

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

    def test_union_volume_addition(self):
        """Fuses two RotateMixedShapes and checks that their fused volume
        is correct"""

        inner_box = RotateMixedShape(
            points=[
                (100, 100, "straight"),
                (100, 200, "straight"),
                (200, 200, "straight"),
                (200, 100, "straight"),
            ]
        )

        outer_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ]
        )

        outer_box_and_inner_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ],
            union=inner_box,
        )

        assert inner_box.volume + outer_box.volume == pytest.approx(
            outer_box_and_inner_box.volume
        )

    def test_incorrect_connections(self):
        """Checks that errors are raised when invalid connection arguments are
        used to construct a RotateMixedShape."""

        def incorrect_string_for_connection_type():
            """Checks ValueError is raised when an invalid connection type is
            specified."""

            RotateMixedShape(
                points=[
                    (0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    (20, 0, "invalid_entry"),
                ]
            )

        self.assertRaises(ValueError, incorrect_string_for_connection_type)

        def incorrect_number_of_connections_function():
            """Checks ValueError is raised when an incorrect number of
            connections is specified."""

            RotateMixedShape(
                points=[(0, 200, "straight"), (200, 100), (0, 0, "spline")]
            )

        self.assertRaises(ValueError, incorrect_number_of_connections_function)

    def test_cut_volume(self):
        """Creates a RotateMixedShape with another RotateMixedShape cut out and
        checks that the volume is correct."""

        outer_shape = RotateMixedShape(
            points=[
                (40, -10, "spline"),
                (35, 50, "spline"),
                (60, 80, "straight"),
                (80, 80, "circle"),
                (100, 40, "circle"),
                (80, 0, "straight"),
                (80, -10, "straight")
            ]
        )
        outer_shape_volume = outer_shape.volume
        outer_shape.cut = self.test_shape
        assert outer_shape.volume == pytest.approx(
            outer_shape_volume - self.test_shape.volume
        )

    def test_mixed_shape_with_straight_and_circle(self):
        """Creates a RotateMixedShape with straight and circular connections and
        checks that the volume is correct."""

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

    def test_export_stp_extension(self):
        """Creates a RotateMixedShape and checks that a stp file of the shape
        can be exported with the correct suffix using the export_stp method."""

        os.system("rm filename.stp filename.step")
        self.test_shape.export_stp("filename.stp")
        self.test_shape.export_stp("filename.step")
        assert Path("filename.stp").exists() is True
        assert Path("filename.step").exists() is True
        os.system("rm filename.stp filename.step")
        self.test_shape.export_stp("filename")
        assert Path("filename.stp").exists() is True
        os.system("rm filename.stp")

    def test_export_stl(self):
        """Creates a RotateMixedShape and checks that a stl file of the shape
        can be exported with the correct suffix using the export_stl method."""

        os.system("rm filename.stl")
        self.test_shape.export_stl("filename.stl")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")
        self.test_shape.export_stl("filename")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")

    def test_export_stp(self):
        """Exports and stp file with mode = solid and wire and checks
        that the outputs exist and relative file sizes are correct."""

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")

        self.test_shape.export_stp('test_solid.stp', mode='solid')
        self.test_shape.export_stp('test_solid2.stp')
        self.test_shape.export_stp('test_wire.stp', mode='wire')

        assert Path("test_solid.stp").exists() is True
        assert Path("test_solid2.stp").exists() is True
        assert Path("test_wire.stp").exists() is True

        assert Path("test_solid.stp").stat().st_size == \
            Path("test_solid2.stp").stat().st_size
        assert Path("test_wire.stp").stat().st_size < \
            Path("test_solid2.stp").stat().st_size

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")

    def test_convert_all_circle_points_change_to_splines(self):
        """creates a RotateMixedShape with two circular edges and converts
        them to spline edges. Checks the new edges have been correctly
        replaced with splines"""

        assert len(self.test_shape_3.points) == 8
        self.test_shape_3.convert_all_circle_connections_to_splines()
        assert len(self.test_shape_3.points) > 8
        assert self.test_shape_3.points[0] == (100, 0, "straight")
        assert self.test_shape_3.points[1][2] == 'spline'
        assert self.test_shape_3.points[2][2] == 'spline'

        # last point is the same as the first point
        assert self.test_shape_3.points[-1] == (100, 0, "straight")
        assert self.test_shape_3.points[-2][2] == 'spline'
        assert self.test_shape_3.points[-3][2] == 'spline'

    def test_convert_circles_to_splines_volume(self):
        """creates a RotateMixedShape with a circular edge and converts the
        edge to a spline edges. Checks the new shape has appoximatly the same
        volume as the orignal shape (with circles)"""

        original_volume = self.test_shape_2.volume
        self.test_shape_2.convert_all_circle_connections_to_splines()
        new_volume = self.test_shape_2.volume

        assert pytest.approx(new_volume, rel=0.000001) == original_volume

        original_volume = self.test_shape_3.volume
        self.test_shape_3.convert_all_circle_connections_to_splines()
        new_volume = self.test_shape_3.volume

        assert pytest.approx(new_volume, rel=0.00001) == original_volume


if __name__ == "__main__":
    unittest.main()
