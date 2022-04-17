import unittest

import pytest

import paramak


class TestSingleNullSubmersionTokamak(unittest.TestCase):
    """Tests functionality of SingleNullSubmersionTokamak class"""

    def setUp(self):
        self.test_reactor = paramak.SingleNullSubmersionTokamak(
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
            support_radial_thickness=90,
            inboard_blanket_radial_thickness=30,
            outboard_blanket_radial_thickness=30,
            elongation=2.00,
            triangularity=0.50,
            pf_coil_case_thicknesses=[10, 10, 10, 10],
            pf_coil_radial_thicknesses=[20, 50, 50, 20],
            pf_coil_vertical_thicknesses=[20, 50, 50, 20],
            pf_coil_radial_position=[500, 550, 550, 500],
            pf_coil_vertical_position=[270, 100, -100, -270],
            rear_blanket_to_tf_gap=50,
            outboard_tf_coil_radial_thickness=30,
            outboard_tf_coil_poloidal_thickness=30,
            divertor_position="lower",
        )

    def test_input_variable_names(self):
        """tests that the number of inputs variables is correct"""

        assert len(self.test_reactor.input_variables.keys()) == 26
        assert len(self.test_reactor.input_variable_names) == 26

    def test_single_null_submersion_tokamak_with_pf_and_tf_coils(self):
        """Creates a SingleNullSubmersionTokamak with pf and tf coils and checks
        that the correct number of components are created."""

        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_case_thicknesses = [10, 20, 10, 10]
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.outboard_tf_coil_radial_thickness = 100
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 50
        self.test_reactor.number_of_tf_coils = 16

        assert len(self.test_reactor.shapes_and_components) == 17

    def test_single_null_submersion_tokamak_rotation_angle_impacts_volume(self):
        """Creates SingleNullSubmersionTokamaks with different rotation angles and
        checks that the relative volumes of the components are correct."""

        self.test_reactor.rotation_angle = 90
        comps_90_vol = [comp.volume() for comp in self.test_reactor.shapes_and_components]
        self.test_reactor.rotation_angle = 180
        comps_180_vol = [comp.volume() for comp in self.test_reactor.shapes_and_components]

        for vol_90, vol_180 in zip(comps_90_vol, comps_180_vol):
            assert vol_90 == pytest.approx(vol_180 * 0.5, rel=0.1)

    def test_hash_value(self):
        """Creates a single null submersion reactor and checks that all shapes
        in the reactor are created when .shapes_and_components is first called.
        Checks that when .shapes_and_components is called again with no changes
        to the reactor, the shapes in the reactor are reconstructed and the
        previously constructed shapes are returned. Checks that when
        .shapes_and_components is called again with changes to the reactor,
        the shapes in the reactor are reconstructed and these new shapes are
        returned. Checks that the reactor_hash_value is only updated when the
        reactor is reconstructed."""

        self.test_reactor.pf_coil_radial_thicknesses = [30, 30, 30, 30]
        self.test_reactor.pf_coil_vertical_thicknesses = [30, 30, 30, 30]
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.pf_coil_case_thicknesses = [10, 20, 20, 30]
        self.test_reactor.outboard_tf_coil_radial_thickness = 30
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 30
        self.test_reactor.number_of_tf_coils = 16

        assert self.test_reactor.reactor_hash_value is None
        # commented out as code inspector suggests all attributs should be
        # declaired in class init
        # for key in [
        #     "_inboard_tf_coils",
        #     "_center_column_shield",
        #     "_plasma",
        #     "_inboard_firstwall",
        #     "_inboard_blanket",
        #     "_firstwall",
        #     "_divertor_lower",
        #     "_blanket",
        #     "_supports",
        #     "_outboard_rear_blanket_wall_upper",
        #     "_outboard_rear_blanket_wall_lower",
        #     "_outboard_rear_blanket_wall",
        #     "_tf_coil",
        #     "_pf_coils",
        #     "_pf_coils_casing",
        # ]:
        #     assert key not in self.test_reactor.__dict__.keys()
        assert self.test_reactor.shapes_and_components is not None

        for key in [
            "_inboard_tf_coils",
            "_center_column_shield",
            "_plasma",
            "_inboard_firstwall",
            "_inboard_blanket",
            "_firstwall",
            "_divertor_lower",
            "_blanket",
            "_supports",
            "_outboard_rear_blanket_wall_upper",
            "_outboard_rear_blanket_wall_lower",
            "_outboard_rear_blanket_wall",
            "_tf_coil",
            "_pf_coils",
            "_pf_coils_casing",
        ]:
            assert key in self.test_reactor.__dict__.keys()
        assert len(self.test_reactor.shapes_and_components) == 17
        assert self.test_reactor.reactor_hash_value is not None
        initial_hash_value = self.test_reactor.reactor_hash_value
        self.test_reactor.rotation_angle = 270
        assert self.test_reactor.reactor_hash_value == initial_hash_value
        assert self.test_reactor.shapes_and_components is not None
        assert self.test_reactor.reactor_hash_value != initial_hash_value
