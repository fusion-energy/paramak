
import paramak
import unittest


class test_PoloidalFieldCoilCaseFC(unittest.TestCase):
    def test_PoloidalFieldCoilCaseFC_creation(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that a cadquery solid is created."""

        pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=pf_coil, casing_thickness=5
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
