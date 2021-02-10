
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateStraightShape, SweepSplineShape


class TestSweepSplineShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = SweepSplineShape(
            points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
            path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a SweepSplineShape are correct."""

        # assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "SweepSplineShape.stp"
        assert self.test_shape.stl_filename == "SweepSplineShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0
        assert self.test_shape.workplane == "XY"
        assert self.test_shape.path_workplane == "XZ"
        assert self.test_shape.force_cross_section == False

    def test_solid_construction_workplane(self):
        """Checks that SweepSplineShapes can be created in different workplanes."""

        self.test_shape.workplane = "YZ"
        self.test_shape.path_workplane = "YX"
        assert self.test_shape.solid is not None

        self.test_shape.workplane = "XZ"
        self.test_shape.path_workplane = "XY"
        assert self.test_shape.solid is not None

    def test_relative_shape_volume_points(self):
        """Creates two SweepSplineShapes and checks that their relative volumes
        are correct."""

        self.test_shape.points = [(-20, 20), (20, 20), (20, -20), (-20, -20)]
        test_volume = self.test_shape.volume
        self.test_shape.points = [(-10, 10), (10, 10), (10, -10), (-10, -10)]
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.25, rel=0.01)

    def test_relative_shape_volume_azimuthal_placement(self):
        """Creates two SweepSplineShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert self.test_shape.volume == pytest.approx(
            test_volume * 4, rel=0.01)

    def test_force_cross_section(self):
        """Checks that a SweepSplineShape with the same cross-section at each path_point
        is created when force_cross_section = True."""

        self.test_shape.force_cross_section = True

        test_area = round(min(self.test_shape.areas))

        assert self.test_shape.areas.count(
            pytest.approx(test_area, rel=0.01)) == 2

        cutting_shape = RotateStraightShape(
            points=[(0, 50), (0, 200), (100, 200), (100, 50)]
        )
        self.test_shape.cut = cutting_shape

        assert self.test_shape.areas.count(
            pytest.approx(test_area, rel=0.01)) == 2

        cutting_shape.points = [(0, 100), (0, 200), (100, 200), (100, 100)]
        self.test_shape.cut = cutting_shape

        assert self.test_shape.areas.count(
            pytest.approx(test_area, rel=0.01)) == 2

    def test_force_cross_section_volume(self):
        """Checks that a SweepSplineShape with a larger volume is created when
        force_cross_section = True than when force_cross_section = False."""

        test_volume = self.test_shape.volume
        self.test_shape.force_cross_section = True
        assert self.test_shape.volume > test_volume

    def test_surface_count(self):
        """Creates a SweepSplineShape and checks that it has the correct number
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

    def test_incorrect_points_input(self):
        """Checks that an error is raised when the points are input with the
        connection"""

        def incorrect_points_definition():
            self.test_shape.points = [
                (10, 10, 'spline'),
                (10, 30, 'spline'),
                (30, 30, 'spline'),
                (30, 10, 'spline')
            ]

        self.assertRaises(
            ValueError,
            incorrect_points_definition
        )


if __name__ == "__main__":
    unittest.main()
