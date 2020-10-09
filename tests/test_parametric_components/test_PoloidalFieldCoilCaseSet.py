
import paramak
import unittest


class test_PoloidalFieldCoilCaseSet(unittest.TestCase):
    def test_PoloidalFieldCoilCaseSet_creation(self):
        """Creates a set of PF coils by providing all required args"""
        test_shape = paramak.PoloidalFieldCoilCaseSet(
            heights=[10, 10, 20, 20],
            widths=[10, 10, 20, 40],
            casing_thicknesses=[5, 5, 10, 10],
            center_points=[(100, 100),
                           (100, 150),
                           (50, 200),
                           (50, 50)],
            rotation_angle=180)

        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 4
