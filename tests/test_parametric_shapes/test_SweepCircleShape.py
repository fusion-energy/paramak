
import math
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateStraightShape, SweepCircleShape


class TestSweepCircleShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = SweepCircleShape(
            radius=10,
            path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a SweepCircleShape are correct."""

        # assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "SweepCircleShape.stp"
        assert self.test_shape.stl_filename == "SweepCircleShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0
        assert self.test_shape.workplane == "XY"
        assert self.test_shape.path_workplane == "XZ"
        assert self.test_shape.force_cross_section is False

    def test_solid_construction_workplane(self):
        """Checks that SweepSplineShapes can be created in different workplanes."""

        self.test_shape.workplane = "YZ"
        self.test_shape.path_workplane = "YX"
        assert self.test_shape.solid is not None

        self.test_shape.workplane = "XZ"
        self.test_shape.path_workplane = "XY"
        assert self.test_shape.solid is not None

    def test_workplane_path_workplane_error_raises(self):
        """Checks that errors are raised when SweepCircleShapes are created with
        disallowed workplane and path_workplane combinations."""

        def workplane_and_path_workplane_equal():
            self.test_shape.workplane = "XZ"
            self.test_shape.path_workplane = "XZ"

        def invalid_relative_workplane_and_path_workplane():
            self.test_shape.workplane = "XZ"
            self.test_shape.path_workplane = "YZ"

        self.assertRaises(ValueError, workplane_and_path_workplane_equal)
        self.assertRaises(
            ValueError,
            invalid_relative_workplane_and_path_workplane)

    def test_absolute_shape_volume(self):
        """Creates a SweepCircleShape and checks that the volume is correct."""

        self.test_shape.path_points = [(50, 0), (50, 50), (50, 100)]
        assert self.test_shape.solid is not None
        assert self.test_shape.volume == pytest.approx(math.pi * 10**2 * 100)

    def test_relative_shape_volume_radius(self):
        """Creates two SweepCircleShapes and checks that their relative volume
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.radius = 20
        assert self.test_shape.volume == pytest.approx(
            test_volume * 4, rel=0.01)

    def test_relative_shape_volume_azimuthal_placement(self):
        """Creates two SweepCircleShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert self.test_shape.volume == pytest.approx(
            test_volume * 4, rel=0.01)

    def test_points_equal_path_points(self):
        """Checks that shape.points = shape.path_points upon construction of a
        SweepCircleShape."""

        assert self.test_shape.points == self.test_shape.path_points

    def test_html(self):
        """Checks that a html graph of the path_points of a SweepCircleShape can be
        exported using the export_html method."""

        assert self.test_shape.export_html("filename.html") is not None

    def test_force_cross_section(self):
        """Checks that a SweepCircleShape with the same cross-section at each path_point
        is created when force_cross_section = True."""

        self.test_shape.force_cross_section = True

        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10**2), rel=0.01)) == 2

        cutting_shape = RotateStraightShape(
            points=[(0, 50), (0, 200), (100, 200), (100, 50)],
        )
        self.test_shape.cut = cutting_shape

        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10**2), rel=0.01)) == 2

        cutting_shape = RotateStraightShape(
            points=[(0, 100), (0, 200), (100, 200), (100, 100)]
        )
        self.test_shape.cut = cutting_shape

        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10**2), rel=0.01)) == 2

    def test_force_cross_section_volume(self):
        """Checks that a SweepCircleShape with a larger volume is created when
        force_cross_section = True than when force_cross_section = False."""

        test_volume = self.test_shape.volume
        self.test_shape.force_cross_section = True
        assert self.test_shape.volume > test_volume

    def test_surface_count(self):
        """Creates a SweepCircleShape and checks that it has the correct number
        of surfaces."""

        assert len(self.test_shape.areas) == 3
        assert len(set(round(i) for i in self.test_shape.areas)) == 2

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
