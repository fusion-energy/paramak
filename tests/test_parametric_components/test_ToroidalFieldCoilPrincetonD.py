
import unittest

import paramak
import pytest


class TestToroidalFieldCoilPrincetonD(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.ToroidalFieldCoilPrincetonD(
            R1=100, R2=300, thickness=50, distance=30, number_of_coils=1,
            with_inner_leg=True
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a ToroidalFieldCoilPrincetonD are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.vertical_displacement == 0
        assert self.test_shape.with_inner_leg
        assert self.test_shape.stp_filename == "ToroidalFieldCoilPrincetonD.stp"
        assert self.test_shape.stl_filename == "ToroidalFieldCoilPrincetonD.stl"
        assert self.test_shape.material_tag == "outer_tf_coil_mat"

    def test_creation_with_inner_leg(self):
        """Creates a tf coil with inner leg using the ToroidalFieldCoilPrincetonD
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000
        assert self.test_shape.inner_leg_connection_points is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=self.test_shape.inner_leg_connection_points, distance=30
        )
        assert test_inner_leg.solid is not None

    def test_creation_no_inner_leg(self):
        """Creates a tf coil with no inner leg using the ToroidalFieldCoilPrincetonD
        parametric component and checks that a cadquery solid is created."""

        test_volume = self.test_shape.volume

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=self.test_shape.inner_leg_connection_points, distance=30
        )
        inner_leg_volume = test_inner_leg.volume

        self.test_shape.with_inner_leg = False

        assert self.test_shape.solid is not None
        assert self.test_shape.volume < test_volume

    def test_relative_volume(self):
        """Creates tf coil shapes with different numbers of tf coils and checks that
        their relative volumes are correct."""

        self.test_shape.number_of_coils = 4
        test_volume = self.test_shape.volume

        self.test_shape.number_of_coils = 8
        assert test_volume == pytest.approx(
            self.test_shape.volume * 0.5, rel=0.01)

    def test_rotation_angle(self):
        """Creates a tf coil with a rotation_angle < 360 degrees and checks
        that the correct cut is performed and the volume is correct."""

        self.test_shape.number_of_coils = 8

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "YZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XY"
        self.test_shape.rotation_axis = "Y"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)
