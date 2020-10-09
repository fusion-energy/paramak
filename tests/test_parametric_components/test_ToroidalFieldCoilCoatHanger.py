
import paramak
import unittest


class test_ToroidalFieldCoilCoatHanger(unittest.TestCase):
    def test_ToroidalFieldCoilCoatHanger_creation(self):
        """creates a tf coil using the ToroidalFieldCoilCoatHanger parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_start_point=(700, 50),
            vertical_length=500,
            thickness=50,
            distance=50,
            number_of_coils=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
