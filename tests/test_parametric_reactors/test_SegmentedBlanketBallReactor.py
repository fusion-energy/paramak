
import unittest

import paramak


class TestSegmentedBlanketBallReactor(unittest.TestCase):

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
            pf_coil_radial_position=[200, 200, 200, 200],
            pf_coil_vertical_position=[200, 100, -100, -200],
            rear_blanket_to_tf_gap=50,
            outboard_tf_coil_radial_thickness=100,
            outboard_tf_coil_poloidal_thickness=50,
            gap_between_blankets=30,
            number_of_blanket_segments=4,
        )

    def test_gap_between_blankets_impacts_volume(self):
        """Creates a SegmentedBlanketBallReactor with different
        gap_between_blankets and checks the volume of the blankes and the
        firstwall changes."""

        self.test_reactor.create_solids()
        small_gap_blanket_volume = self.test_reactor._blanket.volume
        small_gap_firstwall_volume = self.test_reactor._firstwall.volume

        self.test_reactor.gap_between_blankets = 60
        self.test_reactor.create_solids()
        large_gap_blanket_volume = self.test_reactor._blanket.volume
        large_gap_firstwall_volume = self.test_reactor._firstwall.volume

        assert small_gap_blanket_volume > large_gap_blanket_volume
        assert small_gap_firstwall_volume > large_gap_firstwall_volume

    def test_number_of_blanket_segments_impacts_volume(self):
        """Creates a SegmentedBlanketBallReactor with different
        number_of_blanket_segments and checks the volume of the blanket and
        firstwall changes."""

        self.test_reactor.create_solids()
        blanket_volume_few_segments = self.test_reactor._blanket.volume
        firstwall_volume_few_segments = self.test_reactor._firstwall.volume

        self.test_reactor.number_of_blanket_segments = 6
        self.test_reactor.create_solids()
        blanket_volume_many_segments = self.test_reactor._blanket.volume
        firstwall_volume_many_segments = self.test_reactor._firstwall.volume

        assert blanket_volume_many_segments < blanket_volume_few_segments
        assert firstwall_volume_many_segments > firstwall_volume_few_segments

    def test_invalid_parameter_error_raises(self):
        """Checks that the correct errors are raised when invalid arguments for
        parameters are input."""

        def invalid_gap_between_blankets():
            self.test_reactor.gap_between_blankets = -1

        def invalid_number_of_blanket_segments():
            self.test_reactor.number_of_blanket_segments = 1

        self.assertRaises(ValueError, invalid_gap_between_blankets)
        self.assertRaises(ValueError, invalid_number_of_blanket_segments)
