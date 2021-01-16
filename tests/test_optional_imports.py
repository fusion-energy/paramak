
import unittest

import paramak


class TestImportErrors(unittest.TestCase):

    def test_pymoab_imports_raise_error(self):
        """Checks errors are raised when a pymoab import is attempted"""

        def test_pymoab_import_warning():
            paramak.define_moab_core_and_tags
        self.assertRaises(ImportError, test_pymoab_import_warning)

    def test_save_2d_mesh_tally_as_png_raises_error(self):
        """Checks errors are raised when a openmc import is attempted"""

        def save_2d_mesh_tally_as_png_raises_error():
            paramak._save_2d_mesh_tally_as_png('score', 'no_file.png', 'tally')
        self.assertRaises(ImportError, save_2d_mesh_tally_as_png_raises_error)

    def test_get_neutronics_results_from_statepoint_file_raises_error(self):
        """Checks errors are raised when a openmc import is attempted"""

        def get_neutronics_results_from_statepoint_file_raises_error():
            paramak.get_neutronics_results_from_statepoint_file('no_file.h5m')
        self.assertRaises(ImportError, get_neutronics_results_from_statepoint_file_raises_error)


# neutronics material make_graveyard
# openmc
# vtk
# parametric plasma source

if __name__ == "__main__":
    unittest.main()
