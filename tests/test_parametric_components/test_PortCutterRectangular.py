
import unittest

import paramak


class TestPortCutterRectangular(unittest.TestCase):

    def test_creation(self):
        """Checks a PortCutterRectangular creation."""

        test_component = paramak.PortCutterRectangular(
            distance=3,
            z_pos=0,
            height=0.2,
            width=0.4,
            fillet_radius=0.02,
            azimuth_placement_angle=[0, 45, 90, 180]
        )

        assert test_component.solid is not None
