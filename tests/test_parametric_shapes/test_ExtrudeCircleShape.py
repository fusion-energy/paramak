import math
import unittest

import pytest

from paramak import ExtrudeCircleShape


class TestExtrudeCircleShape(unittest.TestCase):

    def setUp(self):
        self.test_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=30
        )

    def test_default_parameters(self):
        """Checks that the default parameters of an ExtrudeCircleShape are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "ExtrudeCircleShape.stp"
        assert self.test_shape.stl_filename == "ExtrudeCircleShape.stl"
        assert self.test_shape.extrude_both

    def test_absolute_shape_volume(self):
        """Creates an ExtrudeCircleShape and checks that its volume is correct."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume == pytest.approx(math.pi * (10**2) * 30)

    def test_relative_shape_volume(self):
        """Creates two ExtrudeCircleShapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert test_volume * 4 == pytest.approx(self.test_shape.volume)

    def test_absolute_shape_areas(self):
        """Creates ExtrudeCircleShapes and checks that the areas of each face
        are correct."""

        assert self.test_shape.area == pytest.approx(
            (math.pi * (10**2) * 2) + (math.pi * (2 * 10) * 30)
        )
        assert len(self.test_shape.areas) == 3
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10**2))) == 2
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (2 * 10) * 30)) == 1

    def test_cut_volume(self):
        """Creates an ExtrudeCircleShape with another ExtrudeCircleShape cut out
        and checks that the volume is correct."""

        shape_with_cut = ExtrudeCircleShape(
            points=[(30, 0)], radius=20, distance=40,
            cut=self.test_shape
        )

        assert shape_with_cut.volume == pytest.approx(
            (math.pi * (20**2) * 40) - (math.pi * (10**2) * 30)
        )

    def test_intersect_volume(self):
        """Creates ExtrudeCircleShapes with other ExtrudeCircleShapes intersected
        and checks that their volumes are correct."""

        intersect_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=50)

        intersected_shape = ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=50,
            intersect=[self.test_shape, intersect_shape]
        )

        assert intersected_shape.volume == pytest.approx(math.pi * 5**2 * 30)

    def test_rotation_angle(self):
        """Creates an ExtrudeCircleShape with a rotation_angle < 360 and checks that
        the correct cut is performed and the volume is correct."""

        self.test_shape.azimuth_placement_angle = [45, 135, 225, 315]
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(test_volume * 0.5)

    def test_extrude_both(self):
        """Creates an ExtrudeCircleShape with extrude_both = True and False and checks
        that the volumes are correct."""

        test_volume_extrude_both = self.test_shape.volume
        self.test_shape.extrude_both = False
        assert self.test_shape.volume == pytest.approx(
            test_volume_extrude_both)


if __name__ == "__main__":
    unittest.main()
