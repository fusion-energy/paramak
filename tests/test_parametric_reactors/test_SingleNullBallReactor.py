
import unittest

import paramak
import pytest


class test_SingleNullBallReactor(unittest.TestCase):
    def test_SingleNullBallReactor_with_pf_and_tf_coils(self):
        """checks that a single null ball reactor with optional pf and tf
        coils can be created using the SingleNullBallReactor parametric_reactor,
        and that the correct number of components are produced"""

        test_reactor = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            divertor_position="lower",
            rotation_angle=360,
        )
        assert len(test_reactor.shapes_and_components) == 9

    def test_single_null_ball_reactor_divertor_lower(self):
        """checks that a single null reactor with a lower divertor can be
        created using the SingleNullBallReactor parametric_reactor"""

        test_reactor = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            divertor_position="lower",
            rotation_angle=360,
        )

        assert len(test_reactor.shapes_and_components) == 7

    def test_single_null_ball_reactor_divertor_upper(self):
        """checks that a single null reactor with an upper divertor can be
        created using the SingleNullBallReactor parametric_reactor"""

        test_reactor = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            divertor_position="upper",
            rotation_angle=360,
        )

        assert len(test_reactor.shapes_and_components) == 7

    def test_SingleNullBallReactor_rotation_angle_impacts_volume(self):
        """creates a single null ball reactor with a rotation angle of
        90 and another reactor with a rotation angle of 180. Then checks the
        volumes of all the components is double in the 180 reactor"""

        test_reactor_90 = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            divertor_position="upper",
            rotation_angle=90,
        )

        test_reactor_180 = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            divertor_position="upper",
            rotation_angle=180,
        )

        for r90, r180 in zip(test_reactor_90.shapes_and_components,
                             test_reactor_180.shapes_and_components):
            assert r90.volume == pytest.approx(r180.volume * 0.5, rel=0.1)

    def test_single_null_ball_reactor_error(self):
        """Trys to build a SingleNullBallReactor with an invalid divertor
        position and checks a ValueError is raised"""

        test_reactor = paramak.SingleNullBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            divertor_position="upper",
            rotation_angle=180,
        )

        def invalid_position():
            test_reactor.divertor_position = "coucou"

        self.assertRaises(ValueError, invalid_position)
