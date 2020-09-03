
import os
import unittest
from pathlib import Path
import warnings

import pytest

import paramak


class test_BallReactor(unittest.TestCase):
    def test_BallReactor_creation_with_narrow_divertor(self):
        """creates a ball reactor using the BallReactor parametric_reactor and checks
        the correct number of components are created"""

        test_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=200,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=150,
            plasma_radial_thickness=100,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=10,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=359,
        )

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 7

    def test_BallReactor_creation_with_wide_divertor(self):
        """checks whether a ball reactor with a wide divertor can be created using
        the BallReactor parametric_reactor, and that the correct number of components
        are created"""

        test_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=200,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=172.5,
            inner_plasma_gap_radial_thickness=150,
            plasma_radial_thickness=100,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=10,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=359,
        )

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 7

    def test_BallReactor_svg_creation(self):
        """creates a ball reactor using the BallReactor parametric_reactor and checks
        an svg image of the reactor can be exported"""

        os.system("rm test_ballreactor_image.svg")

        test_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=50,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=50,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=359,
        )
        test_reactor.export_svg("test_ballreactor_image.svg")

        assert Path("test_ballreactor_image.svg").exists() is True
        os.system("rm test_ballreactor_image.svg")

    def test_BallReactor_with_pf_coils(self):
        """checks whether a ball reactor with optional pf coils can be
        created using the BallReactor parametric_reactor, and that the correct
        number of components are created"""

        test_reactor = paramak.BallReactor(
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
            rotation_angle=359,
        )
        test_reactor.export_stp()
        assert len(test_reactor.shapes_and_components) == 11

    def test_BallReactor_with_pf_and_tf_coils(self):
        """checks whether a ball reactor with optional pf and tf coils can
        be created using the BallReactor parametric_reactor, and that the correct
        number of components are created"""

        test_reactor = paramak.BallReactor(
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
            outboard_tf_coil_radial_thickness=50,
            outboard_tf_coil_poloidal_thickness=50,
            rotation_angle=359,
        )
        test_reactor.export_stp()
        assert len(test_reactor.shapes_and_components) == 12

    def test_BallReactor_with_pf_and_tf_coils_export_physical_groups(self):
        """creates a ball reactor using the BallReactor parametric_reactor and
        checks that the export_physical_groups() method works"""

        test_reactor = paramak.BallReactor(
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
            outboard_tf_coil_radial_thickness=50,
            outboard_tf_coil_poloidal_thickness=50,
            rotation_angle=359,
        )
        test_reactor.export_physical_groups()

        # insert assertion

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
            rotation_angle=359,
        )
        assert len(test_reactor.shapes_and_components) == 12

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
            rotation_angle=359,
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
            rotation_angle=359,
        )

        assert len(test_reactor.shapes_and_components) == 7

    def test_rotation_angle_warning(self):
        """checks that the correct warning message is printed when
        rotation_angle = 360"""

        def warning_trigger():
            try:
                paramak.BallReactor(
                    inner_bore_radial_thickness=50,
                    inboard_tf_leg_radial_thickness=50,
                    center_column_shield_radial_thickness=50,
                    divertor_radial_thickness=100,
                    inner_plasma_gap_radial_thickness=50,
                    plasma_radial_thickness=200,
                    outer_plasma_gap_radial_thickness=50,
                    firstwall_radial_thickness=50,
                    blanket_radial_thickness=100,
                    blanket_rear_wall_radial_thickness=50,
                    elongation=2,
                    triangularity=0.55,
                    number_of_tf_coils=16,
                    rotation_angle=360,
                )
            except (RuntimeError, AttributeError):
                pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warning_trigger()
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "360 degree rotation may result in a Standard_ConstructionError or AttributeError" in str(
                w[-1].message)
