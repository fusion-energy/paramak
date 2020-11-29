
import unittest

import paramak


class TestDivertorITERNoDome(unittest.TestCase):

    def test_creation(self):
        """Creates an ITER-type divertor using the ITERtypeDivertorNoDome
        parametric component and checks that a cadquery solid is created."""

        test_shape = paramak.ITERtypeDivertorNoDome()
        assert test_shape.solid is not None

    def test_stp_export(self):
        """Creates an ITER-type divertor using the ITERtypeDivertorNoDome
        parametric component and checks that a stp file of the shape can be
        exported using the export_stp method."""

        test_shape = paramak.ITERtypeDivertorNoDome()
        test_shape.export_stp("tests/ITER_div_no_dome")

    def test_faces(self):
        """Creates an ITER-type divertor using the ITERtypeDivertorNoDome
        parametric component and checks that a solid with the correct number
        of faces is created"""

        test_shape = paramak.ITERtypeDivertorNoDome()
        assert len(test_shape.areas) == 10
        assert len(set(test_shape.areas)) == 10

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 12
        assert len(set(test_shape.areas)) == 11
