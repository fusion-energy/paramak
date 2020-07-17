
import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_BallReactor(unittest.TestCase):
    def test_BallReactor_creation(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_shape = paramak.BallReactor(
                        inner_bore_radial_thickness=50,
                        inboard_tf_leg_radial_thickness = 200,
                        center_column_radial_thickness= 50,
                        inner_plasma_gap_radial_thickness = 200,
                        plasma_radial_thickness = 100,
                        outer_plasma_gap_radial_thickness = 50,
                        blanket_radial_thickness=100,
                        elongation=2,
                        triangularity=0.55,
                        number_of_tf_coils=16,
        )

        test_shape.export_stp()

        assert len(test_shape.shapes_and_components) == 6

    def test_BallReactor_creation(self):
        os.system("rm test_ballreactor_image.svg")
        my_reactor = paramak.BallReactor(
                                    inner_bore_radial_thickness=50,
                                    inboard_tf_leg_radial_thickness = 200,
                                    center_column_radial_thickness= 50,
                                    inner_plasma_gap_radial_thickness = 200,
                                    plasma_radial_thickness = 100,
                                    outer_plasma_gap_radial_thickness = 50,
                                    blanket_radial_thickness=100,
                                    elongation=2,
                                    triangularity=0.55,
                                    number_of_tf_coils=16,
        )
        my_reactor.export_svg('test_ballreactor_image.svg')

        assert Path("test_ballreactor_image.svg").exists() is True
        os.system("rm test_ballreactor_image.svg")
