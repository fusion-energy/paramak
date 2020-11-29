
import unittest

import paramak


class TestBlanketFP(unittest.TestCase):
    def test_creation(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        assert blanket.solid is not None

    def test_creation_with_optimiser(self):
        # Default
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        assert blanket.solid is not None

        # With limits
        blanket.length_limits = (10, 300)
        blanket.nb_segments_limits = (4, 8)
        assert blanket.solid is not None

        # With None length_limits
        blanket.length_limits = None
        blanket.nb_segments_limits = (4, 8)
        assert blanket.solid is not None

        # With None nb_segments_limits
        blanket.start_angle = 80
        blanket.length_limits = (100, 300)
        blanket.nb_segments_limits = None
        assert blanket.solid is not None

    def test_optimiser(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)

        blanket.length_limits = (100, 300)
        blanket.nb_segments_limits = (2, 8)
        assert blanket.solid is not None

        def no_possible_config():
            blanket.length_limits = (10, 20)
            blanket.nb_segments_limits = (2, 4)
            blanket.solid

        self.assertRaises(ValueError, no_possible_config)

    def test_modifying_nb_segments_limits(self):
        """creates a shape and checks that modifying the nb_segments_limits
        also modifies segmets_angles accordingly
        """
        blanket1 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)

        blanket2 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180,
            cut=blanket1)

        blanket1.nb_segments_limits = (4, 8)
        blanket2.nb_segments_limits = (3, 8)

        assert blanket2.volume != 0

    def test_segments_angles_is_modified_num_segments(self):
        blanket1 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)

        blanket2 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180,
            cut=blanket1)

        blanket1.num_segments = 8
        blanket2.num_segments = 5
        assert blanket2.volume != 0

    def test_num_point_is_affected(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        assert blanket.num_points == blanket.num_segments + 1
        blanket.num_segments = 60
        assert blanket.num_points == blanket.num_segments + 1

    def test_segment_angles_affects_solid(self):
        blanket1 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        blanket2 = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180,
            cut=blanket1)
        blanket2.segments_angles = [0, 25, 50, 90, 130, 150, 180]
        assert blanket2.volume != 0

    def test_warning_segment_angles(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=1,
            stop_angle=50, rotation_angle=180)

        def warning1():
            blanket.start_angle = 1
            blanket.stop_angle = 50
            blanket.num_segments = None
            blanket.segments_angles = [0, 25, 50, 90, 130, 150, 180]

        def warning2():
            blanket.start_angle = None
            blanket.stop_angle = None
            blanket.num_segments = 7
            blanket.segments_angles = [0, 25, 50, 90, 130, 150, 180]

        self.assertWarns(UserWarning, warning1)
        self.assertWarns(UserWarning, warning2)

    def test_creation_with_gaps(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180,
            segments_gap=3
        )
        assert blanket.solid is not None
