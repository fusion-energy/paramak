
import unittest

import paramak


class test_TFCoilCasing(unittest.TestCase):

    def test_creation(self):
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

        casing = paramak.TFCoilCasing(
            magnet=magnet, distance=casing_extrude_distance,
            inner_offset=inner_offset, outer_offset=outer_offset,
            vertical_section_offset=vertical_section_offset)
        assert casing.solid is not None
