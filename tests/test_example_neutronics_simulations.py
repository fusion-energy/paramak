
import os
import sys
import unittest
from pathlib import Path

from examples.example_neutronics_simulations import (
    shape_with_gas_production,
    component_based_mesh_simulation,
    component_based_parameter_study,
    shape_with_spectra_cell_tally)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleNeutronics(unittest.TestCase):

    def test_shape_with_gas_production(self):
        """Runs the example and checks the output files are produced"""
        os.system("rm *.png *.vtk *.json *.h5")
        output_filenames = [
            "results.json",
            "n-Xp_on_2D_mesh_yz.png",
            "n-Xp_on_2D_mesh_xy.png",
            "n-Xp_on_2D_mesh_xz.png",
            "n-Xt_on_2D_mesh_yz.png",
            "n-Xt_on_2D_mesh_xy.png",
            "n-Xt_on_2D_mesh_xz.png",
            "n-Xa_on_2D_mesh_yz.png",
            "n-Xa_on_2D_mesh_xy.png",
            "n-Xa_on_2D_mesh_xz.png",
            "n-Xp_on_3D_mesh.vtk",
            "n-Xt_on_3D_mesh.vtk",
            "n-Xa_on_3D_mesh.vtk",
            "summary.h5",
        ]

        shape_with_gas_production.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_component_based_mesh_simulation(self):
        """Runs the example and checks the output files are produced"""
        os.system("rm *.png *.vtk *.json *.h5 *.stp")
        output_filenames = [
            "results.json",
            "statepoint.10.h5",
            "summary.h5",
            "my_shape.stp",
            "heating_on_2D_mesh_yz.png",
            "heating_on_2D_mesh_yz.png",
            "heating_on_2D_mesh_xz.png",
            "heating_on_3D_mesh.vtk",
        ]

        component_based_mesh_simulation.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_component_based_parameter_study(self):
        """Runs the example and checks the output files are produced"""
        os.system("rm *.png *.vtk *.json *.h5 *.stp")
        output_filenames = [
            "my_shape60.stp",
            "my_shape70.stp",
            "my_shape80.stp",
            "results.json",
            "heating_vs_thickness.svg",
            "statepoint.10.h5",
            "summary.h5",
        ]

        component_based_parameter_study.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_shape_with_spectra_cell_tally(self):
        """Runs the example and checks the output files are produced"""
        os.system("rm *.png *.vtk *.json *.h5")
        output_filenames = [
            "results.json",
            "statepoint.2.h5",
            "summary.h5",
        ]

        shape_with_spectra_cell_tally.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True


if __name__ == "__main__":
    unittest.main()
