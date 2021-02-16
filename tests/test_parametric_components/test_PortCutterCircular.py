import math
import unittest

import paramak

import pytest


class TestPortCutterCircular(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.PortCutterCircular(
            distance=300, radius=20
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PortCutterCircular are correct."""

        assert self.test_shape.center_point == (0, 0)
        assert self.test_shape.workplane == "ZY"
        assert self.test_shape.rotation_axis == "Z"
        assert self.test_shape.extrusion_start_offset == 1
        assert self.test_shape.stp_filename == "PortCutterCircular.stp"
        assert self.test_shape.stl_filename == "PortCutterCircular.stl"
        assert self.test_shape.name == "circular_port_cutter"
        assert self.test_shape.material_tag == "circular_port_cutter_mat"

    def test_creation(self):
        """Creates a circular port cutter using the PortCutterCircular parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_relative_volume(self):
        """Creates PortCutterCircular shapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume

        self.test_shape.extrusion_start_offset = 20
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert self.test_shape.volume == pytest.approx(test_volume * 4)

    def test_absolute_volume(self):
        """Creates a PortCutterCircular shape and checks that its volume is correct."""

        assert self.test_shape.volume == pytest.approx(math.pi * (20**2) * 300)

        self.test_shape.extrusion_start_offset = 20
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.radius = 10

        assert self.test_shape.volume == pytest.approx(
            math.pi * (10**2) * 300 * 4)
