
import unittest
from pathlib import Path

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

        assert Path('test_file.stl').exists() is True
        assert Path('test_file.h5m').exists() is True
