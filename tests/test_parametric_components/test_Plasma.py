
import os
import unittest
import pytest
from pathlib import Path

import paramak


class TestPlasma(unittest.TestCase):
    def test_plasma_attributes(self):
        """Creates a plasma object using the Plasma parametric component and
        checks that its attributes can be set correctly."""

        test_plasma = paramak.Plasma()

        assert isinstance(test_plasma.elongation, float)

        def test_plasma_elongation_min_setting():
            """checks ValueError is raised when an elongation < 0 is specified"""

            test_plasma.elongation = -1

        self.assertRaises(ValueError, test_plasma_elongation_min_setting)

        def test_plasma_elongation_max_setting():
            """checks ValueError is raised when an elongation > 4 is specified"""

            test_plasma.elongation = 400

        self.assertRaises(ValueError, test_plasma_elongation_max_setting)

        def minor_radius_out_of_range():
            """checks ValueError is raised when an minor_radius < 1 is
            specified"""

            test_plasma.minor_radius = 0.5

        self.assertRaises(ValueError, minor_radius_out_of_range)

        def major_radius_out_of_range():
            """checks ValueError is raised when an manor_radius < 1 is
            specified"""

            test_plasma.major_radius = 0.5

        self.assertRaises(ValueError, major_radius_out_of_range)

    def test_plasma_points_of_interest(self):
        test_plasma = paramak.Plasma(vertical_displacement=2)
        assert test_plasma.high_point == (
            test_plasma.major_radius -
            test_plasma.triangularity * test_plasma.minor_radius,
            test_plasma.elongation * test_plasma.minor_radius +
            test_plasma.vertical_displacement,
        )
        assert test_plasma.low_point == (
            test_plasma.major_radius -
            test_plasma.triangularity * test_plasma.minor_radius,
            -test_plasma.elongation * test_plasma.minor_radius +
            test_plasma.vertical_displacement,
        )
        assert test_plasma.outer_equatorial_point == (
            test_plasma.major_radius + test_plasma.minor_radius,
            test_plasma.vertical_displacement
        )
        assert test_plasma.inner_equatorial_point == (
            test_plasma.major_radius - test_plasma.minor_radius,
            test_plasma.vertical_displacement
        )

    def test_plasma_x_points(self):
        """Creates several plasmas with different configurations using the
        Plasma parametric component and checks the location of the x point for
        each."""

        for (
            triangularity,
            elongation,
            minor_radius,
            major_radius,
            vertical_displacement,
        ) in zip(
            [-0.7, 0, 0.5],  # triangularity
            [1, 1.5, 2],  # elongation
            [100, 200, 300],  # minor radius
            [300, 400, 600],  # major radius
            [0, -10, 5],
        ):  # displacement

            for config in ["non-null", "single-null", "double-null"]:

                # Run
                test_plasma = paramak.Plasma(
                    configuration=config,
                    triangularity=triangularity,
                    elongation=elongation,
                    minor_radius=minor_radius,
                    major_radius=major_radius,
                    vertical_displacement=vertical_displacement,
                )

                # Expected
                expected_lower_x_point, expected_upper_x_point = None, None
                if config == "single-null" or config == "double-null":
                    expected_lower_x_point = (1 -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              triangularity *
                                              minor_radius, -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              elongation *
                                              minor_radius +
                                              vertical_displacement, )

                    if config == "double-null":
                        expected_upper_x_point = (
                            expected_lower_x_point[0],
                            (1 +
                             test_plasma.x_point_shift) *
                            elongation *
                            minor_radius +
                            vertical_displacement,
                        )

                # Check
                for point, expected_point in zip(
                    [test_plasma.lower_x_point, test_plasma.upper_x_point],
                    [expected_lower_x_point, expected_upper_x_point],
                ):
                    assert point == expected_point

    def test_plasma_x_points_plasmaboundaries(self):
        """Creates several plasmas with different configurations using the
        PlasmaBoundaries parametric component and checks the location of the x
        point for each."""

        for A, triangularity, elongation, minor_radius, major_radius in zip(
            [0, 0.05, 0.05],  # A
            [-0.7, 0, 0.5],  # triangularity
            [1, 1.5, 2],  # elongation
            [100, 200, 300],  # minor radius
            [300, 400, 600],
        ):  # major radius

            for config in ["non-null", "single-null", "double-null"]:

                # Run
                test_plasma = paramak.PlasmaBoundaries(
                    configuration=config,
                    A=A,
                    triangularity=triangularity,
                    elongation=elongation,
                    minor_radius=minor_radius,
                    major_radius=major_radius,
                )

                # Expected
                expected_lower_x_point, expected_upper_x_point = None, None
                if config == "single-null" or config == "double-null":
                    expected_lower_x_point = (1 -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              triangularity *
                                              minor_radius, -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              elongation *
                                              minor_radius, )

                    if config == "double-null":
                        expected_upper_x_point = (
                            expected_lower_x_point[0],
                            -expected_lower_x_point[1],
                        )

                # Check
                for point, expected_point in zip(
                    [test_plasma.lower_x_point, test_plasma.upper_x_point],
                    [expected_lower_x_point, expected_upper_x_point],
                ):
                    assert point == expected_point

    def test_plasmaboundaries_solid(self):
        """Create a default PlasmaBoundaries shape and check a solid can be
        created"""
        test_plasma = paramak.PlasmaBoundaries()
        for config in ["non-null", "single-null", "double-null"]:
            test_plasma.configuration = config
            assert test_plasma.solid is not None

    def test_export_plasma_source(self):
        """Creates a plasma using the Plasma parametric component and checks a
        stp file of the shape can be exported using the export_stp method."""

        test_plasma = paramak.Plasma()

        os.system("rm plasma.stp")

        test_plasma.export_stp("plasma.stp")

        assert Path("plasma.stp").exists()
        os.system("rm plasma.stp")

    def test_export_plasma_from_points_export(self):
        """Creates a plasma using the PlasmaFromPoints parametric component
        and checks a stp file of the shape can be exported using the export_stp
        method."""

        test_plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=500,
            inner_equatorial_x_point=300,
            high_point=(400, 200),
            rotation_angle=180,
        )

        os.system("rm plasma.stp")

        test_plasma.export_stp("plasma.stp")
        assert test_plasma.high_point[0] > test_plasma.inner_equatorial_x_point
        assert test_plasma.high_point[0] < test_plasma.outer_equatorial_x_point
        assert test_plasma.outer_equatorial_x_point > test_plasma.inner_equatorial_x_point
        assert Path("plasma.stp").exists()
        os.system("rm plasma.stp")

    def test_plasma_relative_volume(self):
        """Creates plasmas using the Plasma parametric component and checks that
        the relative volumes of the solids created are correct"""

        test_plasma = paramak.Plasma()
        test_plasma_volume = test_plasma.volume
        test_plasma.rotation_angle = 180
        assert test_plasma.volume == pytest.approx(test_plasma_volume * 0.5)
