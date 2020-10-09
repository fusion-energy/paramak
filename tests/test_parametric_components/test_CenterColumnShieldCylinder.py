
import os
import unittest
from pathlib import Path

import paramak
import pytest


class test_CenterColumnShieldCylinder(unittest.TestCase):
    def test_CenterColumnShieldCylinder_creation(self):
        """creates a center column shield using the CenterColumnShieldCylinder parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldCylinder(
            height=600, inner_radius=100, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_volume_CenterColumnShieldCylinder(self):
        """creates a CenterColumnShieldCylinder shape and checks that the volume is correct"""

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        assert test_shape.volume == pytest.approx(3534.29)

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=180,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=95,
        )

        assert test_shape.volume == pytest.approx(3534.29 / 2.0)

    def test_export_stp_CenterColumnShieldCylinder(self):
        """creates a CenterColumnShieldCylinder shape and checks that an stp file of the shape
        can be exported using the export_stp method"""

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        os.system("rm center_column_shield.stp")

        test_shape.export_stp("center_column_shield.stp")

        assert Path("center_column_shield.stp").exists()

        os.system("rm center_column_shield.stp")
