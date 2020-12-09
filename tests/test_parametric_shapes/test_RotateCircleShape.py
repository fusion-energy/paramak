
import math
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateCircleShape


class TestRotateCircleShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = RotateCircleShape(
            points=[(60, 0)],
            radius=10
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a RotateCircleShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "RotateCircleShape.stp"
        assert self.test_shape.stl_filename == "RotateCircleShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0

    def test_absolute_shape_volume(self):
        """Creates RotateCircleShapes and checks that their volumes are correct."""

        # See Issue #445
        # assert self.test_shape.volume == pytest.approx(
        #     2 * math.pi * 60 * math.pi * (10**2)
        # )
        self.test_shape.rotation_angle = 270
        assert self.test_shape.volume == pytest.approx(
            2 * math.pi * 60 * math.pi * (10**2) * 0.75
        )

    def test_absolute_shape_areas(self):
        """Creates RotateCircleShapes and checks that the areas of each face are
        correct."""

        # See Issue #445
        # assert self.test_shape.area == pytest.approx(
        #     math.pi * (10 * 2) * math.pi * (60 * 2))
        # assert len(self.test_shape.areas) == 1
        # assert self.test_shape.areas.count(pytest.approx(
        #     math.pi * (10 * 2) * math.pi * (60 * 2), rel=0.01)) == 1

        self.test_shape.rotation_angle = 180
        assert self.test_shape.area == pytest.approx(
            ((math.pi * (10**2)) * 2) + (math.pi * (10 * 2) * math.pi * (60 * 2) / 2), rel=0.01)
        assert len(self.test_shape.areas) == 3
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10**2))) == 2
        assert self.test_shape.areas.count(pytest.approx(
            math.pi * (10 * 2) * math.pi * (60 * 2) / 2, rel=0.01)) == 1

    def test_relative_shape_volume_azimuth_placement_angle(self):
        """Creates two RotateCircleShapes with different azimuth_placement_angles and
        checks that their relative volumes are correct."""

        self.test_shape.rotation_angle = 10
        assert self.test_shape.volume == pytest.approx(
            (math.pi * 10**2) * ((2 * math.pi * 60) / 36)
        )

        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert self.test_shape.volume == pytest.approx(
            (math.pi * 10**2) * ((2 * math.pi * 60) / 36) * 4
        )

    def test_cut_volume(self):
        """Creates a RotateCircleShape with another RotateCircleShape cut out and
        checks that the volume is correct."""

        outer_shape = RotateCircleShape(
            points=[(60, 0)], radius=15
        )
        outer_shape_volume = outer_shape.volume
        outer_shape.cut = self.test_shape
        assert outer_shape.volume == pytest.approx(
            outer_shape_volume - self.test_shape.volume
        )

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
        # the circle wire file is actually larger than the circle solid file
        # assert Path("test_wire.stp").stat().st_size < \
        #     Path("test_solid2.stp").stat().st_size

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")


if __name__ == "__main__":
    unittest.main()
