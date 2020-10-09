
import paramak
import unittest


class test_ToroidalFieldCoilTripleArc(unittest.TestCase):
    def test_ToroidalFieldCoilTripleArc_creation(self):
        """creates a ToroidalFieldCoilTripleArc object and checks a solid is created"""

        test_shape = paramak.ToroidalFieldCoilTripleArc(
            R1=1,
            h=1,
            radii=(1, 2),
            coverages=(10, 60),
            thickness=0.1,
            distance=0.5,
            number_of_coils=6,
            vertical_displacement=0.1)
        assert test_shape.solid is not None
