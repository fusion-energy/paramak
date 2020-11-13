
import os
import math
import unittest
from pathlib import Path

import paramak
import pytest


class test_CoolantChannelRingCurved(unittest.TestCase):
    def test_CoolantChannelRingCurved_creation(self):
        """creates a coolant channel ring using the CoolantChannelRingCurved parametric shape
        and checks that a cadquery solid is created"""

        test_shape = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=8
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CoolantChannelRingCurved_relative_volumes(self):
        """creates coolant channel rings using the CoolantChannelRingCurved parametric shape
        and checks the relative volumes are correct"""

        # number_of_coolant_channels
        test_shape_1 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=4
        )

        test_shape_2 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=8
        )
        assert test_shape_1.volume == pytest.approx(test_shape_2.volume * 0.5)

        test_shape_1 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=8
        )

        test_shape_2 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-30,
            number_of_coolant_channels=8
        )
        assert test_shape_1.volume > test_shape_2.volume

        test_shape_1 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=8,
            force_cross_section=True,
        )

        test_shape_2 = paramak.CoolantChannelRingCurved(
            height=200,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-30,
            number_of_coolant_channels=8,
            force_cross_section=True,
        )
        assert test_shape_1.volume < test_shape_2.volume
