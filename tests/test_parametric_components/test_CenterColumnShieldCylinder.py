
import math
import os
import unittest
from pathlib import Path

import paramak
import pytest


class TestCenterColumnShieldCylinder(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldCylinder(
            height=600, inner_radius=100, outer_radius=200
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a CenterColumnShieldCylinder are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "CenterColumnShieldCylinder.stp"
        assert self.test_shape.stl_filename == "CenterColumnShieldCylinder.stl"
        # assert self.test_shape.name == "center_column_shield"
        assert self.test_shape.material_tag == "center_column_shield_mat"

    def test_creation(self):
        """Creates a center column shield using the CenterColumnShieldCylinder
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_points_calculation(self):
        """Checks that the points used to construct the CenterColumnShieldCylinder component
        are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (100, 300, "straight"), (200, 300, "straight"), (200, -300, "straight"),
            (100, -300, "straight"), (100, 300, "straight")
        ]

    def test_relative_volume(self):
        """Creates CenterColumnShieldCylinder shapes and checks that their
        relative volumes are correct"""

        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert test_volume == pytest.approx(self.test_shape.volume * 2)

    def test_absolute_volume(self):
        """Creates a CenterColumnShieldCylinder shape and checks that its
        relative volume is correct"""

        assert self.test_shape.volume == pytest.approx(
            ((math.pi * (200**2)) - (math.pi * (100**2))) * 600
        )

    def test_absolute_area(self):
        """Creates a CenterColumnShieldCylinder shape and checks that the
        areas of the faces of the solid created are correct"""

        assert len(self.test_shape.areas) == 4
        assert self.test_shape.area == pytest.approx((((math.pi * (200**2)) - (math.pi * (
            100**2))) * 2) + (math.pi * (2 * 200) * 600) + (math.pi * (2 * 100) * 600))
        assert self.test_shape.areas.count(pytest.approx(
            (math.pi * (200**2)) - (math.pi * (100**2)))) == 2
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (2 * 200) * 600)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (2 * 100) * 600)) == 1

    def test_export_stp_CenterColumnShieldCylinder(self):
        """Creates a CenterColumnShieldCylinder shape and checks that a stp
        file of the shape can be exported using the export_stp method."""

        os.system("rm center_column_shield.stp")
        self.test_shape.export_stp("center_column_shield.stp")
        assert Path("center_column_shield.stp").exists()
        os.system("rm center_column_shield.stp")

    def test_parametric_component_hash_value(self):
        """Creates a parametric component and checks that a cadquery solid with
        a unique hash value is created when .solid is called. Checks that the
        same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the
        parametric component. Checks that a new cadquery solid with a new
        unique hash value is constructed when shape.solid is called after
        changes to the parametric component have been made. Checks that the
        hash_value of a parametric component is not updated until a new
        cadquery solid has been created."""

        assert self.test_shape.hash_value is None
        assert self.test_shape.solid is not None
        assert self.test_shape.hash_value is not None
        initial_hash_value = self.test_shape.hash_value
        assert self.test_shape.solid is not None
        assert initial_hash_value == self.test_shape.hash_value
        self.test_shape.height = 120
        assert initial_hash_value == self.test_shape.hash_value
        assert self.test_shape.solid is not None
        assert initial_hash_value != self.test_shape.hash_value

    def test_center_column_shield_cylinder_invalid_parameters_errors(self):
        """Checks that the correct errors are raised when invalid arguments are entered
        as shape parameters."""

        def incorrect_inner_radius():
            self.test_shape.inner_radius = 250

        def incorrect_outer_radius():
            self.test_shape.inner_radius = 100
            self.test_shape.outer_radius = 50

        def incorrect_height():
            self.test_shape.outer_radius = 200
            self.test_shape.height = None

        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_outer_radius)
        self.assertRaises(ValueError, incorrect_height)
