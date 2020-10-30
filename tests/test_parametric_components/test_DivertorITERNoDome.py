
import paramak
import unittest


class test_DivertorITERNoDome(unittest.TestCase):
    def test_DivertorITER_creation(self):
        """Creates an ITER-type divertor using the ITERtypeDivertorNoDome
        parametric component and checks that a cadquery solid is created."""

        test_shape = paramak.ITERtypeDivertorNoDome()
        assert test_shape.solid is not None

    def test_DivertorITER_STP_export(self):
        """Creates an ITER-type divertor using the ITERtypeDivertorNoDome
        parametric component and checks that a stp file of the shape can be
        exported using the export_stp method."""

        test_shape = paramak.ITERtypeDivertorNoDome()
        test_shape.export_stp("tests/ITER_div_no_dome")
