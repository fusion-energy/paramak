import os
import paramak
import unittest


class test_BlanketFP(unittest.TestCase):
    def test_creation(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        assert blanket.solid is not None

    def test_num_point_is_affected(self):
        blanket = paramak.BlanketFPPoloidalSegments(
            thickness=20, start_angle=0,
            stop_angle=180, rotation_angle=180)
        assert blanket.num_points == blanket.num_segments + 1
        blanket.num_segments = 60
        assert blanket.num_points == blanket.num_segments + 1
