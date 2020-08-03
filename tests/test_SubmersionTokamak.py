
import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_SubmersionTokamak(unittest.TestCase):
    def test_SubmersionTokamak_creation_with_extra_blanket_needed(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=100,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outboard_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_radial_thicknesses=50,
            pf_coil_to_tf_coil_radial_gap=50,
            tf_coil_radial_thickness=50,
            # divertor_radial_thickness=50,
            tf_coil_poloidal_thickness=50,
            plasma_high_point=(50+50+50+100+50+50+100,350),
            # divertor_vertical_thickness=50,
            # tf_coil_to_rear_blanket_vertical_gap=50,
            # tf_coil_vertical_thickness=50,
            # pf_coil_vertical_thicknesses=50,
            # number_of_tf_coils=16,
            rotation_angle=180
        )

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 10

    def test_SubmersionTokamak_svg_creation(self):
        os.system("rm test_SubmersionTokamak_image.svg")

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=100,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outboard_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_radial_thicknesses=50,
            pf_coil_to_tf_coil_radial_gap=50,
            tf_coil_radial_thickness=50,
            # divertor_radial_thickness=50,
            tf_coil_poloidal_thickness=50,
            plasma_high_point=(50+50+50+100+50+50+100,350),
            # divertor_vertical_thickness=50,
            # tf_coil_to_rear_blanket_vertical_gap=50,
            # tf_coil_vertical_thickness=50,
            # pf_coil_vertical_thicknesses=50,
            # number_of_tf_coils=16,
            rotation_angle=180
        )
        test_reactor.export_svg('test_SubmersionTokamak_image.svg')

        assert Path("test_SubmersionTokamak_image.svg").exists() is True
        os.system("rm test_SubmersionTokamak_image.svg")

