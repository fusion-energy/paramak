
import paramak
import unittest


class test_PoloidalFieldCoil(unittest.TestCase):
    def test_PoloidalFieldCoil_creation(self):
        """creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
