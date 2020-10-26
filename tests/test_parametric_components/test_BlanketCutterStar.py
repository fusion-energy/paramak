
import paramak
import unittest


class test_BlanketCutterStar(unittest.TestCase):
    def test_BlanketCutterStar_creation(self):
        """creates a pf coil using the BlanketCutterStar parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.BlanketCutterStar(
            distance=100)

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
