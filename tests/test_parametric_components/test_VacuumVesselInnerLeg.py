
import unittest

import paramak


class TestVacuumVessel(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.VacuumVesselInnerLeg(
            inner_height=1100,
            inner_radius=700,
            inner_leg_radius=100,
            thickness=0.2
        )

    def test_creation(self):
        """Creates a shape using the VacuumVessel parametric component and
        checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
