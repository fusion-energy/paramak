
import unittest
from pathlib import Path

import paramak
from paramak.neutronics_utils import (add_stl_to_moab_core,
                                      define_moab_core_and_tags)
import openmc


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

        create_inital_particles(source, 10)

        assert Path("initial_source.h5").exists() is True

    def extract_points_from_initial_source(self):
        """Creates an initial_source.h5 from a point source reads in the file
        and checks the first point is 0, 0, 0 as exspected."""

        os.system("rm *.h5")

        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.energy = openmc.stats.Discrete([14e6], [1])

        paramak.neutronics_utils.create_inital_particles(source, 100)

        create_inital_particles(source, 10)

        for view_plane in ['XZ', 'XY', 'YZ', 'YX', 'ZY', 'ZX', 'RZ', 'XYZ']:

            points = extract_points_from_initial_source(view_plane=view_plane)

            assert points[0][0] == 0
            assert points[0][1] == 0
            assert points[0][2] == 0
