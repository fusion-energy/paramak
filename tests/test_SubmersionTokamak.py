import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_SubmersionTokamak(unittest.TestCase):
    def test_SubmersionTokamak_svg_creation(self):
        """creates a SubmersionTokamak and checks a solids are created and export_svg produces a file"""
        os.system("rm test_SubmersionTokamak_image.svg")

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=100,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            divertor_radial_thickness=100,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            support_radial_thickness=150,
            plasma_high_point=(50 + 50 + 50 + 100 + 50 + 50 + 100, 350),
            rotation_angle=180,
        )
        test_reactor.export_svg("test_SubmersionTokamak_image.svg")

        assert Path("test_SubmersionTokamak_image.svg").exists() is True
        os.system("rm test_SubmersionTokamak_image.svg")

    def test_minimal_SubmersionTokamak_creation(self):
        """creates a SubmersionTokamak from parametric shape and checks solids are created"""

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=100,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            divertor_radial_thickness=100,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            support_radial_thickness=150,
            plasma_high_point=(50 + 50 + 50 + 100 + 50 + 50 + 100, 350),
            rotation_angle=180,
        )

        assert len(test_reactor.shapes_and_components) == 8

    def test_SubmersionTokamak_with_tf_coils_creation(self):
        """creates a SubmersionTokamak with TF coils and checks solids are created"""
        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=50,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            divertor_radial_thickness=50,
            plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
            rotation_angle=180,
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            tf_coil_poloidal_thickness=70,
            number_of_tf_coils=4,
        )
        assert len(test_reactor.shapes_and_components) == 9

    def test_SubmersionTokamak_with_tf_and_pf_coils_creation(self):
        """creates a SubmersionTokamak with TF and PF coils and checks solids are created"""
        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=50,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            divertor_radial_thickness=50,
            plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
            rotation_angle=180,
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            tf_coil_poloidal_thickness=70,
            pf_coil_vertical_thicknesses=[50, 50, 50, 50, 50],
            pf_coil_radial_thicknesses=[40, 40, 40, 40, 40],
            pf_coil_to_tf_coil_radial_gap=50,
            number_of_tf_coils=4,
        )
        assert len(test_reactor.shapes_and_components) == 14

    def test_minimal_SubmersionTokamak_stp_creation(self):
        """creates a SubmersionTokamak from parametric shape and checks solids are created"""

        os.system("rm -r minimal_SubmersionTokamak")

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=100,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            divertor_radial_thickness=100,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            support_radial_thickness=150,
            plasma_high_point=(50 + 50 + 50 + 100 + 50 + 50 + 100, 350),
            rotation_angle=180,
        )
        test_reactor.export_stp("minimal_SubmersionTokamak")

        output_filenames = [
            "minimal_SubmersionTokamak/inboard_tf_coils.stp",
            "minimal_SubmersionTokamak/center_column_shield.stp",
            "minimal_SubmersionTokamak/plasma.stp",
            "minimal_SubmersionTokamak/divertor.stp",
            "minimal_SubmersionTokamak/outboard_firstwall.stp",
            "minimal_SubmersionTokamak/supports.stp",
            "minimal_SubmersionTokamak/blanket.stp",
            "minimal_SubmersionTokamak/outboard_rear_blanket_wall.stp",
            "minimal_SubmersionTokamak/Graveyard.stp",
        ]

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r minimal_SubmersionTokamak")

    def test_SubmersionTokamak_with_pf_coils_stp_creation(self):
        """creates a SubmersionTokamak with PF coils and checks stp files are created"""

        os.system("rm -r pf_SubmersionTokamak")

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=50,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            divertor_radial_thickness=50,
            plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
            rotation_angle=180,
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            tf_coil_poloidal_thickness=70,
            number_of_tf_coils=4,
        )
        test_reactor.export_stp("pf_SubmersionTokamak")

        output_filenames = [
            "pf_SubmersionTokamak/inboard_tf_coils.stp",
            "pf_SubmersionTokamak/center_column_shield.stp",
            "pf_SubmersionTokamak/plasma.stp",
            "pf_SubmersionTokamak/divertor.stp",
            "pf_SubmersionTokamak/outboard_firstwall.stp",
            "pf_SubmersionTokamak/supports.stp",
            "pf_SubmersionTokamak/blanket.stp",
            "pf_SubmersionTokamak/outboard_rear_blanket_wall.stp",
            "pf_SubmersionTokamak/Graveyard.stp",
        ]

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r pf_SubmersionTokamak")

    def test_SubmersionTokamak_with_tf_and_pf_coils_stp_creation(self):
        """creates a SubmersionTokamak with TF and PF coils and checks STP files are created"""

        os.system("rm -r tf_pf_SubmersionTokamak")

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=25,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            inboard_blanket_radial_thickness=50,
            firstwall_radial_thickness=50,
            inner_plasma_gap_radial_thickness=70,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=70,
            outboard_blanket_radial_thickness=200,
            blanket_rear_wall_radial_thickness=50,
            divertor_radial_thickness=50,
            plasma_high_point=(50 + 50 + 50 + 100 + 100, 350),
            rotation_angle=180,
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            tf_coil_poloidal_thickness=70,
            pf_coil_vertical_thicknesses=[50, 50, 50, 50, 50],
            pf_coil_radial_thicknesses=[40, 40, 40, 40, 40],
            pf_coil_to_tf_coil_radial_gap=50,
            number_of_tf_coils=4,
        )
        test_reactor.export_stp("tf_pf_SubmersionTokamak")

        output_filenames = [
            "tf_pf_SubmersionTokamak/inboard_tf_coils.stp",
            "tf_pf_SubmersionTokamak/center_column_shield.stp",
            "tf_pf_SubmersionTokamak/plasma.stp",
            "tf_pf_SubmersionTokamak/divertor.stp",
            "tf_pf_SubmersionTokamak/outboard_firstwall.stp",
            "tf_pf_SubmersionTokamak/supports.stp",
            "tf_pf_SubmersionTokamak/blanket.stp",
            "tf_pf_SubmersionTokamak/outboard_rear_blanket_wall.stp",
            "tf_pf_SubmersionTokamak/Graveyard.stp",
        ]

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r tf_pf_SubmersionTokamak")
