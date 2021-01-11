
import math
import random
import unittest

import paramak
import pytest


class TestCuttingWedge(unittest.TestCase):
    """Creates a random sized cutting wedge and changes the volume"""

    def test_volume_of_for_5_random_dimentions(self):
        for test_number in range(5):
            height = random.uniform(1., 2000.)
            radius = random.uniform(1., 1000)
            rotation_angle = random.uniform(1., 360.)
            azimuth_placement_angle = random.uniform(1., 360.)

            test_shape = paramak.CuttingWedge(
                height=height,
                radius=radius,
                rotation_angle=rotation_angle,
                azimuth_placement_angle=azimuth_placement_angle
            )
            angle_fraction = 360 / rotation_angle
            correct_volume = (math.pi * radius ** 2 * height) / angle_fraction
            assert test_shape.volume == pytest.approx(correct_volume)

    def test_surface_reflectivity_in_neutronics_description(self):
        test_shape = paramak.CuttingWedge(
            height=1000,
            radius=1000,
            rotation_angle=270,
            surface_reflectivity=True
        )

        json_dict = test_shape.neutronics_description()
        assert 'surface_reflectivity' in json_dict.keys()
        assert json_dict['surface_reflectivity'] is True
