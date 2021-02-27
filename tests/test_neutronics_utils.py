
import os
import unittest
from pathlib import Path

import openmc
import paramak
from paramak.neutronics_utils import (add_stl_to_moab_core,
                                      define_moab_core_and_tags)


class TestNeutronicsUtilityFunctions(unittest.TestCase):

    def test_moab_instance_creation(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

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

    def test_create_inital_source_file(self):
        """Creates an initial_source.h5 from a point source"""

        os.system("rm *.h5")

        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.energy = openmc.stats.Discrete([14e6], [1])

        paramak.neutronics_utils.create_inital_particles(source, 100)

        assert Path("initial_source.h5").exists() is True

    def test_extract_points_from_initial_source(self):
        """Creates an initial_source.h5 from a point source reads in the file
        and checks the first point is 0, 0, 0 as exspected."""

        os.system("rm *.h5")

        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.energy = openmc.stats.Discrete([14e6], [1])

        paramak.neutronics_utils.create_inital_particles(source, 10)

        for view_plane in ['XZ', 'XY', 'YZ', 'YX', 'ZY', 'ZX', 'RZ', 'XYZ']:

            points = paramak.neutronics_utils.extract_points_from_initial_source(
                view_plane=view_plane)

            assert len(points) == 10

            for point in points:
                if view_plane == 'XYZ':
                    assert len(point) == 3
                    assert point[0] == 0
                    assert point[1] == 0
                    assert point[2] == 0
                else:
                    assert len(point) == 2
                    assert point[0] == 0
                    assert point[1] == 0

    def test_extract_points_from_initial_source_incorrect_view_plane(self):
        """Tries to make extract points on to viewplane that is not accepted"""

        def incorrect_viewplane():
            """Inccorect view_plane should raise a ValueError"""

            source = openmc.Source()
            source.space = openmc.stats.Point((0, 0, 0))
            source.energy = openmc.stats.Discrete([14e6], [1])

            paramak.neutronics_utils.create_inital_particles(source, 10)

            paramak.neutronics_utils.extract_points_from_initial_source(
                view_plane='coucou'
            )

        self.assertRaises(ValueError, incorrect_viewplane)
