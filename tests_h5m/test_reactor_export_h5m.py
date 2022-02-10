import unittest
from pathlib import Path

import dagmc_h5m_file_inspector as di
import paramak


class TestReactor(unittest.TestCase):
    """testing the export_dagmc_h5m method of the TestReactor class"""

    def setUp(self):
        self.test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], name="test_shape"
        )

        self.test_shape2 = paramak.ExtrudeStraightShape(
            points=[(100, 100), (50, 100), (50, 50)], distance=20, name="test_shape2"
        )

        test_shape_3 = paramak.PoloidalFieldCoilSet(
            heights=[2, 2], widths=[3, 3], center_points=[(50, -100), (50, 100)]
        )

        self.test_reactor = paramak.Reactor([self.test_shape])

        self.test_reactor_2 = paramak.Reactor([self.test_shape, self.test_shape2])

        # this reactor has a compound shape in the geometry
        self.test_reactor_3 = paramak.Reactor([self.test_shape, test_shape_3])

    def test_dagmc_h5m_export(self):
        """Exports a shape with a single volume and checks that it
        exist (volume id and material tag) in the resulting h5m file"""

        self.test_reactor_3.rotation_angle = 180
        self.test_reactor_3.export_dagmc_h5m("dagmc_reactor.h5m")

        vols = di.get_volumes_from_h5m("dagmc_reactor.h5m")
        assert vols == [1, 2, 3]  # there are three volumes in test_reactor_3

        mats = di.get_materials_from_h5m("dagmc_reactor.h5m")
        print(mats)
        assert mats == ["mat_pf_coil", "mat_test_shape"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_reactor.h5m")
        assert vols_and_mats == {
            1: "mat_test_shape",
            2: "mat_pf_coil",
            3: "mat_pf_coil",
        }

    def test_dagmc_h5m_export_mesh_size(self):
        """Exports h5m file with higher resolution mesh and checks that the
        file sizes increases"""

        self.test_reactor_3.export_dagmc_h5m(
            "dagmc_default.h5m", min_mesh_size=10, max_mesh_size=20
        )
        self.test_reactor_3.export_dagmc_h5m(
            "dagmc_bigger.h5m", min_mesh_size=2, max_mesh_size=9
        )

        assert (
            Path("dagmc_bigger.h5m").stat().st_size
            > Path("dagmc_default.h5m").stat().st_size
        )


if __name__ == "__main__":
    unittest.main()
