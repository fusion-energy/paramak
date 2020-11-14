
import os
import unittest
import warnings
from pathlib import Path

import paramak
import pytest


class test_SegmentedBlanketBallReactor(unittest.TestCase):

    def test_gap_between_blankets_impacts_volume(
            self):
        """creates a SegmentedBlanketBallReactor with different
        gap_between_blankets and checks the volume of the blankes and the
        firstwall changes."""

        small_gap_reactor = paramak.SegmentedBlanketBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=150,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=20,
            blanket_radial_thickness=50,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            gap_between_blankets=30,
            number_of_blanket_segments=5,
        )

        large_gap_reactor = paramak.SegmentedBlanketBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=150,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=20,
            blanket_radial_thickness=50,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            gap_between_blankets=60,
            number_of_blanket_segments=5,
        )

        assert small_gap_reactor._blanket.volume > large_gap_reactor._blanket.volume
        assert small_gap_reactor._firstwall.volume > large_gap_reactor._firstwall.volume

    def test_number_of_blanket_segments_impacts_volume(self):
        """creates a SegmentedBlanketBallReactor with different
        number_of_blanket_segments and checks the volume of the blanket and
        firstwall changes"""

        few_segment_reactor = paramak.SegmentedBlanketBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=150,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=20,
            blanket_radial_thickness=50,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            gap_between_blankets=30,
            number_of_blanket_segments=5,
            blanket_fillet_radius=0,
        )

        many_segment_reactor = paramak.SegmentedBlanketBallReactor(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=150,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=20,
            blanket_radial_thickness=50,
            blanket_rear_wall_radial_thickness=30,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
            pf_coil_radial_thicknesses=[50, 50, 50, 50],
            pf_coil_vertical_thicknesses=[50, 50, 50, 50],
            pf_coil_to_rear_blanket_radial_gap=50,
            pf_coil_to_tf_coil_radial_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            gap_between_blankets=30,
            number_of_blanket_segments=8,
            blanket_fillet_radius=0,
        )

        assert many_segment_reactor._blanket.volume < few_segment_reactor._blanket.volume
        assert many_segment_reactor._firstwall.volume > few_segment_reactor._firstwall.volume
