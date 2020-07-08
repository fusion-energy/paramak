
import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_SubmersionBallReactor(unittest.TestCase):
    def test_SubmersionBallReactor_creation(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_shape = paramak.SubmersionBallReactor(major_radius=300,
                                 minor_radius=100,
                                 offset_from_plasma=20,
                                 blanket_thickness=150,
                                 firstwall_thickness=10,
                                 center_column_shield_outer_radius=160,
                                 center_column_shield_inner_radius=100,
                                 number_of_tf_coils=16,
                                 casing_thickness=10
                                 )

        assert len(test_shape.shapes_and_components) == 7
