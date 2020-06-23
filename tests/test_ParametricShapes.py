
import os
import unittest
from pathlib import Path

import pytest

from paramak.parametric_shapes import BlanketConstantThickness
from paramak.parametric_shapes import PoloidalFieldCoilCase
from paramak.parametric_shapes import DivertorBlock
from paramak.parametric_shapes import CenterColumnShieldHyperbola
from paramak.parametric_shapes import CenterColumnShieldCylinder
from paramak.parametric_shapes import PoloidalFieldCoil
from paramak.parametric_shapes import CenterColumnShieldFlatTopHyperbola
from paramak.parametric_shapes import CenterColumnShieldPlasmaHyperbola
from paramak.parametric_shapes import PlasmaShape


class test_BlanketConstantThickness(unittest.TestCase):
    def test_BlanketConstantThickness_creation(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_shape = BlanketConstantThickness(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=90,
            start_angle=270,
            offset_from_plasma=30,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_PoloidalFieldCoilCase(unittest.TestCase):
    def test_PoloidalFieldCoilCase_creation(self):
        """creates a poloidal field coil from parametric shape and checks a solid is created"""
        test_shape = PoloidalFieldCoilCase(
            casing_thickness=5, coil_height=50, coil_width=50, center_point=(1000, 500)
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_PlasmaShape(unittest.TestCase):
    def test_plasma_elongation_type(self):
        """creates a plasma object and checks elongation is type float"""

        test_plasma = PlasmaShape()

        assert type(test_plasma.elongation) == float

        def test_plasma_elongation_min_setting():
            """checks ValueError is raised when an elongation < 0 is specified"""

            test_plasma.elongation = -1

        self.assertRaises(ValueError, test_plasma_elongation_min_setting)

        def test_plasma_elongation_max_setting():
            """checks ValueError is raised when an elongation > 4 is specified"""

            test_plasma.elongation = 400

        self.assertRaises(ValueError, test_plasma_elongation_max_setting)

    def test_export_plasma_source(self):
        """checks that export_stp() exports plasma stp file"""

        test_plasma = PlasmaShape()

        os.system("rm plasma.stp")

        test_plasma.export_stp("plasma.stp")

        assert Path("plasma.stp").exists() == True
        os.system("rm plasma.stp")


# class test_DivertorBlock(unittest.TestCase):
# def test_DivertorBlock_creation(self):
#         test_shape = DivertorBlock(major_radius = 300,
#                                    minor_radius = 50,
#                                    triangularity = 0.5,
#                                    elongation = 2,
#                                    thickness = 50,
#                                    stop_angle = 120,
#                                    offset_from_plasma = 20,
#                                    start_x_value = 10)

#         assert test_shape.solid is not None
#         assert test_shape.volume > 1000


class test_CenterColumnShieldFlatTopHyperbola(unittest.TestCase):
    def test_CenterColumnShieldFlatTopHyperbola_creation(self):
        """creates a CenterColumnShieldFlatTopHyperbola object and checks a solid is created"""

        test_shape = CenterColumnShieldFlatTopHyperbola(
            height=500,
            arc_height=300,
            inner_radius=50,
            mid_radius=100,
            outer_radius=150,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldPlasmaHyperbola(unittest.TestCase):
    def test_CenterColumnShieldPlasmaHyperbola_creation(self):
        """creates a CenterColumnShieldPlasmaHyperbola object and checks a solid is created"""

        test_shape = CenterColumnShieldPlasmaHyperbola(
            inner_radius=50, height=800, mid_offset=40, edge_offset=30
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldHyperbola(unittest.TestCase):
    def test_CenterColumnShieldHyperbola_creation(self):
        """creates a CenterColumnShieldHyperbola object and checks a solid is created"""

        test_shape = CenterColumnShieldHyperbola(
            height=100, inner_radius=50, mid_radius=80, outer_radius=100
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_PoloidalFieldCoil(unittest.TestCase):
    def test_PoloidalFieldCoil_creation(self):
        """creates a PoloidalFieldCoil object and checks a solid is created"""

        test_shape = PoloidalFieldCoil(height=50, width=60, center_point=(1000, 500))

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldCylinder(unittest.TestCase):
    def test_CenterColumnShieldCylinder_creation(self):
        """creates a CenterColumnShieldCylinder object and checks a solid is created"""

        test_shape = CenterColumnShieldCylinder(
            height=600, inner_radius=100, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_volume_CenterColumnShieldCylinder(self):
        """creates a CenterColumnShieldCylinder object and checks that the volume is correct"""

        test_shape = CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        assert test_shape.volume == pytest.approx(3534.29)

        test_shape = CenterColumnShieldCylinder(
            rotation_angle=180,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=95,
        )

        assert test_shape.volume == pytest.approx(3534.29 / 2.0)

    def test_export_stp_CenterColumnShieldCylinder(self):
        """checks that export_stp() can export an stp file of a CenterColumnShieldCylinder object"""

        test_shape = CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        os.system("rm center_column_shield.stp")

        test_shape.export_stp("center_column_shield.stp")

        assert Path("center_column_shield.stp").exists() == True

        os.system("rm center_column_shield.stp")


if __name__ == "__main__":
    unittest.main()