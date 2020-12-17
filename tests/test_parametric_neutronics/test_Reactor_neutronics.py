
import os
import unittest
from pathlib import Path

import paramak


class TestReactorNeutronics(unittest.TestCase):

    def test_export_h5m(self):
        """Creates a Reactor object consisting of two shapes and checks a h5m
        file of the reactor can be exported using the export_h5m method."""

        os.system('rm small_dagmc.h5m')
        os.system('rm small_dagmc_without_graveyard.h5m')
        os.system('rm small_dagmc_with_graveyard.h5m')
        os.system('rm large_dagmc.h5m')
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2')
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        test_reactor.export_h5m(filename='small_dagmc.h5m', tolerance=0.01)
        test_reactor.export_h5m(
            filename='small_dagmc_without_graveyard.h5m',
            tolerance=0.01,
            skip_graveyard=True)
        test_reactor.export_h5m(
            filename='small_dagmc_with_graveyard.h5m',
            tolerance=0.01,
            skip_graveyard=False)
        test_reactor.export_h5m(filename='large_dagmc.h5m', tolerance=0.001)

        assert Path("small_dagmc.h5m").exists() is True
        assert Path("small_dagmc_with_graveyard.h5m").exists() is True
        assert Path("large_dagmc.h5m").exists() is True
        assert Path("large_dagmc.h5m").stat().st_size > Path(
            "small_dagmc.h5m").stat().st_size
        assert Path("small_dagmc_without_graveyard.h5m").stat(
        ).st_size < Path("small_dagmc.h5m").stat().st_size

    def test_export_h5m_without_extension(self):
        """Tests that the code appends .h5m to the end of the filename"""

        os.system('rm out.h5m')
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2')
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        test_reactor.export_h5m(filename='out', tolerance=0.01)
        assert Path("out.h5m").exists() is True
        os.system('rm out.h5m')

    def test_offset_from_graveyard_sets_attribute(self):
        """Creates a graveyard for a reactor and sets the graveyard_offset.
        Checks that the Reactor.graveyard_offset property is set"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2')
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        test_reactor.make_graveyard(graveyard_offset=101)
        assert test_reactor.graveyard_offset == 101


if __name__ == "__main__":
    unittest.main()
