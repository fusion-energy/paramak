
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

        assert Path("test_solid.stp").stat().st_size == \
            Path("test_solid2.stp").stat().st_size
        assert Path("test_wire.stp").stat().st_size < \
            Path("test_solid2.stp").stat().st_size

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")


if __name__ == "__main__":
    unittest.main()
