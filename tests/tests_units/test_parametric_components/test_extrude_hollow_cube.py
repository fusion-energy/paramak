import unittest

import paramak


class TestHollowCube(unittest.TestCase):
    """tests the hoolw cube shape that is used as a graveyard"""

    def setUp(self):
        self.test_shape = paramak.HollowCube(length=10, thickness=2)

    def test_default_parameters(self):
        """Checks that the default parameters of a HollowCube are
        correct."""

        assert self.test_shape.center_coordinate == (0.0, 0.0, 0.0)

    def test_center_point_changes_bounding_box(self):
        """Checks that moving the center results in the bounding box move as well"""

        default_shape_bb = ((-(10 + 2) / 2, -(10 + 2) / 2, -(10 + 2) / 2), ((10 + 2) / 2, (10 + 2) / 2, (10 + 2) / 2))
        assert self.test_shape.bounding_box == default_shape_bb

        self.test_shape.center_coordinate = (1, 1, 1)

        assert self.test_shape.bounding_box == (
            (default_shape_bb[0][0] + 1, default_shape_bb[0][1] + 1, default_shape_bb[0][2] + 1),
            (default_shape_bb[1][0] + 1, default_shape_bb[1][1] + 1, default_shape_bb[1][2] + 1),
        )

        self.test_shape.center_coordinate = (-2, 3, 14)

        assert self.test_shape.bounding_box == (
            (default_shape_bb[0][0] - 2, default_shape_bb[0][1] + 3, default_shape_bb[0][2] + 14),
            (default_shape_bb[1][0] - 2, default_shape_bb[1][1] + 3, default_shape_bb[1][2] + 14),
        )
