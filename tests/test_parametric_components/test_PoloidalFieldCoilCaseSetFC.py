
import math
import unittest

import paramak
import pytest


class TestPoloidalFieldCoilCaseSetFC(unittest.TestCase):

    def setUp(self):
        self.pf_coils_set = paramak.PoloidalFieldCoilSet(
            heights=[10, 10, 20, 20],
            widths=[10, 10, 20, 40],
            center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
        )

        self.test_shape = paramak.PoloidalFieldCoilCaseSetFC(
            pf_coils=self.pf_coils_set,
            casing_thicknesses=[5, 10, 5, 10],
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PoloidalFieldCoilCaseSetFC are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "PoloidalFieldCoilCaseSetFC.stp"
        assert self.test_shape.stl_filename == "PoloidalFieldCoilCaseSetFC.stl"
        # assert self.test_shape.name == "pf_coil_case_set_fc"
        assert self.test_shape.material_tag == "pf_coil_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the PoloidalFieldCoilCaseSetFC are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (105.0, 105.0, 'straight'), (105.0, 95.0, 'straight'), (95.0, 95.0, 'straight'),
            (95.0, 105.0, 'straight'), (105.0, 105.0, 'straight'), (110.0, 110.0, 'straight'),
            (110.0, 90.0, 'straight'), (90.0, 90.0, 'straight'), (90.0, 110.0, 'straight'),
            (110.0, 110.0, 'straight'), (105.0, 155.0, 'straight'), (105.0, 145.0, 'straight'),
            (95.0, 145.0, 'straight'), (95.0, 155.0, 'straight'), (105.0, 155.0, 'straight'),
            (115.0, 165.0, 'straight'), (115.0, 135.0, 'straight'), (85.0, 135.0, 'straight'),
            (85.0, 165.0, 'straight'), (115.0, 165.0, 'straight'), (60.0, 210.0, 'straight'),
            (60.0, 190.0, 'straight'), (40.0, 190.0, 'straight'), (40.0, 210.0, 'straight'),
            (60.0, 210.0, 'straight'), (65.0, 215.0, 'straight'), (65.0, 185.0, 'straight'),
            (35.0, 185.0, 'straight'), (35.0, 215.0, 'straight'), (65.0, 215.0, 'straight'),
            (70.0, 60.0, 'straight'), (70.0, 40.0, 'straight'), (30.0, 40.0, 'straight'),
            (30.0, 60.0, 'straight'), (70.0, 60.0, 'straight'), (80.0, 70.0, 'straight'),
            (80.0, 30.0, 'straight'), (20.0, 30.0, 'straight'), (20.0, 70.0, 'straight'),
            (80.0, 70.0, 'straight'), (105.0, 105.0, 'straight')
        ]

    def test_from_pf_coil_set(self):
        """Checks that a set of PF coil cases can be constructed from a PF coils object
        using the PoloidalField~CoilCaseSetFC parametric shape."""

        assert self.test_shape.solid is not None
        assert len(self.test_shape.solid.Solids()) == 4
        assert len(self.pf_coils_set.solid.Solids()) == 4

    def test_with_zero_thickness(self):
        """Creates a set of PF coil cases from a PF coils object and sets one
        of the casing thicknesses to 0."""

        self.test_shape.casing_thicknesses = [5, 5, 0, 10]

        assert self.test_shape.solid is not None
        assert len(self.test_shape.solid.Solids()) == 3
        assert len(self.pf_coils_set.solid.Solids()) == 4

    def test_from_pf_coil_set_absolute_volume(self):
        """Creates a set of pf coil cases from a pf coil set object and checks
        that the volume is correct."""

        assert self.test_shape.volume == pytest.approx((((20 * 5 * 2) + (10 * 5 * 2)) * math.pi * 2 * 100) + (((30 * 10 * 2) + (
            10 * 10 * 2)) * math.pi * 2 * 100) + (((30 * 5 * 2) + (20 * 5 * 2)) * math.pi * 2 * 50) + (((60 * 10 * 2) + (20 * 10 * 2)) * math.pi * 2 * 50))

    def test_from_pf_coil_set_absolute_areas(self):
        """Creates a set of pf coil cases from a pf coil set object and checks
        that the areas are correct"""

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

    def test_PoloidalFieldCoilCaseSetFC_incorrect_lengths_FC(self):
        """Checks that an error is raised when a PoloidalFieldCoilCaseSetFC is made
        with the wrong number of casing thicknesses using a coil set object."""

        def make_PoloidalFieldCoilCaseSetFC_incorrect_lengths_FC():
            self.test_shape.casing_thicknesses = [5, 5, 10]
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilCaseSetFC_incorrect_lengths_FC
        )

    def test_PoloidalFieldCoilCaseSetFC_incorrect_lengths(self):
        """Checks that an error is raised when a PoloidalFieldCoilCaseSetFC is made
        with the wrong number of casing thicknesses using a list."""

        def make_PoloidalFieldCoilCaseSetFC_incorrect_lengths():
            self.pf_coils_set.height = 10
            self.pf_coils_set.width = 10
            self.pf_coils_set.center_point = (100, 100)

            self.test_shape.pf_coils = [self.pf_coils_set]
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilCaseSetFC_incorrect_lengths
        )

    def test_PoloidalFieldCoilCaseSetFC_incorrect_pf_coil(self):
        """Checks that an error is raised when a PoloidalFieldCoilCaseSetFC is made
        with the pf_coils as an incorrect entry."""

        def make_PoloidalFieldCoilCaseSetFC_incorrect_pf_coil():
            self.test_shape.pf_coils = 20
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            make_PoloidalFieldCoilCaseSetFC_incorrect_pf_coil
        )

    def test_from_list(self):
        """Creates a set of PF coil cases from a list of PF coils with a list
        of thicknesses."""

        pf_coils_1 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 100))

        pf_coils_2 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 150))

        pf_coils_3 = paramak.PoloidalFieldCoil(height=20,
                                               width=20,
                                               center_point=(50, 200))

        pf_coils_4 = paramak.PoloidalFieldCoil(height=20,
                                               width=40,
                                               center_point=(50, 50))

        test_shape = paramak.PoloidalFieldCoilCaseSetFC(
            pf_coils=[pf_coils_1, pf_coils_2, pf_coils_3, pf_coils_4],
            casing_thicknesses=[5, 5, 10, 10]
        )

        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 4

    def test_PoloidalFieldCoilCaseSetFC_with_number_thickness(self):
        """Creates a set of PF coil cases from a list of PF coils with a
        single numerical thicknesses."""

        pf_coils_1 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 100))

        pf_coils_2 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 150))

        pf_coils_3 = paramak.PoloidalFieldCoil(height=20,
                                               width=20,
                                               center_point=(50, 200))

        pf_coils_4 = paramak.PoloidalFieldCoil(height=20,
                                               width=40,
                                               center_point=(50, 50))

        test_shape = paramak.PoloidalFieldCoilCaseSetFC(
            pf_coils=[pf_coils_1, pf_coils_2, pf_coils_3, pf_coils_4],
            casing_thicknesses=10,
        )

        assert test_shape.casing_thicknesses == 10
        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 4
