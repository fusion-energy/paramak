
import os
import unittest
from pathlib import Path

import paramak


class TestShapeExportH5mPymoab(unittest.TestCase):

    def setUp(self):

        self.my_shape = paramak.CenterColumnShieldHyperbola(
            height=500,
            inner_radius=50,
            mid_radius=60,
            outer_radius=100,
            material_tag='center_column_shield_mat',
            method='pymoab'
        )

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
        test_reactor.export_h5m(
            filename='small_dagmc.h5m',
            faceting_tolerance=0.01
        )
        test_reactor.export_h5m(
            filename='small_dagmc_without_graveyard.h5m',
            faceting_tolerance=0.01,
            include_graveyard=False
        )
        test_reactor.export_h5m(
            filename='small_dagmc_with_graveyard.h5m',
            faceting_tolerance=0.01,
            include_graveyard=True
        )
        test_reactor.export_h5m(
            filename='large_dagmc.h5m',
            faceting_tolerance=0.001
        )

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
        test_reactor.export_h5m(filename='out', faceting_tolerance=0.01)
        assert Path("out.h5m").exists() is True
        os.system('rm out.h5m')

    def test_export_h5m_makes_dagmc_file(self):
        """Makes a NeutronicsModel from a shapes, then makes the h5m file"""

        # tests method using class attribute
        os.system('rm dagmc.h5m')
        self.my_shape.export_h5m()
        assert Path('dagmc.h5m').exists() is True

        # tests method using method argument
        os.system('rm dagmc.h5m')
        self.my_shape.export_h5m(method='pymoab')
        assert Path('dagmc.h5m').exists() is True

    def test_export_vtk(self):
        """Creates vtk files from the h5m files and checks they exist"""

        os.system('rm *.h5m *.vtk')

        assert self.my_shape.h5m_filename is None
        self.my_shape.export_h5m_with_pymoab()
        self.my_shape.export_vtk()
        assert Path('dagmc.h5m').is_file
        assert Path('dagmc.vtk').is_file
        assert Path('dagmc_no_graveyard.vtk').is_file
        assert self.my_shape.h5m_filename == 'dagmc.h5m'

        self.my_shape.export_vtk(filename='custom_filename.vtk')
        assert Path('custom_filename.vtk').is_file

        self.my_shape.export_vtk(filename='suffixless_filename')
        assert Path('suffixless_filename.vtk').is_file


class TestReactorExportH5mPymoab(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1'
        )

        self.test_shape2 = paramak.ExtrudeStraightShape(
            points=[(100, 100), (50, 100), (50, 50)],
            distance=20,
            material_tag='mat2'
        )

        self.test_reactor = paramak.Reactor([self.test_shape])

    def test_export_h5m_with_pymoab_without_faceting_tolerance(self):
        """exports a h5m file with faceting_tolerance set to None which uses
        the the self.faceting_tolerance is used"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2'
        )
        my_reactor = paramak.Reactor([test_shape])
        my_reactor.faceting_tolerance = 1e-2
        my_reactor.export_h5m_with_pymoab(faceting_tolerance=None)

    def test_export_h5m_with_pymoab_without_plasma(self):
        """exports a h5m file with pymoab without the plasma"""

        os.system('rm *.stl')

        test_shape1 = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            stl_filename='RotateStraightShape.stl',
            material_tag='mat1',
        )
        test_shape2 = paramak.Plasma(
            stl_filename='plasma.stl',
            material_tag='mat1',
        )

        my_reactor = paramak.Reactor([test_shape1, test_shape2])
        my_reactor.export_h5m_with_pymoab(
            include_plasma=False, filename='no_plasma.h5m')

        assert Path('RotateStraightShape.stl').is_file()
        assert Path('plasma.stl').is_file() is False
        my_reactor.export_h5m_with_pymoab(
            include_plasma=True, filename='with_plasma.h5m')
        assert Path('plasma.stl').is_file()
        assert Path('with_plasma.h5m').stat().st_size > Path(
            'no_plasma.h5m').stat().st_size

    def test_export_h5m_with_pymoab_from_manifest_file(self):
        """exports a h5m file when shapes_and_components is set to a string"""

        os.system('rm dagmc.h5m')
        os.system('rm *.stp')
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            stp_filename='test_shape.stp'
        )
        test_shape.export_stp()
        test_shape.export_neutronics_description('manifest.json')
        my_reactor = paramak.Reactor('manifest.json')
        my_reactor.export_h5m_with_pymoab()
        assert Path('dagmc.h5m').is_file()

    def test_export_vtk(self):
        """Creates vtk files from the h5m files and checks they exist"""

        os.system('rm *.h5m *.vtk')

        assert self.test_reactor.h5m_filename is None
        self.test_reactor.export_h5m_with_pymoab()
        self.test_reactor.export_vtk()
        assert Path('dagmc.h5m').is_file()
        assert Path('dagmc.vtk').is_file()
        self.test_reactor.export_vtk(
            include_graveyard=False,
            filename='dagmc_no_graveyard.vtk')
        assert Path('dagmc_no_graveyard.vtk').is_file()
        assert self.test_reactor.h5m_filename == 'dagmc.h5m'

        self.test_reactor.export_vtk(filename='custom_filename.vtk')
        assert Path('custom_filename.vtk').is_file()

        self.test_reactor.export_vtk(filename='suffixless_filename')
        assert Path('suffixless_filename.vtk').is_file()


if __name__ == "__main__":
    unittest.main()
