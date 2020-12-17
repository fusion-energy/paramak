
import os
import unittest
from pathlib import Path

import paramak


class TestTFCoilCasing(unittest.TestCase):

    def setUp(self):
        inner_offset = 10
        outer_offset = 10
        magnet_thickness = 5
        magnet_extrude_distance = 10
        vertical_section_offset = 20
        casing_extrude_distance = magnet_extrude_distance * 2

        # create a princeton D magnet
        magnet = paramak.ToroidalFieldCoilPrincetonD(
            R1=100, R2=200, thickness=magnet_thickness,
            distance=magnet_extrude_distance, number_of_coils=1)

        self.test_shape = paramak.TFCoilCasing(
            magnet=magnet, distance=casing_extrude_distance,
            inner_offset=inner_offset, outer_offset=outer_offset,
            vertical_section_offset=vertical_section_offset)

    def test_creation(self):

        assert self.test_shape.solid is not None

    def test_export_stp(self):
        """Exports and stp file with mode = solid and wire and checks
        that the outputs exist and relative file sizes are correct."""

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")

        self.test_shape.export_stp('test_solid.stp', mode='solid')
        self.test_shape.export_stp('test_solid2.stp')
        self.test_shape.export_stp('test_wire.stp', mode='wire')

        assert Path("test_solid.stp").exists() is True
        assert Path("test_solid2.stp").exists() is True
        assert Path("test_wire.stp").exists() is True

        assert Path("test_solid.stp").stat().st_size == \
            Path("test_solid2.stp").stat().st_size
        assert Path("test_wire.stp").stat().st_size < \
            Path("test_solid2.stp").stat().st_size

        os.system("rm test_solid.stp test_solid2.stp test_wire.stp")
