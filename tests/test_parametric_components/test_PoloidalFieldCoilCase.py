
import paramak
import unittest


class test_PoloidalFieldCoilCase(unittest.TestCase):
    def test_PoloidalFieldCoilCase_creation(self):
        """creates a pf coil case using the PoloidalFieldCoilCase parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.PoloidalFieldCoilCase(
            casing_thickness=5,
            coil_height=50,
            coil_width=50,
            center_point=(
                1000,
                500))

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
