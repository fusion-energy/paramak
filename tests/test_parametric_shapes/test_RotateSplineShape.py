
import os
import unittest
from pathlib import Path

import pytest
from paramak import RotateSplineShape


class TestRotateSplineShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = RotateSplineShape(
            points=[(50, 0), (50, 20), (70, 80), (90, 50), (70, 0),
                    (90, -50), (70, -80), (50, -20)])

    def test_default_parameters(self):
        """Checks that the default parameters of a RotateSplineShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "RotateSplineShape.stp"
        assert self.test_shape.stl_filename == "RotateSplineShape.stl"
        assert self.test_shape.azimuth_placement_angle == 0

    def test_absolute_shape_volume(self):
        """creates a rotated shape using spline connections and checks the volume
        is correct"""

        self.test_shape.rotation_angle = 360
        volume_360 = self.test_shape.volume

        assert self.test_shape.solid is not None
        assert volume_360 > 100

        self.test_shape.rotation_angle = 180
        assert self.test_shape.solid is not None
        assert self.test_shape.volume == pytest.approx(volume_360 * 0.5)

    def test_cut_volume(self):
        """Creates a RotateSplineShape with another RotateSplineShape cut out
        and checks that the volume is correct."""

        inner_shape = RotateSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], rotation_angle=180
        )

        outer_shape = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(900.88, abs=0.1)
        assert outer_shape.volume == pytest.approx(2881.76, abs=0.1)
        assert outer_shape_with_cut.volume == pytest.approx(
            2881.76 - 900.88, abs=0.2)

    def test_shape_face_areas(self):
        """Creates RotateSplineShapes and checks that the face areas are expected."""

        assert len(self.test_shape.areas) == 1
        assert len(set(self.test_shape.areas)) == 1

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 3
        assert len(set([round(i) for i in self.test_shape.areas])) == 2

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
