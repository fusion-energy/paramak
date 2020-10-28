
import os
import unittest
import warnings
from pathlib import Path

import paramak
import pytest


class test_SubmersionTokamak(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(test_SubmersionTokamak, self).__init__(*args, **kwargs)
        self.Submersion_Tokamak_reactor = paramak.SubmersionTokamak(
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
            rotation_angle=359,
        )

        self.SingleNullSubmersionTokamak = paramak.SingleNullSubmersionTokamak(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            number_of_tf_coils=16,
            support_radial_thickness=20,
            inboard_blanket_radial_thickness=20,
            outboard_blanket_radial_thickness=20,
            plasma_high_point=(200, 200),
            divertor_position="upper",
            support_position="upper",
            rotation_angle=359,
        )

    def test_SubmersionTokamak_svg_creation(self):
        """creates a submersion reactor using the SubmersionTokamak parametric
        reactor and checks that an svg file of the reactor can be exported
        using the export_svg method"""

        os.system("rm test_SubmersionTokamak_image.svg")

        test_reactor = self.Submersion_Tokamak_reactor
        test_reactor.export_svg("test_SubmersionTokamak_image.svg")

        assert Path("test_SubmersionTokamak_image.svg").exists() is True
        os.system("rm test_SubmersionTokamak_image.svg")

    def test_minimal_SubmersionTokamak_creation(self):
        """creates a submersion reactor using the SubmersionTokamak parametric
        reactor and checks that the correct number of components are created"""

        test_reactor = self.Submersion_Tokamak_reactor

        assert len(test_reactor.shapes_and_components) == 8

    def test_SubmersionTokamak_with_tf_coils_creation(self):
        """creates a submersion reactor with tf coils using the
        SubmersionTokamak parametric reactor and checks that the correct number
        of components are created"""

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
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            outboard_tf_coil_poloidal_thickness=70,
            number_of_tf_coils=4,
            rotation_angle=359,
        )
        assert len(test_reactor.shapes_and_components) == 9

    def test_SubmersionTokamak_with_tf_and_pf_coils_creation(self):
        """creates a submersion reactor with tf and pf coils using the
        Submersion Tokamak parametric reactor and checks that the correct
        number of components are created"""

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
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            outboard_tf_coil_poloidal_thickness=70,
            pf_coil_vertical_thicknesses=[50, 50, 50, 50, 50],
            pf_coil_radial_thicknesses=[40, 40, 40, 40, 40],
            pf_coil_to_tf_coil_radial_gap=50,
            number_of_tf_coils=4,
            rotation_angle=359,
        )
        assert len(test_reactor.shapes_and_components) == 10

    def test_minimal_SubmersionTokamak_stp_creation(self):
        """creates a submersion reactor using the SubmersionTokamak parameteric
        reactor and checks that stp files of all components can be exported
        using the export_stp method"""

        os.system("rm -r minimal_SubmersionTokamak")

        test_reactor = self.Submersion_Tokamak_reactor
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
        """creates a submersion reactor with pf coils using the
        SubmersionTokamak parametric reactor and checks that stp files of all
        components can be exported using the export_stp method"""

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
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            outboard_tf_coil_poloidal_thickness=70,
            number_of_tf_coils=4,
            rotation_angle=359
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
        """creates a submersion reactor with tf and pf coils using the
        SubmersionTokamak parametric reactor and checks that stp files of all
        components can be exported using the export_stp method"""

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
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            outboard_tf_coil_poloidal_thickness=70,
            pf_coil_vertical_thicknesses=[50, 50, 50, 50, 50],
            pf_coil_radial_thicknesses=[40, 40, 40, 40, 40],
            pf_coil_to_tf_coil_radial_gap=50,
            number_of_tf_coils=4,
            rotation_angle=359,
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

    def test_SingleNullSubmersionTokamak_with_pf_and_tf_coils(self):
        """creates a single null submersion reactor with pf and tf coils using
        the SingleNullSubmersionTokamak parametric reactor and checks that the
        correct number of components are created"""

        test_reactor = paramak.SingleNullSubmersionTokamak(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            number_of_tf_coils=16,
            support_radial_thickness=20,
            inboard_blanket_radial_thickness=20,
            outboard_blanket_radial_thickness=20,
            plasma_high_point=(200, 200),
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=20,
            divertor_position="upper",
            support_position="upper",
            rotation_angle=359,
        )
        assert len(test_reactor.shapes_and_components) == 10

    def test_SingleNullSubmersionTokamak_divertor_lower_support_lower(self):
        """creates a single null submersion reactor with lower supports and
        divertor using the SingleNullSubmersionTokamak parametric reactor and
        checks that the correct number of components are created"""

        test_reactor = self.SingleNullSubmersionTokamak
        test_reactor.divertor_position = "lower"
        test_reactor.support_position = "lower"
        assert len(test_reactor.shapes_and_components) == 8

    def test_SingleNullSubmersionTokamak_divertor_upper_support_upper(self):
        """creates a single null submersion reactor with upper supports and
        divertor using the SingleNullSubmersionTokamak parametric reactor and
        checks that the correct number of components are created"""

        test_reactor = self.SingleNullSubmersionTokamak
        assert len(test_reactor.shapes_and_components) == 8

    def test_SingleNullSubmersionTokamak_rotation_angle_impacts_volume(self):
        """creates a single null submersion reactor with a rotation angle of
        90 and another reactor with a rotation angle of 180. Then checks the
        volumes of all the components is double in the 180 reactor"""

        test_reactor_90 = paramak.SingleNullSubmersionTokamak(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            number_of_tf_coils=16,
            support_radial_thickness=20,
            inboard_blanket_radial_thickness=20,
            outboard_blanket_radial_thickness=20,
            plasma_high_point=(200, 200),
            divertor_position="upper",
            support_position="upper",
            rotation_angle=90,
        )

        test_reactor_180 = paramak.SingleNullSubmersionTokamak(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            number_of_tf_coils=16,
            support_radial_thickness=20,
            inboard_blanket_radial_thickness=20,
            outboard_blanket_radial_thickness=20,
            plasma_high_point=(200, 200),
            divertor_position="upper",
            support_position="upper",
            rotation_angle=180,
        )

        for r90, r180 in zip(test_reactor_90.shapes_and_components,
                             test_reactor_180.shapes_and_components):
            assert r90.volume == pytest.approx(r180.volume * 0.5, rel=0.1)

    def test_rotation_angle_warning(self):
        """checks that the correct warning message is printed when
        rotation_angle = 360"""

        def warning_trigger():
            try:
                paramak.SubmersionTokamak(
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
                    plasma_high_point=(
                        50 + 50 + 50 + 100 + 50 + 50 + 100,
                        350),
                    rotation_angle=360,
                )
            except BaseException:
                pass
        msg = "360 degree rotation may result in a " + \
            "Standard_ConstructionError or AttributeError"
        with pytest.warns(UserWarning, match=msg):
            warning_trigger()

    def test_SubmersionTokamak_error_divertor_pos(self):
        test_reactor = self.SingleNullSubmersionTokamak

        def invalid_divertor_position():
            test_reactor.divertor_position = "coucou"

        self.assertRaises(ValueError, invalid_divertor_position)

        def invalid_support_position():
            test_reactor.support_position = "coucou"

        self.assertRaises(ValueError, invalid_support_position)

    def test_plasma_high_point_error(self):
        """checks that error are raised when invalid plasma_high_point is set
        """
        test_reactor = self.Submersion_Tokamak_reactor

        def small_plasma_high_point():
            test_reactor.plasma_high_point = (1, 240)
            test_reactor._make_vertical_build()

        def large_plasma_high_point():
            test_reactor.plasma_high_point = (1000, 240)
            test_reactor._make_vertical_build()

        self.assertRaises(ValueError, small_plasma_high_point)
        self.assertRaises(ValueError, large_plasma_high_point)
