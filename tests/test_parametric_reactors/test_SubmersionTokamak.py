
import os
import unittest
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
            elongation=2.3,
            triangularity=0.45,
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
            elongation=2.3,
            triangularity=0.45,
            divertor_position="upper",
            support_position="upper",
            rotation_angle=359,
        )

    def test_svg_creation(self):
        """creates a submersion reactor using the SubmersionTokamak parametric
        reactor and checks that an svg file of the reactor can be exported
        using the export_svg method"""

        os.system("rm test_image.svg")

        test_reactor = self.Submersion_Tokamak_reactor
        test_reactor.export_svg("test_image.svg")

        assert Path("test_image.svg").exists() is True
        os.system("rm test_image.svg")

    def test_minimal_creation(self):
        """creates a submersion reactor using the SubmersionTokamak parametric
        reactor and checks that the correct number of components are created"""

        test_reactor = self.Submersion_Tokamak_reactor

        assert len(test_reactor.shapes_and_components) == 8

    def test_with_tf_coils_creation(self):
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
            elongation=2.3,
            triangularity=0.45,
            support_radial_thickness=150,
            outboard_tf_coil_radial_thickness=50,
            tf_coil_to_rear_blanket_radial_gap=50,
            outboard_tf_coil_poloidal_thickness=70,
            number_of_tf_coils=4,
            rotation_angle=359,
        )
        assert len(test_reactor.shapes_and_components) == 9

    def test_with_tf_and_pf_coils_creation(self):
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
            elongation=2.3,
            triangularity=0.45,
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
        assert len(test_reactor.shapes_and_components) == 11

    def test_minimal_stp_creation(self):
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

    def test_with_pf_coils_stp_creation(self):
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
            elongation=2.3,
            triangularity=0.45,
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

    def test_with_tf_and_pf_coils_stp_creation(self):
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
            elongation=2.3,
            triangularity=0.45,
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
                    elongation=2.3,
                    triangularity=0.45,
                    rotation_angle=360,
                )._rotation_angle_check()
            except BaseException:
                pass
        msg = "360 degree rotation may result in a " + \
            "Standard_ConstructionError or AttributeError"
        with pytest.warns(UserWarning, match=msg):
            warning_trigger()

    def test_submersion_reactor_hash_value(self):
        """Creates a submersion reactor and checks that all shapes in the reactor are created
        when .shapes_and_components is first called. Checks that when .shapes_and_components
        is called again with no changes to the reactor, the shapes in the reactor are
        reconstructed and the previously constructed shapes are returned. Checks that when
        .shapes_and_components is called again with no changes to the reactor, the shapes in
        the reactor are reconstructed and these new shapes are returned. Checks that the
        reactor_hash_value is only updated when the reactor is reconstructed."""

        test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=30,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=30,
            divertor_radial_thickness=80,
            inner_plasma_gap_radial_thickness=50,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            number_of_tf_coils=16,
            rotation_angle=180,
            support_radial_thickness=50,
            inboard_blanket_radial_thickness=30,
            outboard_blanket_radial_thickness=30,
            elongation=2.4,
            triangularity=0.5,
            pf_coil_radial_thicknesses=[30, 30, 30, 30],
            pf_coil_vertical_thicknesses=[30, 30, 30, 30],
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=30,
            outboard_tf_coil_poloidal_thickness=30,
            tf_coil_to_rear_blanket_radial_gap=20,
        )

        assert test_reactor.reactor_hash_value is None
        for key in [
            "_inboard_tf_coils",
            "_center_column_shield",
            "_plasma",
            "_inboard_firstwall",
            "_inboard_blanket",
            "_firstwall",
            "_divertor",
            "_blanket",
            "_supports",
            "_outboard_rear_blanket_wall_upper",
            "_outboard_rear_blanket_wall_lower",
            "_outboard_rear_blanket_wall",
            "_tf_coil",
            "_pf_coil"
        ]:
            assert key not in test_reactor.__dict__.keys()

        assert test_reactor.shapes_and_components is not None
        for key in [
            "_inboard_tf_coils",
            "_center_column_shield",
            "_plasma",
            "_inboard_firstwall",
            "_inboard_blanket",
            "_firstwall",
            "_divertor",
            "_blanket",
            "_supports",
            "_outboard_rear_blanket_wall_upper",
            "_outboard_rear_blanket_wall_lower",
            "_outboard_rear_blanket_wall",
            "_tf_coil",
            "_pf_coil"
        ]:
            assert key in test_reactor.__dict__.keys()

        assert len(test_reactor.shapes_and_components) == 11
        assert test_reactor.reactor_hash_value is not None
        initial_hash_value = test_reactor.reactor_hash_value
        test_reactor.rotation_angle = 270
        assert test_reactor.reactor_hash_value == initial_hash_value
        assert test_reactor.shapes_and_components is not None
        assert test_reactor.reactor_hash_value != initial_hash_value
