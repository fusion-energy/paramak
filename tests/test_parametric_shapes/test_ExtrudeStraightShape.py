
import os
import unittest
from pathlib import Path

import pytest
from paramak import ExtrudeStraightShape


class TestExtrudeStraightShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=30
        )

    def test_default_parameters(self):
        """Checks that the default parameters of an ExtrudeStraightShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "ExtrudeStraightShape.stp"
        assert self.test_shape.stl_filename == "ExtrudeStraightShape.stl"
        assert self.test_shape.extrude_both

    def test_absolute_shape_volume(self):
        """Creates an ExtrudeStraightShape and checks that the volume is correct."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume == pytest.approx(20 * 20 * 30)

    def test_absolute_shape_areas(self):
        """Creates an ExtrudeStraightShape and checks that the volume is correct."""

        assert self.test_shape.area == pytest.approx(
            (20 * 20 * 2) + (20 * 30 * 4)
        )
        assert len(self.test_shape.areas) == 6
        assert self.test_shape.areas.count(pytest.approx(20 * 20)) == 2
        assert self.test_shape.areas.count(pytest.approx(20 * 30)) == 4

    def test_relative_shape_volume(self):
        """Creates two ExtrudeStraightShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.rotation_axis = "Y"
        assert self.test_shape.volume == pytest.approx(test_volume * 4)

    def test_cut_volume(self):
        """Creates an ExtrudeStraightShape with another ExtrudeStraightShape cut out
        and checks that the volume is correct."""

        shape_with_cut = ExtrudeStraightShape(
            points=[(0, 0), (0, 40), (40, 40), (40, 0)], distance=40,
            cut=self.test_shape
        )

        assert shape_with_cut.volume == pytest.approx(
            (40 * 40 * 40) - (20 * 20 * 30)
        )

    def test_union_volume(self):
        """Creates a union of two ExtrudeStraightShapes and checks that the volume is
        correct."""

        unioned_shape = ExtrudeStraightShape(
            points=[(0, 10), (0, 30), (20, 30), (20, 10)], distance=30,
            union=self.test_shape
        )
        assert unioned_shape.volume == pytest.approx(30 * 20 * 30)

    def test_intersect_volume(self):
        """Creates an ExtrudeStraightShape with another ExtrudeStraightShape intersected
        and checks that the volume is correct."""

        intersected_shape = ExtrudeStraightShape(
            points=[(0, 10), (0, 30), (20, 30), (20, 10)], distance=30,
            intersect=self.test_shape
        )
        assert intersected_shape.volume == pytest.approx(10 * 20 * 30)

    def test_rotation_angle(self):
        """Creates an ExtrudeStraightShape with a rotation_angle < 360 and checks that
        the correct cut is performed and the volume is correct."""

        self.test_shape.azimuth_placement_angle = [45, 135, 225, 315]
        self.rotation_axis = "Y"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

    def test_extrude_both(self):
        """Creates an ExtrudeStraightShape with extrude_both = True and False and checks
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
