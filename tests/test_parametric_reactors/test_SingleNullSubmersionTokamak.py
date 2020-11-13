
import unittest

import paramak
import pytest


class test_SingleNullSubmersionTokamak(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(test_SingleNullSubmersionTokamak, self).__init__(*args, **kwargs)
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
            elongation=1.9,
            triangularity=0.65,
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
        assert len(test_reactor.shapes_and_components) == 11

    def test_SingleNullSubmersionTokamak_divertor_lower_support_lower(self):
        """creates a single null submersion reactor with lower supports and
        divertor using the SingleNullSubmersionTokamak parametric reactor and
        checks that the correct number of components are created"""

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
            elongation=2.5,
            triangularity=0.7,
            divertor_position="lower",
            support_position="lower",
            rotation_angle=359,
        )
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
            elongation=2.4,
            triangularity=0.5,
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
            elongation=2.3,
            triangularity=0.45,
            divertor_position="upper",
            support_position="upper",
            rotation_angle=180,
        )

        for r90, r180 in zip(test_reactor_90.shapes_and_components,
                             test_reactor_180.shapes_and_components):
            assert r90.volume == pytest.approx(r180.volume * 0.5, rel=0.1)

    def test_SubmersionTokamak_error_divertor_pos(self):
        test_reactor = self.SingleNullSubmersionTokamak

        def invalid_divertor_position():
            test_reactor.divertor_position = "coucou"

        self.assertRaises(ValueError, invalid_divertor_position)

        def invalid_support_position():
            test_reactor.support_position = "coucou"

        self.assertRaises(ValueError, invalid_support_position)

    def test_SingleNullSubmersionTokamak_hash_value(self):
        """Creates a single null submersion reactor and checks that all shapes in the reactor
        are created when .shapes_and_components is first called. Checks that when
        .shapes_and_components is called again with no changes to the reactor, the shapes in
        the reactor are reconstructed and the previously constructed shapes are returned.
        Checks that when .shapes_and_components is called again with changes to the reactor,
        the shapes in the reactor are reconstructed and these new shapes are returned. Checks
        that the reactor_hash_value is only updated when the reactor is reconstructed."""

        test_reactor = paramak.SingleNullSubmersionTokamak(
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
            divertor_position="upper",
            support_position="upper"
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
            "_pf_coils_casing",
            "_pf_coil",
            "_pf_coils_casing",
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
            "_pf_coils_casing",
            "_pf_coils_casing",
            "_pf_coil",
        ]:
            assert key in test_reactor.__dict__.keys()
        assert len(test_reactor.shapes_and_components) == 10
        assert test_reactor.reactor_hash_value is not None
        initial_hash_value = test_reactor.reactor_hash_value
        test_reactor.rotation_angle = 270
        assert test_reactor.reactor_hash_value == initial_hash_value
        assert test_reactor.shapes_and_components is not None
        assert test_reactor.reactor_hash_value != initial_hash_value
