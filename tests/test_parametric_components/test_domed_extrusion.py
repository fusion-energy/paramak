import unittest

import pytest

import paramak


class TestExtrudeHollowRectangle(unittest.TestCase):
    def setUp(self):
        self.test_shape = paramak.ExtrudeHollowRectangle(height=10, width=15, casing_thickness=1, distance=2)

    def test_volumes_for_various_combo_match(self):
        """Checks that """

        pool_lower_pos = paramak.DomedExtrusion(
            extrusion_distance = 100,
            dome_height = 50,
            extrusion_start_offset = -20,
            radius=200,
            name='lower_20',
            upper_or_lower='lower',
            rotation_angle=180
        )

        pool_upper_pos = paramak.DomedExtrusion(
            extrusion_distance = 100,
            dome_height = 50,
            extrusion_start_offset = -20,
            radius=200,
            name='upper_20',
            upper_or_lower='upper',
            rotation_angle=180
        )

        pool_upper_neg = paramak.DomedExtrusion(
            extrusion_distance = -100,
            dome_height = 50,
            extrusion_start_offset = -20,
            radius=200,
            name='upper_-20',
            upper_or_lower='upper',
            rotation_angle=180
        )

        pool_lower_neg = paramak.DomedExtrusion(
            extrusion_distance = -100,
            dome_height = 50,
            extrusion_start_offset = -20,
            radius=200,
            name='lower_-20',
            upper_or_lower='lower',
            rotation_angle=180
        )
        
        vol_to_check = pool_lower_pos.volume()
        assert pytest.approx(pool_upper_pos.volume()) == vol_to_check
        assert pytest.approx(pool_upper_neg.volume()) == vol_to_check
        assert pytest.approx(pool_lower_neg.volume()) == vol_to_check

    def test_extrusion_distance_increases_volume(self):
        """Checks that a shape that is twice as long is bigger but not quite
        twice a bt as they both have the same domed end"""

        small_shape = paramak.DomedExtrusion(extrusion_distance = 10)
        big_shape = paramak.DomedExtrusion(extrusion_distance = 20)
        
        assert small_shape.volume() < big_shape.volume()
        assert small_shape.volume() *2 > big_shape.volume()

    def test_radius_increases_volume(self):
        """Checks that a shape that is twice the radius is bigger"""

        small_shape = paramak.DomedExtrusion(radius = 10)
        big_shape = paramak.DomedExtrusion(radius = 20)
        
        assert small_shape.volume() < big_shape.volume()

    def test_radius_increases_volume(self):
        """Checks that a shape that is twice rotation_angle is bigger"""

        small_shape = paramak.DomedExtrusion(rotation_angle = 180)
        big_shape = paramak.DomedExtrusion(rotation_angle = 360)
        
        assert small_shape.volume() < big_shape.volume()
