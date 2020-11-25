
import unittest

import paramak
import pytest


class test_CoolantChannelRingCurved(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CoolantChannelRingCurved(
            height=100,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=8
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a CoolantChannelRingCurved are correct."""

        # assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "CoolantChannelRingCurved.stp"
        assert self.test_shape.stl_filename == "CoolantChannelRingCurved.stl"
        assert self.test_shape.material_tag == "coolant_channel_mat"

    def test_CoolantChannelRingCurved_creation(self):
        """Creates a coolant channel ring using the CoolantChannelRingCurved parametric shape
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_CoolantChannelRingCurved_relative_volumes(self):
        """Creates coolant channel rings using the CoolantChannelRingCurved parametric shape
        and checks the relative volumes are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.number_of_coolant_channels = 4
        assert test_volume == pytest.approx(self.test_shape.volume * 2)

        test_volume = self.test_shape.volume
        self.test_shape.mid_offset = -30
        assert test_volume > self.test_shape.volume
        self.test_shape.force_cross_section = True
        assert test_volume < self.test_shape.volume

    # need to add check to warn/raise error when there is coolant channel
    # overlap and a test
