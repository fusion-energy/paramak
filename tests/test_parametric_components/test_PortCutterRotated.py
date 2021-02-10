
import unittest

import numpy as np
import paramak


class TestPortCutterRotated(unittest.TestCase):
    def test_shape_construction_and_volume(self):
        """Cuts a vessel cylinder with several different size port cutters."""

        small_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        large_ports = paramak.PortCutterRotated(
            polar_coverage_angle=6,
            center_point=(100, 0),
            polar_placement_angle=10,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            max_distance_from_center=1000,
            rotation_angle=10
        )

        vessel_with_out_ports = paramak.CenterColumnShieldCylinder(
            height=500,
            inner_radius=200,
            outer_radius=300
        )

        vessel_with_small_ports = paramak.CenterColumnShieldCylinder(
            height=500,
            inner_radius=200,
            outer_radius=300,
            cut=small_ports
        )

        vessel_with_large_ports = paramak.CenterColumnShieldCylinder(
            height=500,
            inner_radius=200,
            outer_radius=300,
            cut=large_ports
        )

        assert large_ports.volume > small_ports.volume
        assert vessel_with_out_ports.volume > vessel_with_small_ports.volume
        assert vessel_with_small_ports.volume > vessel_with_large_ports.volume

    def test_polar_coverage_angle_impacts_volume(self):
        """Checks the volumes of two port cutters with different
        polar_coverage_angle and checks angle impacts the volume."""

        small_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        large_ports = paramak.PortCutterRotated(
            polar_coverage_angle=6,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        assert large_ports.volume > small_ports.volume

    def test_max_distance_from_center_impacts_volume(self):
        """Checks the volumes of two port cutters with different
        max_distance_from_center and checks distance impacts the volume."""

        small_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        large_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=2000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        assert large_ports.volume > small_ports.volume

    def test_azimuth_placement_angle_impacts_volume(self):
        """Checks the volumes of two port cutters with different
        azimuth_placement_angle and checks distance impacts the volume."""

        small_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        large_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 5),
            rotation_angle=10
        )

        assert large_ports.volume > small_ports.volume

    def test_rotation_angle_impacts_volume(self):
        """Checks the volumes of two port cutters with different
        rotation_angle and checks distance impacts the volume."""

        small_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=10
        )

        large_ports = paramak.PortCutterRotated(
            polar_coverage_angle=5,
            center_point=(100, 0),
            polar_placement_angle=10,
            max_distance_from_center=1000,
            azimuth_placement_angle=np.linspace(0, 360, 4),
            rotation_angle=20
        )

        assert large_ports.volume > small_ports.volume

    def test_outerpoint_negative(self):
        """Tests that when polar_coverage_angle is greater than 180 an error is
        raised."""
        def error():
            paramak.PortCutterRotated(
                center_point=(1, 1),
                polar_coverage_angle=181,
                polar_placement_angle=0,
                rotation_angle=10,
            )
        self.assertRaises(ValueError, error)
