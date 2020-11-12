
import os
import math
import unittest
from pathlib import Path

import paramak
import pytest


class test_CoolantChannelRingStraight(unittest.TestCase):
    def test_CoolantChannelRingStraight_creation(self):
        """creates a coolant channel ring using the CoolantChannelRingStraight parametric shape
        and checks that a cadquery solid is created"""

        test_shape = paramak.CoolantChannelRingStraight(
            height=200,
            channel_radius=10,
            ring_radius=70,
            number_of_coolant_channels=8,
            workplane="XY"
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CoolantChannelRingStraight_faces(self):
        """creates a CoolantChannelRingStraight shape and checks that the areas of its faces
        are correct"""

        test_shape = paramak.CoolantChannelRingStraight(
            height=200,
            channel_radius=10,
            ring_radius=70,
            number_of_coolant_channels=1,
            workplane="XY"
        )

        assert test_shape.area == pytest.approx(
            ((math.pi * (10**2)) * 2) + (math.pi * (10 * 2) * 200))
        assert len(test_shape.areas) == 3
        assert test_shape.areas.count(pytest.approx(math.pi * (10**2))) == 2
        assert test_shape.areas.count(
            pytest.approx(math.pi * (10 * 2) * 200)) == 1

        test_shape.number_of_coolant_channels = 8
        assert test_shape.area == pytest.approx(
            (((math.pi * (10**2)) * 2) + (math.pi * (10 * 2) * 200)) * 8)
        assert len(test_shape.areas) == 24
        assert test_shape.areas.count(pytest.approx(math.pi * (10**2))) == 16
        assert test_shape.areas.count(
            pytest.approx(math.pi * (10 * 2) * 200)) == 8

    def test_CoolantChannelRingStraight_volume(self):
        """creates CoolantChannelRingStraight shapes and checks that the volumes are correct"""

        test_shape = paramak.CoolantChannelRingStraight(
            height=200,
            channel_radius=10,
            ring_radius=70,
            number_of_coolant_channels=8,
            workplane="XY"
        )
        assert test_shape.volume == pytest.approx(
            math.pi * (10 ** 2) * 200 * 8)

        test_shape = paramak.CoolantChannelRingStraight(
            height=100,
            channel_radius=20,
            ring_radius=70,
            number_of_coolant_channels=5,
            workplane="XY"
        )
        assert test_shape.volume == pytest.approx(
            math.pi * (20 ** 2) * 100 * 5)