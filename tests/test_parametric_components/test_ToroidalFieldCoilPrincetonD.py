
import paramak
import unittest


class test_ToroidalFieldCoilPrincetonD(unittest.TestCase):
    def test_ToroidalFieldCoilPrincetonD_creation(self):
        """creates a ToroidalFieldCoilPrincetonD object and checks a solid is created"""

        test_shape = paramak.ToroidalFieldCoilPrincetonD(
            R1=100,
            R2=300,
            thickness=50,
            distance=50,
            number_of_coils=2,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_ToroidalFieldCoilPrincetonD_with_leg(self):
        """creates a ToroidalFieldCoilPrincetonD object and checks a leg can
        be created"""

        my_magnet = paramak.ToroidalFieldCoilPrincetonD(
            R1=0.29, R2=0.91, thickness=0.05, distance=0.05, number_of_coils=1)
        my_magnet.export_stp('princeton.stp')

        my_leg = paramak.ExtrudeStraightShape(
            points=my_magnet.inner_leg_connection_points, distance=0.05)

        assert my_leg.solid is not None
