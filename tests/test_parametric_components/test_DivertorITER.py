
import paramak
import unittest


class test_DivertorITER(unittest.TestCase):
    def test_DivertorITER_creation(self):
        """creates an ITER-type divertor using the ITERtypeDivertor parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.ITERtypeDivertor()
        assert test_shape.solid is not None

    def test_DivertorITER_STP_export(self):
        """creates an ITER-type divertor using the ITERtypeDivertor parametric component and
        checks that an stp file of the shape can be exported using the export_stp method"""

        test_shape = paramak.ITERtypeDivertor()
        test_shape.export_stp("tests/ITER_div")
