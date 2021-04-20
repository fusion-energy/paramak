
import os
import unittest
from pathlib import Path

import pytest
from paramak import ExtrudeMixedShape


class TestExtrudeMixedShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = ExtrudeMixedShape(
            points=[(50, 0, "straight"), (50, 50, "spline"), (60, 70, "spline"),
                    (70, 50, "circle"), (60, 25, "circle"), (70, 0, "straight")],
            distance=50
        )

        self.test_shape_2 = ExtrudeMixedShape(
            distance=1,
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

        self.test_shape_3 = ExtrudeMixedShape(
            distance=180,
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

    def test_default_parameters(self):
        """Checks that the default parameters of an ExtrudeMixedShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "ExtrudeMixedShape.stp"
        assert self.test_shape.stl_filename == "ExtrudeMixedShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0

    def test_absolute_shape_volume(self):
        """Creates an ExtrudeMixedShape and checks that the volume is correct."""

        assert self.test_shape.volume > 20 * 20 * 30

    def test_relative_shape_volume(self):
        """Creates two ExtrudeMixedShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 180]

        assert self.test_shape.volume == pytest.approx(
            test_volume * 2, rel=0.01)

    def test_shape_face_areas(self):
        """Creates an ExtrudeMixedShape and checks that the face areas are expected."""

        self.test_shape.extrude_both = False
        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 5

    def test_cut_volume(self):
        """Creates an ExtrudeMixedShape with another ExtrudeMixedShape cut out and
        checks that the volume is correct."""

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

    def test_export_stp_extension(self):
        """Creates an ExtrudeMixedShape and checks that a stp file of the shape
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
        """Creates a ExtrudeMixedShape and checks that a stl file of the shape
        can be exported with the correct suffix using the export_stl method."""

        os.system("rm filename.stl")
        self.test_shape.export_stl("filename.stl")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")
        self.test_shape.export_stl("filename")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")

    def test_rotation_angle(self):
        """Creates an ExtrudeMixedShape with a rotation_angle < 360 and checks that
        the correct cut is performed and the volume is correct."""

        self.test_shape.azimuth_placement_angle = [45, 135, 225, 315]
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

    def test_extrude_both(self):
        """Creates an ExtrudeMixedShape with extrude_both = True and False and checks
        that the volumes are correct."""

        test_volume_extrude_both = self.test_shape.volume
        self.test_shape.extrude_both = False
        assert self.test_shape.volume == pytest.approx(
            test_volume_extrude_both)

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

        assert pytest.approx(Path("test_solid.stp").stat().st_size, rel=1) == \
            Path("test_solid2.stp").stat().st_size
        assert Path("test_wire.stp").stat().st_size < \
            Path("test_solid2.stp").stat().st_size

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")

    def test_convert_all_circle_points_change_to_splines(self):
        """creates a ExtrudeMixedShape with one circular edges and converts
        them to spline edges. Checks the new edges have been correctly
        replaced with splines"""

        assert len(self.test_shape_2.points) == 8
        self.test_shape_2.convert_all_circle_connections_to_splines()
        assert len(self.test_shape_2.points) > 8
        assert self.test_shape_2.points[0] == (100, 0, "straight")
        assert self.test_shape_2.points[1] == (200, 0, 'spline')

        # last point is the same as the first point
        assert self.test_shape_2.points[-1] == (100, 0, "straight")
        assert self.test_shape_2.points[-2] == (110, 45, "straight")
        assert self.test_shape_2.points[-3] == (140, 75, "straight")
        assert self.test_shape_2.points[-4] == (150, 100, "straight")
        assert self.test_shape_2.points[-5] == (200, 100, "straight")

        for point in self.test_shape_2.points[1:len(
                self.test_shape_2.points) - 5]:
            assert point[2] == 'spline'

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

        assert pytest.approx(new_volume, rel=0.000001) == original_volume


if __name__ == "__main__":
    unittest.main()
