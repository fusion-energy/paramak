
import unittest

import paramak


class TestVacuumVessel(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.VacuumVessel(
            height=2, inner_radius=1, thickness=0.2
        )

    def test_creation(self):
        """Creates a shape using the VacuumVessel parametric component and
        checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None

    def test_ports(self):
        """Creates a vacuum vessel with ports holes in it and checks that a
        caquery solid is created."""

        cutter1 = paramak.PortCutterRectangular(
            distance=3, center_point=(
                0, 0), height=0.2, width=0.4, fillet_radius=0.01)
        cutter2 = paramak.PortCutterRectangular(
            distance=3, center_point=(
                0.5, 0), height=0.2, width=0.4, fillet_radius=0.00)
        cutter3 = paramak.PortCutterRectangular(
            distance=3, center_point=(-0.5, 0), height=0.2, width=0.4,
            physical_groups=None)
        cutter4 = paramak.PortCutterCircular(
            distance=3,
            center_point=(
                0.25,
                0),
            radius=0.1,
            azimuth_placement_angle=45,
            physical_groups=None)
        cutter5 = paramak.PortCutterRotated(
            (0, 0), azimuth_placement_angle=-90, rotation_angle=10,
            fillet_radius=0.01, physical_groups=None)

        pre_cut_volume = self.test_shape.volume

        self.test_shape.cut = [cutter1, cutter2, cutter3, cutter4, cutter5]
        assert self.test_shape.solid is not None
        assert self.test_shape.volume < pre_cut_volume
