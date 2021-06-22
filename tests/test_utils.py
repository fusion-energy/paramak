
import os
import unittest
from pathlib import Path

import numpy as np
import paramak
import plotly.graph_objects as go
import pytest
import urllib.request
from cadquery.cq import Workplane
from paramak.utils import (EdgeLengthSelector, FaceAreaSelector,
                           add_stl_to_moab_core, define_moab_core_and_tags,
                           extract_points_from_edges, facet_wire,
                           find_center_point_of_circle, plotly_trace)


class TestUtilityFunctions(unittest.TestCase):

    def test_make_watertight_cmd_with_example_dagmc_file(self):
        """downloads a h5m and makes it watertight, checks the the watertight
        file is produced."""

        os.system('rm *.h5m')

        url = 'https://github.com/Shimwell/fusion_example_for_openmc_using_paramak/raw/main/dagmc.h5m'
        urllib.request.urlretrieve(url, 'not_watertight_dagmc.h5m')

        output_filename = paramak.utils.make_watertight(
            input_filename="not_watertight_dagmc.h5m",
            output_filename="watertight_dagmc.h5m"
        )

        assert Path("not_watertight_dagmc.h5m").exists() is True
        assert output_filename == "watertight_dagmc.h5m"
        assert Path("watertight_dagmc.h5m").exists() is True

    def test_export_vtk_without_h5m_raises_error(self):
        """exports a vtk file when shapes_and_components is set to a string"""

        def check_correct_error_is_rasied():
            os.system('rm *.h5m *.vtk')
            paramak.utils.export_vtk(h5m_filename='dagmc.h5m')

        self.assertRaises(FileNotFoundError, check_correct_error_is_rasied)

    def test_export_vtk_without_h5m_suffix(self):
        """exports a vtk file when shapes_and_components is set to a string"""

        os.system('rm *.stl *.h5m *.vtk')

        pf_coil = paramak.PoloidalFieldCoil(
            height=10,
            width=10,
            center_point=(100, 0),
            rotation_angle=180,
            material_tag='copper'
        )

        pf_coil.export_h5m_with_pymoab(
            filename='dagmc',
            include_graveyard=True,
        )

        paramak.utils.export_vtk(h5m_filename='dagmc')

        assert Path('dagmc.vtk').is_file()
        assert Path('dagmc.h5m').is_file()

    def test_missing_dagmc_not_watertight_file(self):

        def missing_dagmc_not_watertight_file():
            """Trys to make a watertight dagmc.h5m file without a
            dagmc_not_watertight.h5m input file"""

            os.system('rm *.h5m')

            paramak.utils.make_watertight(
                input_filename="dagmc_not_watertight.h5m",
                output_filename="dagmc.h5m",
            )

        self.assertRaises(
            FileNotFoundError,
            missing_dagmc_not_watertight_file
        )

    def test_moab_instance_creation(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        os.system('rm *.stl *.h5m')

        moab_core, moab_tags = define_moab_core_and_tags()

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )

        test_shape.export_stl('test_file.stl')

        new_moab_core = add_stl_to_moab_core(
            moab_core=moab_core,
            surface_id=1,
            volume_id=1,
            material_name='test_mat',
            tags=moab_tags,
            stl_filename='test_file.stl'
        )

        all_sets = new_moab_core.get_entities_by_handle(0)

        file_set = new_moab_core.create_meshset()

        new_moab_core.add_entities(file_set, all_sets)

        new_moab_core.write_file('test_file.h5m')

        assert Path('test_file.stl').exists()
        assert Path('test_file.h5m').exists()

    def test_convert_circle_to_spline(self):
        """Tests the conversion of 3 points on a circle into points on a spline
        curve."""

        new_points = paramak.utils.convert_circle_to_spline(
            p_0=(200., 0.),
            p_1=(250., 50.),
            p_2=(200., 100.),
            tolerance=0.2
        )

        # these points can change from 200. to values like 200.00000000000009
        assert pytest.approx(new_points[0][0], abs=0.0000000000001) == 200
        assert pytest.approx(new_points[0][1], abs=0.0000000000001) == 0
        assert pytest.approx(new_points[-1][0], abs=0.0000000000001) == 200
        assert pytest.approx(new_points[-1][1], abs=0.0000000000001) == 100

        new_points_more_details = paramak.utils.convert_circle_to_spline(
            p_0=(200, 0),
            p_1=(250, 50),
            p_2=(200, 100),
            tolerance=0.1
        )

        assert len(new_points_more_details) > len(new_points)

    def test_extract_points_from_edges(self):
        """Extracts points from edges and checks the list returned is the
        correct len and contains the correct types"""

        test_points = [(1, 1), (3, 1), (4, 2)]
        test_shape = paramak.ExtrudeStraightShape(
            points=test_points,
            distance=6,
            workplane='YZ')

        edges = facet_wire(wire=test_shape.wire)

        points = extract_points_from_edges(edges=edges, view_plane='YZ')

        assert len(points) == 6

        for point in points:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(
            edges=edges[0], view_plane='YZ')

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(
            edges=edges[0], view_plane='XYZ')

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 3
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)
            assert isinstance(point[2], float)

    def test_trace_creation(self):
        """Creates a plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[
                (0, 20),
                (20, 0),
                (0, -20)
            ],
            mode='markers+lines',
            color=(10, 10, 10, 0.5)
        )

        assert isinstance(trace, go.Scatter)

    def test_trace_creation_3d(self):
        """Creates a 3d plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[
                (0, 20, 0),
                (20, 0, 10),
                (0, -20, -10)
            ],
            mode='markers+lines',
            color=(10, 10, 10)
        )

        assert isinstance(trace, go.Scatter3d)

    def test_find_center_point_of_circle(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        point_a = (0, 20)
        point_b = (20, 0)
        point_3 = (0, -20)

        assert find_center_point_of_circle(
            point_a, point_b, point_3) == (
            (0, 0), 20)

    def test_EdgeLengthSelector_with_fillet_areas(self):
        """tests the filleting of a RotateStraightShape results in an extra
        surface area"""

        test_shape = paramak.RotateStraightShape(
            points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 3

        test_shape.solid = test_shape.solid.edges(
            EdgeLengthSelector(6.28)).fillet(0.1)

        assert len(test_shape.areas) == 4

    def test_FaceAreaSelector_with_fillet_areas(self):
        """tests the filleting of a ExtrudeStraightShape"""

        test_shape = paramak.ExtrudeStraightShape(
            distance=5, points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 5

        test_shape.solid = test_shape.solid.faces(
            FaceAreaSelector(0.5)).fillet(0.1)

        assert len(test_shape.areas) == 11

    def test_find_center_point_of_circle_zero_det(self):
        """Checks that None is given if det is zero
        """
        point_a = (0, 0)
        point_b = (0, 0)
        point_3 = (0, 0)

        assert find_center_point_of_circle(
            point_a, point_b, point_3) == (
            None, np.inf)

    # these tests only work if trelis is avaialbe
    # def test_make_watertight_cmd(self):
    #     """exports a h5m and makes it watertight, checks the the watertight
    #     file is produced."""

    #     os.system('rm *.stl *.h5m')

    #     https://github.com/Shimwell/fusion_example_for_openmc_using_paramak/raw/main/dagmc.h5m

    #     pf_coil = paramak.PoloidalFieldCoil(
    #         height=10,
    #         width=10,
    #         center_point=(100, 0),
    #         rotation_angle=180,
    #         material_tag='copper',
    #         method='trelis'
    #     )

    #     pf_coil.export_h5m_with_trelis(
    #         filename='not_watertight_dagmc.h5m',
    #         include_graveyard=True,
    #     )

    #     assert Path('not_watertight_dagmc.h5m').is_file

    #     output_filename = paramak.utils.make_watertight(
    #         input_filename="not_watertight_dagmc.h5m",
    #         output_filename="watertight_dagmc.h5m"
    #     )

    #     assert Path("not_watertight_dagmc.h5").exists() is True
    #     assert output_filename == "watertight_dagmc.h5m"
    #     assert Path("watertight_dagmc.h5").exists() is True

    # def test_trelis_command_to_create_dagmc_h5m_with_default_mat_name(self):
    #     """Creats a h5m file with trelis and forms groups using the material_tag
    #     key in the manifest.json file. Then checks the groups in the resulting
    #     h5 file match those in the original dictionary"""

    #     pf_coil = paramak.PoloidalFieldCoil(
    #         height=10,
    #         width=10,
    #         center_point=(100, 0),
    #         rotation_angle=180,
    #     )

    #     pf_coil_case = paramak.PoloidalFieldCoilCaseFC(
    #         pf_coil=pf_coil,
    #         casing_thickness=5
    #     )

    #     pf_coil.export_stp('pf_coil.stp')
    #     pf_coil_case.export_stp('pf_coil_case.stp')

    #     manifest_with_material_tags = [
    #         {
    #             "material_tag": "copper",
    #             "stp_filename": "pf_coil_case.stp"
    #         },
    #         {
    #             "material_tag": "tungsten_carbide",
    #             "stp_filename": "pf_coil.stp"
    #         }
    #     ]
    #     with open('manifest.json', 'w') as outfile:
    #         json.dump(manifest_with_material_tags, outfile)

    #     paramak.utils.trelis_command_to_create_dagmc_h5m(
    #         faceting_tolerance=1e-2,
    #         merge_tolerance=1e-4,
    #         material_key_name='material_tag',
    #         batch=True
    #         )

    #     list_of_mats = paramak.utils.find_material_groups_in_h5m(
    #         filename="dagmc_not_watertight.h5m"
    #     )

    #     assert len(list_of_mats) == 2
    #     assert 'mat:copper' in list_of_mats
    #     assert 'mat:tungsten_carbide' in list_of_mats
    #     # assert 'mat:graveyard' in list_of_mats

    # def test_trelis_command_to_create_dagmc_h5m_with_user_mat_name(self):
    #     """Creats a h5m file with trelis and forms groups using the material_id
    #     key in the manifest.json file. Then checks the groups in the resulting
    #     h5 file match those in the original dictionary"""

    #     os.system('rm *.stp *.h5m *.json')

    #     pf_coil = paramak.PoloidalFieldCoil(
    #         height=10,
    #         width=10,
    #         center_point=(100, 0),
    #         rotation_angle=180,
    #     )

    #     pf_coil_case = paramak.PoloidalFieldCoilCaseFC(
    #         pf_coil=pf_coil,
    #         casing_thickness=5
    #     )

    #     pf_coil.export_stp('pf_coil.stp')
    #     pf_coil_case.export_stp('pf_coil_case.stp')

    #     manifest_with_material_tags = [
    #         {
    #             "material_id": "42",
    #             "stp_filename": "pf_coil_case.stp"
    #         },
    #         {
    #             "material_id": 12,  # this is an int to check the str() works
    #             "stp_filename": "pf_coil.stp"
    #         }
    #     ]
    #     with open('manifest.json', 'w') as outfile:
    #         json.dump(manifest_with_material_tags, outfile)

    #     paramak.utils.trelis_command_to_create_dagmc_h5m(
    #         faceting_tolerance=1e-2,
    #         merge_tolerance=1e-4,
    #         material_key_name='material_id',
    #         batch=True,
    #     )

    #     list_of_mats = paramak.utils.find_material_groups_in_h5m(
    #         filename="dagmc_not_watertight.h5m"
    #     )

    #     assert len(list_of_mats) == 2
    #     assert 'mat:42' in list_of_mats
    #     assert 'mat:12' in list_of_mats
    #     # assert 'mat:graveyard' in list_of_mats

    # def test_trelis_command_to_create_dagmc_h5m_with_custom_geometry_key(self):
    #     """Creats a h5m file with trelis and loads stp files using a custom
    #     key in the manifest.json file. Then checks the groups in the resulting
    #     h5 file match those in the original dictionary"""

    #     os.system('rm *.stp *.h5m *.json')

    #     pf_coil = paramak.PoloidalFieldCoil(
    #         height=10,
    #         width=10,
    #         center_point=(100, 0),
    #         rotation_angle=180,
    #     )

    #     pf_coil_case = paramak.PoloidalFieldCoilCaseFC(
    #         pf_coil=pf_coil,
    #         casing_thickness=5
    #     )

    #     pf_coil.export_stp('pf_coil_custom_key.stp')
    #     pf_coil_case.export_stp('pf_coil_case_custom_key.stp')

    #     manifest_with_material_tags = [
    #         {
    #             "material_tag": "copper",
    #             "geometry_filename": "pf_coil_custom_key.stp"
    #         },
    #         {
    #             "material_tag": "tungsten_carbide",
    #             "geometry_filename": "pf_coil_case_custom_key.stp"
    #         }
    #     ]
    #     with open('manifest.json', 'w') as outfile:
    #         json.dump(manifest_with_material_tags, outfile)

    #     paramak.utils.trelis_command_to_create_dagmc_h5m(
    #         faceting_tolerance=1e-2,
    #         merge_tolerance=1e-4,
    #         geometry_key_name='geometry_filename',
    #         batch=True
    #     )

    #     list_of_mats = paramak.utils.find_material_groups_in_h5m(
    #         filename="dagmc_not_watertight.h5m"
    #     )

    #     assert len(list_of_mats) == 2
    #     assert 'mat:copper' in list_of_mats
    #     assert 'mat:tungsten_carbide' in list_of_mats
