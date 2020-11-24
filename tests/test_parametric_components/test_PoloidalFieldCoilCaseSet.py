
import math
import unittest

import paramak
import pytest


class test_PoloidalFieldCoilCaseSet(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.PoloidalFieldCoilCaseSet(
            heights=[10, 10, 20, 20],
            widths=[10, 10, 20, 40],
            center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
            casing_thicknesses=[5, 10, 5, 10],
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PoloidalFieldCoilCaseSet are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "PoloidalFieldCoilCaseSet.stp"
        assert self.test_shape.stl_filename == "PoloidalFieldCoilCaseSet.stl"
        # assert self.test_shape.name == "pf_coil_case_set"
        assert self.test_shape.material_tag == "pf_coil_case_mat"

    def test_PoloidalFieldCoilCaseSet_creation(self):
        """Creates a set of pf coils using the PoloidalFieldCoilCaseSet
        parametric component and passing all required args, and checks
        that a solid with the correct number of solids is created."""

        assert self.test_shape.solid is not None
        assert len(self.test_shape.solid.Solids()) == 4

    def test_PoloidalFieldCoilCaseSet_creation_with_zero_thickness(self):
        """Creates a set of pf coils using the PoloidalFieldCoilCaseSet
        parametric component and passing a 0 entry into the casing_thicknesses
        list, and checks that a solid with the correct number of solids is
        created."""

        self.test_shape.casing_thicknesses = [5, 0, 10, 10]

        assert self.test_shape.solid is not None
        assert len(self.test_shape.solid.Solids()) == 3

    def test_PoloidalFieldCoilCaseSet_absolute_volume(self):
        """Creates a set of pf coils using the PoloidalFieldCoilCaseSet
        parametric component and checks that the volume is correct."""

        assert self.test_shape.volume == pytest.approx((((20 * 5 * 2) +
                (10 * 5 * 2)) * math.pi * 2 * 100) + (((30 * 10 * 2) +
                (10 * 10 * 2)) * math.pi * 2 * 100) + (((30 * 5 * 2) +
                (20 * 5 * 2)) * math.pi * 2 * 50) + (((60 * 10 * 2) +
                (20 * 10 * 2)) * math.pi * 2 * 50))

    def test_PoloidalFieldCoilCaseSet_absolute_areas(self):
        """Creates a set of pf coils using the PoloidalFieldCoilCaseSet
        parametric component and checks that the areas are correct"""

        assert len(self.test_shape.areas) == 32
        assert len(set([round(i) for i in self.test_shape.areas])) == 16
        assert self.test_shape.areas.count(
            pytest.approx(10 * math.pi * 2 * 100)) == 6
        assert self.test_shape.areas.count(
            pytest.approx(40 * math.pi * 2 * 50)) == 4
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * 2 * 100)) == 4
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * 2 * 50)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(10 * math.pi * 2 * 105)) == 3
        assert self.test_shape.areas.count(
            pytest.approx(10 * math.pi * 2 * 95)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 110)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 90)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * 2 * 115)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * 2 * 85)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 60)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 40)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(30 * math.pi * 2 * 65)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 70)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(20 * math.pi * 2 * 30)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(40 * math.pi * 2 * 80)) == 1

    def test_PoloidalFieldCoilCaseSet_incorrect_args(self):
        """Creates a solid using the PoloidalFieldCoilCaseSet with incorrect
        args"""

        def test_PoloidalFieldCoilSet_incorrect_lengths_():
            """Checks PoloidalFieldCoilSet with the wrong number of casing
            thicknesses (3) using a coil set object with 4 pf_coils."""

            self.test_shape.casing_thicknesses = [5, 5, 10]
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_lengths_)
