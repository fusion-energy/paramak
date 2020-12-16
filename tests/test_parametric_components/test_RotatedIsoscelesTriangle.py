

import unittest

import paramak
import pytest


class TestRotatedIsoscelesTriangle(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.RotatedIsoscelesTriangle(
            height=10,
            base_length=20,
            pivot_angle=0,
            pivot_point=(100, 50),
            rotation_angle=45,
        )

    def test_component_creation(self):
        """Creates a RotatedTrapezoid object and checks that the .solid is not
        None."""

        assert self.test_shape.solid is not None

    def test_check_number_of_surfaces(self):
        """Counts the surfaces in a fully rotated and partly rotated
        RotatedTrapezoid."""

        assert len(self.test_shape.areas) == 5

        self.test_shape.rotation_angle = 360

        assert len(self.test_shape.areas) == 3

    def test_args_do_not_impact_volume(self):
        """Changes args that should not impact the volume and checks that they
        do not impact the volume"""

        test_shape_vol = self.test_shape.volume

        self.test_shape.pivot_angle = 180

        assert pytest.approx(
            self.test_shape.volume,
            rel=0.01) == test_shape_vol

        self.test_shape.pivot_point = (100, 300)

        assert pytest.approx(
            self.test_shape.volume,
            rel=0.01) == test_shape_vol

    def test_args_impact_volume(self):
        """Changes args that should impact the volume and checks that the
        volume changes as a result of the argument changes"""

        test_shape_vol = self.test_shape.volume

        self.test_shape.pivot_angle = 45

        assert self.test_shape.volume > test_shape_vol

        self.test_shape.height = 42

        assert self.test_shape.volume > test_shape_vol

        self.test_shape.height = 10
        self.test_shape.length_2 = 42

        assert self.test_shape.volume > test_shape_vol

        self.test_shape.height = 10
        self.test_shape.base_length = 20
        self.test_shape.length_3 = 42

        assert self.test_shape.volume > test_shape_vol
