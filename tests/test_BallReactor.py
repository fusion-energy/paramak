
import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_BallReactor(unittest.TestCase):
    def test_BallReactor_creation_with_extra_blanket_needed(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_reactor = paramak.BallReactor(
                                        inner_bore_radial_thickness=50,
                                        inboard_tf_leg_radial_thickness = 200,
                                        center_column_shield_radial_thickness= 50,
                                        divertor_radial_thickness = 50,
                                        inner_plasma_gap_radial_thickness = 150,
                                        plasma_radial_thickness = 100,
                                        outer_plasma_gap_radial_thickness = 50,
                                        firstwall_radial_thickness=50,
                                        blanket_radial_thickness=100,
                                        blanket_rear_wall_radial_thickness=10,
                                        elongation=2,
                                        triangularity=0.55,
                                        number_of_tf_coils=16,
        )

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 14

    def test_BallReactor_creation_without_extra_blanket_needed(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_reactor = paramak.BallReactor(
                                        inner_bore_radial_thickness=50,
                                        inboard_tf_leg_radial_thickness = 200,
                                        center_column_shield_radial_thickness= 50,
                                        divertor_radial_thickness = 172.5,
                                        inner_plasma_gap_radial_thickness = 150,
                                        plasma_radial_thickness = 100,
                                        outer_plasma_gap_radial_thickness = 50,
                                        firstwall_radial_thickness=50,
                                        blanket_radial_thickness=100,
                                        blanket_rear_wall_radial_thickness=10,
                                        elongation=2,
                                        triangularity=0.55,
                                        number_of_tf_coils=16,
        )

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 8

    def test_BallReactor_svg_creation(self):
        os.system("rm test_ballreactor_image.svg")

        my_reactor = paramak.BallReactor(
                                        inner_bore_radial_thickness=50,
                                        inboard_tf_leg_radial_thickness = 200,
                                        center_column_shield_radial_thickness= 50,
                                        divertor_radial_thickness = 172.5,
                                        inner_plasma_gap_radial_thickness = 150,
                                        plasma_radial_thickness = 100,
                                        outer_plasma_gap_radial_thickness = 50,
                                        firstwall_radial_thickness=50,
                                        blanket_radial_thickness=100,
                                        blanket_rear_wall_radial_thickness=10,
                                        elongation=2,
                                        triangularity=0.55,
                                        number_of_tf_coils=16,
        )
        my_reactor.export_svg('test_ballreactor_image.svg')

        assert Path("test_ballreactor_image.svg").exists() is True
        os.system("rm test_ballreactor_image.svg")
