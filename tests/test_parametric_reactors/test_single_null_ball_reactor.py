import unittest

import pytest

import paramak


class TestSingleNullBallReactor(unittest.TestCase):
    """tests functionality of the test_SingleNullBallReactor class"""

    def setUp(self):
        self.test_reactor = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=200,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=150,
            plasma_radial_thickness=100,
            outer_plasma_gap_radial_thickness=50,
            plasma_gap_vertical_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=10,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=4,
            rear_blanket_to_tf_gap=10,
            outboard_tf_coil_radial_thickness=10,
            outboard_tf_coil_poloidal_thickness=10,
            divertor_position="lower",
            rotation_angle=180,
            pf_coil_case_thicknesses=[10, 10, 10, 10],
            pf_coil_radial_thicknesses=[20, 50, 50, 20],
            pf_coil_vertical_thicknesses=[20, 50, 50, 20],
            pf_coil_radial_position=[500, 575, 575, 500],
            pf_coil_vertical_position=[300, 100, -100, -300],
        )

    def test_input_variable_names(self):
        """tests that the number of inputs variables is correct"""

        assert len(self.test_reactor.input_variables.keys()) == 25
        assert len(self.test_reactor.input_variable_names) == 25

    def test_single_null_ball_reactor_with_pf_and_tf_coils(self):
        """Checks that a SingleNullBallReactor with optional pf and tf coils can
        be created and that the correct number of components are produced."""

        assert len(self.test_reactor.shapes_and_components) == 16

    def test_single_null_ball_reactor_rotation_angle_impacts_volume(self):
        """Creates SingleNullBallReactors with different rotation angles and
        checks that the relative volumes of the components are correct."""

        self.test_reactor.rotation_angle = 90
        test_reactor_90_components = self.test_reactor.shapes_and_components
        self.test_reactor.rotation_angle = 180
        test_reactor_180_components = self.test_reactor.shapes_and_components

        for r90, r180 in zip(test_reactor_90_components, test_reactor_180_components):
            assert r90.volume() == pytest.approx(r180.volume() * 0.5, rel=0.1)

    def test_hash_value(self):
        """Creates a single null ball reactor and checks that all shapes in the
        reactor are created when .shapes_and_components is first called. Checks
        that when .shapes_and_components is called again with no changes to the
        reactor, the shapes in the reactor are not reconstructed and the
        previously constructed shapes are returned. Checks that when
        .shapes_and_components is called again with changes to the reactor, the
        shapes in the reactor are reconstructed and these new shapes are
        returned. Checks that the reactor_hash_value is only updated when the
        reactor is reconstruced."""

        assert self.test_reactor.reactor_hash_value is None
        # commented out as code inspector suggests all attributs should be
        # declaired in class init
        # for key in [
        #     "_plasma",
        #     "_inboard_tf_coils",
        #     "_center_column_shield",
        #     "_divertor_lower",
        #     "_firstwall",
        #     "_blanket",
        #     "_blanket_rear_wall",
        #     "_pf_coils",
        #     "_pf_coils_casing",
        #     "_tf_coil",
        # ]:
        #     assert key not in self.test_reactor.__dict__.keys()
        assert self.test_reactor.shapes_and_components is not None

        for key in [
            "_plasma",
            "_inboard_tf_coils",
            "_center_column_shield",
            "_divertor_lower",
            "_firstwall",
            "_blanket",
            "_blanket_rear_wall",
            "_pf_coils",
            "_pf_coils_casing",
            "_tf_coil",
        ]:
            assert key in self.test_reactor.__dict__.keys()
        assert len(self.test_reactor.shapes_and_components) == 16
        assert self.test_reactor.reactor_hash_value is not None
        initial_hash_value = self.test_reactor.reactor_hash_value
        self.test_reactor.rotation_angle = 270
        assert self.test_reactor.reactor_hash_value == initial_hash_value
        assert self.test_reactor.shapes_and_components is not None
        assert self.test_reactor.reactor_hash_value != initial_hash_value
