
import math
import unittest

import paramak
import pytest


class test_CoolantChannelRingStraight(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CoolantChannelRingStraight(
            height=100,
            channel_radius=10,
            ring_radius=70,
            number_of_coolant_channels=8
        )
    
    def test_CoolantChannelRingStraight_creation(self):
        """Creates a coolant channel ring using the CoolantChannelRingStraight parameteric shape
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_CoolantChannelRingStraight_faces(self):
        """Creates a CoolantChannelRingStraight shape and checks that the areas of its faces
        are correct."""

        self.test_shape.workplane = "XY"
        self.test_shape.rotation_axis = "Z"

        assert self.test_shape.area == pytest.approx(
            (((math.pi * (10**2)) * 2) + (math.pi * (10 * 2) * 100)) * 8)
        assert len(self.test_shape.areas) == 24
        assert self.test_shape.areas.count(pytest.approx(math.pi * (10**2))) == 16
        assert self.test_shape.areas.count(
            pytest.approx(math.pi * (10 * 2) * 100)) == 8

    def test_CoolantChannelRingStraight_volume(self):
        """Creates CoolantChannelRingStraight shapes and checks that the volumes are correct."""

        self.test_shape.workplane = "XY"
        self.test_shape.rotation_axis = "Z"

        assert self.test_shape.volume == pytest.approx(
            math.pi * (10 ** 2) * 100 * 8)
