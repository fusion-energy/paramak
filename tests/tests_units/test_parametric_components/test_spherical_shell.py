import unittest

import paramak


class TestSphericalShell(unittest.TestCase):
    def setUp(self):
        self.test_shape = paramak.SphericalShell(inner_radius=1, shell_thickness=0.2)

    def test_creation(self):
        """Creates a shape using the VacuumVessel parametric component and
        checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
    