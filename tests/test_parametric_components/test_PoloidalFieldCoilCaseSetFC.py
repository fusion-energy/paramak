
import paramak
import unittest


class test_PoloidalFieldCoilCaseSetFC(unittest.TestCase):
    def test_PoloidalFieldCoilCaseSetFC_from_pf_coil_set(self):
        """Creates a set of PF coil cases from a PF coils object"""
        pf_coils_set = paramak.PoloidalFieldCoilSet(
            heights=[10, 10, 20, 20],
            widths=[10, 10, 20, 40],
            center_points=[(100, 100),
                           (100, 150),
                           (50, 200),
                           (50, 50)],
            rotation_angle=180)

        test_shape = paramak.PoloidalFieldCoilCaseSetFC(
            pf_coils=pf_coils_set, casing_thicknesses=[
                5, 5, 10, 10], rotation_angle=180)

        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 4
        assert len(pf_coils_set.solid.Solids()) == 4

    def test_PoloidalFieldCoilCaseSetFC_incorrect_args(self):
        """creates a solid using the PoloidalFieldCoilCaseSetFC with the wrong number of casing_thicknesses"""
        def test_PoloidalFieldCoilSet_incorrect_lengths_FC():
            """Checks PoloidalFieldCoilSet with the wrong number of casing thicknesses using a coil set object"""
            pf_coils_set = paramak.PoloidalFieldCoilSet(
                heights=[10, 10, 20, 20],
                widths=[10, 10, 20, 40],
                center_points=[(100, 100),
                               (100, 150),
                               (50, 200),
                               (50, 50)],
                rotation_angle=180)

            paramak.PoloidalFieldCoilCaseSetFC(
                pf_coils=pf_coils_set, casing_thicknesses=[
                    5, 5, 10], rotation_angle=180).solid

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_lengths_FC)

        def test_PoloidalFieldCoilSet_incorrect_lengths():
            """Checks PoloidalFieldCoilSet with the wrong number of casing thicknesses using a list"""
            pf_coils_1 = paramak.PoloidalFieldCoil(
                height=10,
                width=10,
                center_point=(100, 100),
                rotation_angle=180)

            paramak.PoloidalFieldCoilCaseSetFC(
                pf_coils=[pf_coils_1],
                casing_thicknesses=[5, 5, 10, 10],
                rotation_angle=180).solid

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_lengths)

        def test_PoloidalFieldCoilSet_incorrect_pf_coil():
            """Checks PoloidalFieldCoilSet with the pf_coils as an incorrect entry"""
            paramak.PoloidalFieldCoilCaseSetFC(
                pf_coils=20,
                casing_thicknesses=[5, 5, 10, 10],
                rotation_angle=180).solid

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_pf_coil)

    def test_PoloidalFieldCoilCaseSetFC_from_list(self):
        """Creates a set of PF coil cases from a list of PF coils"""
        pf_coils_1 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 100),
                                               rotation_angle=180)

        pf_coils_2 = paramak.PoloidalFieldCoil(height=10,
                                               width=10,
                                               center_point=(100, 150),
                                               rotation_angle=180)

        pf_coils_3 = paramak.PoloidalFieldCoil(height=20,
                                               width=20,
                                               center_point=(50, 200),
                                               rotation_angle=180)

        pf_coils_4 = paramak.PoloidalFieldCoil(height=20,
                                               width=40,
                                               center_point=(50, 50),
                                               rotation_angle=180)

        test_shape = paramak.PoloidalFieldCoilCaseSetFC(
            pf_coils=[
                pf_coils_1, pf_coils_2, pf_coils_3, pf_coils_4], casing_thicknesses=[
                5, 5, 10, 10], rotation_angle=180)

        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 4
