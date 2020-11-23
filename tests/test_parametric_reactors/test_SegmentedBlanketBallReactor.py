
import unittest

import paramak


class test_SegmentedBlanketBallReactor(unittest.TestCase):
    def setUp(self):
        self.test_reactor = paramak.SegmentedBlanketBallReactor(
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
            number_of_blanket_segments=4,
        )

    def test_gap_between_blankets_impacts_volume(
            self):
        """creates a SegmentedBlanketBallReactor with different
        gap_between_blankets and checks the volume of the blankes and the
        firstwall changes."""

        self.test_reactor.gap_between_blankets = 30
        self.test_reactor.create_solids()
        small_gap_blanket = self.test_reactor._blanket.volume
        small_gap_fw = self.test_reactor._firstwall.volume

        self.test_reactor.gap_between_blankets = 60
        self.test_reactor.create_solids()
        large_gap_blanket = self.test_reactor._blanket.volume
        large_gap_fw = self.test_reactor._firstwall.volume

        assert small_gap_blanket > large_gap_blanket
        assert small_gap_fw > large_gap_fw

    def test_number_of_blanket_segments_impacts_volume(self):
        """creates a SegmentedBlanketBallReactor with different
        number_of_blanket_segments and checks the volume of the blanket and
        firstwall changes"""

        self.test_reactor.number_of_blanket_segments = 4
        self.test_reactor.create_solids()
        blanket_few_segments = self.test_reactor._blanket.volume
        fw_few_segments = self.test_reactor._firstwall.volume

        self.test_reactor.number_of_blanket_segments = 6
        self.test_reactor.create_solids()
        blanket_many_segments = self.test_reactor._blanket.volume
        fw_many_segments = self.test_reactor._firstwall.volume

        assert blanket_many_segments < blanket_few_segments
        assert fw_many_segments > fw_few_segments

    def test_inccorect_args(self):
        reactor = paramak.SegmentedBlanketBallReactor(
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
            blanket_fillet_radius=0,
            number_of_blanket_segments=4,
        )

        def inccorect_number_of_blanket_segments():
            self.test_reactor.number_of_blanket_segments = 1

        self.assertRaises(ValueError, inccorect_number_of_blanket_segments)

        def inccorect_gap_between_blankets():
            self.test_reactor.gap_between_blankets = -1

        self.assertRaises(ValueError, inccorect_gap_between_blankets)
