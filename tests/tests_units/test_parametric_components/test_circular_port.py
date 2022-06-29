import unittest

import paramak


class TestCircularPort(unittest.TestCase):
    def setUp(self):

        self.test_shape = paramak.CircularPort(
            inner_radius=20,
            azimuth_placement_angle=[0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            color=(0, 1, 0),
            rotation_angle=180,
            blank_flange_thickness=4,
            flange_thickness=10,
            wall_thickness=2,
            distance=50,
            flange_gap=0,
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a CircularPort are correct."""

        assert self.test_shape.inner_radius == 20
        assert self.test_shape.rotation_angle == 180
        assert self.test_shape.blank_flange_thickness == 4
        assert self.test_shape.flange_thickness == 10
        assert self.test_shape.wall_thickness == 2
        assert self.test_shape.distance == 50
        assert self.test_shape.flange_gap == 0

    def test_creation(self):
        """Creates a circular port cutter using the CircularPort parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume() > 1000

    def test_gap_makes_extra_surfaces(self):
        """Creates a circular port cutter using the CircularPort parametric
        component and checks that a cadquery solid with the right number of
        surfaces is created."""

        self.test_shape.azimuth_placement_angle = [0]
        self.test_shape.rotation_angle = 360
        assert len(self.test_shape.solid.val().Faces()) == 7
        self.test_shape.flange_gap = 1
        assert len(self.test_shape.solid.val().Faces()) == 9

    def test_gap_and_cut_makes_extra_surfaces(self):
        """Creates a circular port cutter using the CircularPort parametric
        component and checks that a cadquery solid with the right number of
        surfaces is created."""

        self.test_shape.azimuth_placement_angle = [0]
        self.test_shape.rotation_angle = 180  # this cuts the shape in half
        assert len(self.test_shape.solid.val().Faces()) == 8
        self.test_shape.flange_gap = 1
        assert len(self.test_shape.solid.val().Faces()) == 12
