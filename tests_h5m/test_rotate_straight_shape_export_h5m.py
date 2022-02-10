import unittest
from pathlib import Path

import dagmc_h5m_file_inspector as di
from paramak import RotateStraightShape


class TestRotateStraightShape(unittest.TestCase):
    """testing the export_dagmc_h5m method of the RotateStraightShape class"""

    def setUp(self):
        self.test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )

    def test_dagmc_h5m_export_multi_volume(self):
        """Exports a shape with multiple volumes and checks that they all
        exist (volume ids and material tags) in the resulting h5m file"""

        self.test_shape.rotation_angle = 10
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.name = "my_material_name"
        self.test_shape.export_dagmc_h5m("dagmc_multi_volume.h5m")

        vols = di.get_volumes_from_h5m("dagmc_multi_volume.h5m")
        assert vols == [1, 2, 3, 4]

        mats = di.get_materials_from_h5m("dagmc_multi_volume.h5m")
        assert mats == ["mat_my_material_name"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_multi_volume.h5m")
        assert vols_and_mats == {
            1: "mat_my_material_name",
            2: "mat_my_material_name",
            3: "mat_my_material_name",
            4: "mat_my_material_name",
        }

    def test_dagmc_h5m_export_single_volume(self):
        """Exports a shape with a single volume and checks that it
        exist (volume id and material tag) in the resulting h5m file"""

        self.test_shape.rotation_angle = 180
        self.test_shape.name = "my_material_name_single"
        self.test_shape.export_dagmc_h5m("dagmc_single_volume.h5m")

        vols = di.get_volumes_from_h5m("dagmc_single_volume.h5m")
        assert vols == [1]

        mats = di.get_materials_from_h5m("dagmc_single_volume.h5m")
        assert mats == ["mat_my_material_name_single"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_single_volume.h5m")
        assert vols_and_mats == {1: "mat_my_material_name_single"}

    def test_dagmc_h5m_export_mesh_size(self):
        """Exports h5m file with higher resolution mesh and checks that the
        file sizes increases"""

        self.test_shape.export_dagmc_h5m(
            "dagmc_default.h5m", min_mesh_size=10, max_mesh_size=20
        )
        self.test_shape.export_dagmc_h5m(
            "dagmc_bigger.h5m", min_mesh_size=2, max_mesh_size=9
        )

        assert (
            Path("dagmc_bigger.h5m").stat().st_size
            > Path("dagmc_default.h5m").stat().st_size
        )


if __name__ == "__main__":
    unittest.main()
