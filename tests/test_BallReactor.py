
import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_BallReactor(unittest.TestCase):
    def test_BallReactor_creation(self):
        """creates blanket from parametric shape and checks a solid is created"""

        test_shape = paramak.BallReactor(
            major_radius=300,
            minor_radius=100,
            elongation=2,
            triangularity=0.9,
            offset_from_plasma=20,
            blanket_thickness=100,
            center_column_shield_outer_radius=180,
            center_column_shield_inner_radius=120,
            number_of_tf_coils=16,
            divertor_width=100,
            rotation_angle = 180
        )

        test_shape.export_stp()

        assert len(test_shape.shapes_and_components) == 6
