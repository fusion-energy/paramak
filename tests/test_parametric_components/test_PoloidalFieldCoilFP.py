
import unittest

import paramak
import pytest


class TestPoloidalFieldCoilFP(unittest.TestCase):

    def test_shape_construction_and_volume(self):
        """Cuts a vessel cylinder with several different size port cutters."""

        test_component = paramak.PoloidalFieldCoilFP(
            corner_points=[(10, 10), (20, 22)])

        assert test_component.volume == pytest.approx(12063.715789784808)
        assert test_component.corner_points == [(10, 10), (20, 22)]
        assert test_component.solid is not None
