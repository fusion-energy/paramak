
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateStraightShape, SweepMixedShape


class TestSweepMixedShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = SweepMixedShape(
            points=[(-10, -10, "straight"), (-10, 10, "spline"), (0, 20, "spline"),
                    (10, 10, "circle"), (0, 0, "circle"), (10, -10, "straight")],
            path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a SweepMixedShape are correct."""

        # assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "SweepMixedShape.stp"
        assert self.test_shape.stl_filename == "SweepMixedShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0
        assert self.test_shape.workplane == "XY"
        assert self.test_shape.path_workplane == "XZ"
        assert self.test_shape.force_cross_section == False

    def test_solid_construction_workplane(self):
        """Checks that SweepMixedShapes can be created in different workplanes"""

        self.test_shape.workplane = "YZ"
        self.test_shape.path_workplane = "YX"
        assert self.test_shape.solid is not None

        self.test_shape.workplane = "XZ"
        self.test_shape.path_workplane = "XY"
        assert self.test_shape.solid is not None

    def test_relative_shape_volume_points(self):
        """Creates two SweepMixedShapes and checks that their relative volumes
        are correct."""

        self.test_shape.points = [(-10, -10, "straight"), (-10, 10, "spline"), (0, 20, "spline"),
                                  (10, 10, "circle"), (0, 0, "circle"), (10, -10, "straight")]
        test_volume = self.test_shape.volume
        self.test_shape.points = [(-20, -20, "straight"), (-20, 20, "spline"), (0, 40, "spline"),
                                  (20, 20, "circle"), (0, 0, "circle"), (20, -20, "straight")]
        assert self.test_shape.volume == pytest.approx(
            test_volume * 4, rel=0.01)

    def test_relative_shape_volume_azimuthal_placement(self):
        """Creates two SweepMixedShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert self.test_shape.volume == pytest.approx(
            test_volume * 4, rel=0.01)

    def test_workplane_path_workplane_error_raises(self):
        """Checks that errors are raised when SweepMixedShapes are created with
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

    def test_workplane_opposite_distance(self):
        """Checks that a SweepMixedShape can be created with workplane XZ and
        path_workplane XY."""

        self.test_shape.workplane = "XZ"
        self.test_shape.path_workplane = "XY"

        assert self.test_shape.solid is not None

    def test_force_cross_section(self):
        """Checks that a SweepMixedshape with the same cross-section at each path_point
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
        """Checks that a SweepMixedShape with a larger volume is created when
        force_cross_section = True than when force_cross_section = False."""

        test_volume = self.test_shape.volume
        self.test_shape.force_cross_section = True
        assert self.test_shape.volume > test_volume

    def test_surface_count(self):
        """Creates a SweepStraightShape and checks that it has the correct number
        of surfaces."""

        assert len(self.test_shape.areas) == 6
        assert len(set(round(i) for i in self.test_shape.areas)) == 5

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
