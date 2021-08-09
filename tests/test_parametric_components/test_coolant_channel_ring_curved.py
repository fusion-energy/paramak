
import unittest

import paramak
import pytest


class TestCoolantChannelRingCurved(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CoolantChannelRingCurved(
            height=100,
            channel_radius=10,
            ring_radius=70,
            mid_offset=-20,
            number_of_coolant_channels=6
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a CoolantChannelRingCurved are correct."""

        # assert self.test_shape.rotation_angle == 360
        assert self.test_shape.start_angle == 0
        assert self.test_shape.stp_filename == "CoolantChannelRingCurved.stp"
        assert self.test_shape.stl_filename == "CoolantChannelRingCurved.stl"
        assert self.test_shape.material_tag == "coolant_channel_mat"

    def test_creation(self):
        """Creates a coolant channel ring using the CoolantChannelRingCurved parametric shape
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_relative_volumes(self):
        """Creates coolant channel rings using the CoolantChannelRingCurved parametric shape
        and checks the relative volumes are correct."""

        test_volume = self.test_shape.volume
        self.test_shape.number_of_coolant_channels = 3
        assert test_volume == pytest.approx(self.test_shape.volume * 2)

        test_volume = self.test_shape.volume
        self.test_shape.mid_offset = -30
        assert test_volume > self.test_shape.volume
        self.test_shape.force_cross_section = True
        assert test_volume < self.test_shape.volume

    def test_start_angle(self):
        """Checks that the coolant channels are placed at the correct azimuthal placement
        angles for a given start angle."""

        assert self.test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300
        ]
        self.test_shape.start_angle = 10
        assert self.test_shape.azimuth_placement_angle == [
            10, 70, 130, 190, 250, 310
        ]
