import unittest
import math
import paramak


class TestSphericalShell(unittest.TestCase):
    def setUp(self):
        self.test_shape = paramak.SphericalShell(inner_radius=1, shell_thickness=0.2, rotation_angle=180)

    def test_volume(self):
        """Creates a shape wit different roation angles and checks the volume."""
        vol1 = (4 / 3) * math.pi * math.pow(self.test_shape.inner_radius, 3)
        vol2 = (4 / 3) * math.pi * math.pow(self.test_shape.inner_radius + self.test_shape.shell_thickness, 3)
        full_vol = vol2 - vol1

        self.test_shape.rotation_angle = 180
        assert math.isclose(0.5 * full_vol, self.test_shape.volume())

        self.test_shape.rotation_angle = 360
        assert math.isclose(full_vol, self.test_shape.volume())

        self.test_shape.rotation_angle = 270
        assert math.isclose(0.75 * full_vol, self.test_shape.volume())

    def test_creation(self):
        """Creates a shape and checks that a cadquery solid is created.
        Different rotation angles are used as we have special case handling
        for the 360 degree case"""

        self.test_shape.rotation_angle = 180
        assert self.test_shape.solid is not None

        self.test_shape.rotation_angle = 360
        assert self.test_shape.solid is not None

    def test_surfaces(self):
        """Creates a shape and checks that a cadquery solid is created.
        Different rotation angles are used as we have special case handling
        for the 360 degree case"""

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.solid.faces().all()) == 3

        self.test_shape.rotation_angle = 360
        assert len(self.test_shape.solid.faces().all()) == 2

        self.test_shape.rotation_angle = 270
        assert len(self.test_shape.solid.faces().all()) == 4
