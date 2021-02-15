
import unittest

import paramak

import pytest


class TestPortCutterRectangular(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.PortCutterRectangular(
            width=20, height=40, distance=300
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PortCutterRectangular are correct."""

        assert self.test_shape.center_point == (0, 0)
        assert self.test_shape.workplane == "ZY"
        assert self.test_shape.rotation_axis == "Z"
        assert self.test_shape.extrusion_start_offset == 1
        assert self.test_shape.fillet_radius is None
        assert self.test_shape.stp_filename == "PortCutterRectangular.stp"
        assert self.test_shape.stl_filename == "PortCutterRectangular.stl"
        assert self.test_shape.name == "rectangular_port_cutter"
        assert self.test_shape.material_tag == "rectangular_port_cutter_mat"

    def test_creation(self):
        """Creates a rectangular port cutter using the PortCutterRectangular parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_relative_volume(self):
        """Creates PortCutterRectangular shapes and checks that their relative volumes
        are correct."""

        test_volume = self.test_shape.volume

        self.test_shape.extrusion_start_offset = 20
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert self.test_shape.volume == pytest.approx(test_volume * 4)

    def test_absolute_volume(self):
        """Creates a PortCutterRectangular shape and checks that its volume is correct."""

        assert self.test_shape.volume == pytest.approx(20 * 40 * 300)

        self.test_shape.extrusion_start_offset = 20
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.width = 20
        self.test_shape.height = 20

        assert self.test_shape.volume == pytest.approx(20 * 20 * 300 * 4)

    def test_workplane(self):
        """Creates PortCutterRectangular shapes in different workplanes and checks that
        the geometries are correct."""

        cutting_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 50), (500, 50), (500, 0)],
            workplane="YZ",
        )
        self.test_shape.cut = cutting_shape

        assert self.test_shape.volume == pytest.approx(20 * 40 * 300 * 0.5)

        self.test_shape.workplane = "XZ"
        cutting_shape.workplane = "YZ"

        assert self.test_shape.volume == pytest.approx(20 * 40 * 300 * 0.5)

    def test_filleting(self):
        """Creates a PortCutterRectangular shape with filleted edges and checks
        that its volume is correct."""

        test_volume = self.test_shape.volume
        self.test_shape.fillet_radius = 5

        assert self.test_shape.volume < test_volume
        self.test_shape.workplane = "ZX"
        assert self.test_shape.volume < test_volume
        self.test_shape.workplane = "YX"
        assert self.test_shape.volume < test_volume
