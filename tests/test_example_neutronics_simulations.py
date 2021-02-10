
import os
import sys
import unittest
from pathlib import Path

from examples.example_neutronics_simulations import (
    shape_with_gas_production)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleNeutronics(unittest.TestCase):

    def test_make_cad_from_points(self):
        """Runs the example and checks the output files are produced"""
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
        ]
        os.system("rm *.png")
        os.system("rm *.vtk")
        shape_with_gas_production.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True


if __name__ == "__main__":
    unittest.main()
