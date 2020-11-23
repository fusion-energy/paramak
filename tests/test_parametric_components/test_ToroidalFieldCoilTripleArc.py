
import unittest

import paramak
import pytest


class test_ToroidalFieldCoilTripleArc(unittest.TestCase):
    def test_ToroidalFieldCoilTripleArc_creation_with_inner_leg(self):
        """creates a tf coil with inner leg using the ToroidalFieldCoilTripleArc
        parametric component and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilTripleArc(
            R1=100,
            h=100,
            radii=(100, 200),
            coverages=(10, 60),
            thickness=10,
            distance=50,
            number_of_coils=1,
            vertical_displacement=10,
            with_inner_leg=True
        )
        assert test_shape.solid is not None
        assert test_shape.volume > 1000
        assert test_shape.inner_leg_connection_points is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=test_shape.inner_leg_connection_points, distance=0.5
        )
        assert test_inner_leg.solid is not None

    def test_ToroidalFieldCoilTripleArc_creation_no_inner_leg(self):
        """creates a tf coil with no inner leg using the ToroidalFieldCoilRectangle
        parametric component and checks that a cadquery solid is created"""

        test_shape_1 = paramak.ToroidalFieldCoilTripleArc(
            R1=100, h=100, radii=(100, 200), coverages=(10, 60), thickness=10,
            distance=50, number_of_coils=1, vertical_displacement=10,
            with_inner_leg=True
        )
        test_volume_1 = test_shape_1.volume

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=test_shape_1.inner_leg_connection_points, distance=50
        )
        inner_leg_volume = test_inner_leg.volume

        test_shape_2 = paramak.ToroidalFieldCoilTripleArc(
            R1=100, h=100, radii=(100, 200), coverages=(10, 60), thickness=10,
            distance=50, number_of_coils=1, vertical_displacement=10,
            with_inner_leg=False
        )
        assert test_shape_2.solid is not None
        assert test_shape_2.volume == pytest.approx(
            test_volume_1 - inner_leg_volume, rel=0.01)

    def test_ToroidalFieldCoilTripleArc_relative_volume(self):
        """creates tf coil shapes with different numbers of tf coils and checks that
        their relative volumes are correct"""

        test_shape_1 = paramak.ToroidalFieldCoilTripleArc(
            R1=100, h=100, radii=(100, 200), coverages=(10, 60), thickness=10,
            distance=50, number_of_coils=1, vertical_displacement=10,
            with_inner_leg=True
        )
        test_volume_1 = test_shape_1.volume

        test_shape_2 = paramak.ToroidalFieldCoilTripleArc(
            R1=100, h=100, radii=(100, 200), coverages=(10, 60), thickness=10,
            distance=50, number_of_coils=8, vertical_displacement=10,
            with_inner_leg=True
        )
        assert test_shape_2.volume == pytest.approx(
            test_volume_1 * 8, rel=0.01)

    def test_ToroidalFieldCoilTripleArc_rotation_angle(self):
        """Creates tf coils with rotation_angles < 360 in different workplanes
        and checks that the correct cuts are performed and their volumes are
        correct."""

        test_shape = paramak.ToroidalFieldCoilTripleArc(
            R1=150,
            h=200,
            radii=(50, 50),
            coverages=(70, 70),
            thickness=50,
            distance=50,
            number_of_coils=8,
        )

        test_shape.rotation_angle = 360
        test_shape.workplane = "XZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5, rel=0.01)

        test_shape.rotation_angle = 360
        test_shape.workplane = "YZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5, rel=0.01)

        # this test will remain commented until workplane issue #308 is resolved
        # currently causes terminal to crash due to large number of unions
        # test_shape.rotation_angle = 360
        # test_shape.workplane = "XY"
        # test_volume = test_shape.volume
        # test_shape.rotation_angle = 180
        # assert test_shape.volume == pytest.approx(test_volume * 0.5)
