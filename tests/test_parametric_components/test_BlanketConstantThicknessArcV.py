
import paramak
import unittest


class test_BlanketConstantThicknessArcV(unittest.TestCase):
    def test_BlanketConstantThickness_creation(self):
        """Creates a blanket using the BlanketConstantThicknessArcV parametric
        component and checks that a cadquery solid is created."""

        test_shape = paramak.BlanketConstantThicknessArcV(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=180,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
