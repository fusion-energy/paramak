
import unittest
import pytest
import paramak


class TestVacuumVessel(unittest.TestCase):

    def setUp(self):
        self.cutter = paramak.PortCutterRectangular(
            width=100,
            height=100,
            distance=1100,
            azimuth_placement_angle=[
                0,
                90,
                180,
                270])
        self.test_shape = paramak.VacuumVesselInnerLeg(
            inner_height=1100,
            inner_radius=700,
            inner_leg_radius=100,
            thickness=100,
        )
        self.test_shape_cut = paramak.VacuumVesselInnerLeg(
            inner_height=1100,
            inner_radius=700,
            inner_leg_radius=100,
            thickness=100,
            cut=self.cutter
        )

    def test_creation(self):
        """Creates a shape using the VacuumVessel parametric component and
        checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None

    def test_cut(self):
        assert self.test_shape.volume != self.test_shape_cut.volume
