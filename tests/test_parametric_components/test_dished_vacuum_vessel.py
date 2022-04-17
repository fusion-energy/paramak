import pytest

import paramak


def test_volume_increases_with_rotation_angle():
    test_shape_1 = paramak.DishedVacuumVessel(rotation_angle=180)
    test_shape_2 = paramak.DishedVacuumVessel(rotation_angle=360)
    assert test_shape_1.volume() * 2 == pytest.approx(test_shape_2.volume())
