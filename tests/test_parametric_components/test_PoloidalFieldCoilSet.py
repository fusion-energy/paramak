
import math
import unittest

import paramak
import pytest


class TestPoloidalFieldCoilSet(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.PoloidalFieldCoilSet(
            heights=[10, 15, 5],
            widths=[20, 25, 30],
            center_points=[(100, 100), (200, 200), (300, 300)]
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PoloidalFieldCoilSet are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "PoloidalFieldCoilSet.stp"
        assert self.test_shape.stl_filename == "PoloidalFieldCoilSet.stl"
        # assert self.test_shape.name == "pf_coil"
        assert self.test_shape.material_tag == "pf_coil_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the PoloidalFieldCoilSet are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (110.0, 105.0, 'straight'), (110.0, 95.0, 'straight'), (90.0, 95.0, 'straight'),
            (90.0, 105.0, 'straight'), (212.5, 207.5, 'straight'), (212.5, 192.5, 'straight'),
            (187.5, 192.5, 'straight'), (187.5, 207.5, 'straight'), (315.0, 302.5, 'straight'),
            (315.0, 297.5, 'straight'), (285.0, 297.5, 'straight'), (285.0, 302.5, 'straight'),
            (110.0, 105.0, 'straight')
        ]

    def test_creation(self):
        """Creates a solid using the PoloidalFieldCoilSet parametric component
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert len(self.test_shape.solid.Solids()) == 3

    def test_absolute_volume(self):
        """Creates a set of pf coils using the PoloidalFieldCoilSet parametric
        component and checks that the volume is correct."""

        assert self.test_shape.volume == (pytest.approx((10 * 20 * math.pi * (2 * 100)) + (
            15 * 25 * math.pi * (2 * 200)) + (5 * 30 * math.pi * (2 * 300))))

    def test_absolute_areas(self):
        """Creates a set of pf coils using the PoloidalFieldCoilSet parametric
        component and checks that the areas of its faces are correct."""

        assert len(self.test_shape.areas) == 12
        assert len(set(round(i) for i in self.test_shape.areas)) == 9
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * (2 * 100))) == 2
        assert self.test_shape.areas.count(
            pytest.approx(25 * math.pi * (2 * 200))) == 2
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * (2 * 300))) == 2
        assert self.test_shape.areas.count(
            pytest.approx(10 * math.pi * (2 * 90))) == 1
        assert self.test_shape.areas.count(
            pytest.approx(10 * math.pi * (2 * 110))) == 1
        assert self.test_shape.areas.count(
            pytest.approx(15 * math.pi * (2 * 187.5))) == 1
        assert self.test_shape.areas.count(
            pytest.approx(15 * math.pi * (2 * 212.5))) == 1
        assert self.test_shape.areas.count(
            pytest.approx(5 * math.pi * (2 * 285))) == 1
        assert self.test_shape.areas.count(
            pytest.approx(5 * math.pi * (2 * 315))) == 1

    def test_PoloidalFieldCoilSet_incorrect_height(self):
        """Checks that an error is raised when a PoloidalFieldCoilSet is made
        with height passed as the wrong type."""

        def make_PoloidalFieldCoilSet_incorrect_height():
            paramak.PoloidalFieldCoilSet(
                heights=10,
                widths=[20, 20, 20],
                center_points=[(100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilSet_incorrect_height
        )

    def test_PoloidalFieldCoilSet_incorrect_width(self):
        """Checks that an error is raised when a PoloidalFieldCoilSet is made
        with width passed as the wrong type."""

        def make_PoloidalFieldCoilSet_incorrect_width():
            paramak.PoloidalFieldCoilSet(
                heights=[10, 10, 10],
                widths=20,
                center_points=[(100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilSet_incorrect_width
        )

    def test_PoloidalFieldCoilSet_incorrect_center_points(self):
        """Checks that an error is raised when a PoloidalFieldCoilSet is made
        with center_points passed as the wrong type."""

        def make_PoloidalFieldCoilSet_incorrect_center_points():
            paramak.PoloidalFieldCoilSet(
                heights=[10, 10, 10],
                widths=[20, 20, 20],
                center_points=100)

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilSet_incorrect_center_points
        )

    def test_PoloidalFieldCoilSet_incorrect_width_length(self):
        """Checks that an error is raised when a PoloidalFieldCoilSet is made
        with the incorrect number of widths."""

        def make_PoloidalFieldCoilSet_incorrect_width_length():
            paramak.PoloidalFieldCoilSet(
                heights=[10, 10, 10],
                widths=[20, 20],
                center_points=[(100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilSet_incorrect_width_length
        )
