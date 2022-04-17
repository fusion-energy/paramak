import unittest
from pathlib import Path

import dagmc_h5m_file_inspector as di
from paramak import RotateStraightShape


class TestRotateStraightShape(unittest.TestCase):
    """testing the export_dagmc_h5m method of the RotateStraightShape class"""

    def setUp(self):
        self.test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        self.test_shape.graveyard_size = 100

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
        assert mats == ["my_material_name"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_multi_volume.h5m")
        assert vols_and_mats == {
            1: "my_material_name",
            2: "my_material_name",
            3: "my_material_name",
            4: "my_material_name",
        }

    def test_dagmc_h5m_export_custom_tag_multi_volume(self):
        """Exports a shape with multiple volumes and checks that they all
        exist (volume ids and material tags) in the resulting h5m file"""

        self.test_shape.rotation_angle = 10
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.name = "my_material_name"
        self.test_shape.export_dagmc_h5m("dagmc_multi_volume.h5m", tags=["1"])

        vols = di.get_volumes_from_h5m("dagmc_multi_volume.h5m")
        assert vols == [1, 2, 3, 4]

        mats = di.get_materials_from_h5m("dagmc_multi_volume.h5m")
        assert mats == ["1"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_multi_volume.h5m")
        assert vols_and_mats == {
            1: "1",
            2: "1",
            3: "1",
            4: "1",
        }

    def test_dagmc_h5m_export_custom_tag_multi_volume_with_graveyard(self):
        """Exports a shape with multiple volumes and checks that they all
        exist (volume ids and material tags) in the resulting h5m file"""

        self.test_shape.rotation_angle = 10
        self.test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        self.test_shape.name = "my_material_name"
        self.test_shape.export_dagmc_h5m("dagmc_multi_volume.h5m", tags=["1", "graveyard"], include_graveyard=True)

        vols = di.get_volumes_from_h5m("dagmc_multi_volume.h5m")
        assert vols == [1, 2, 3, 4, 5]

        mats = di.get_materials_from_h5m("dagmc_multi_volume.h5m")
        assert mats == ["1", "graveyard"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_multi_volume.h5m")
        assert vols_and_mats == {
            1: "1",
            2: "1",
            3: "1",
            4: "1",
            5: "graveyard",
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
        assert mats == ["my_material_name_single"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_single_volume.h5m")
        assert vols_and_mats == {1: "my_material_name_single"}

    def test_dagmc_h5m_export_single_volume_with_graveyard(self):
        """Exports a shape with a single volume plus graveyard cell and checks
        that it exist (volume id and material tag) in the resulting h5m file"""

        self.test_shape.rotation_angle = 180
        self.test_shape.name = "my_material_name_single"
        self.test_shape.export_dagmc_h5m(filename="dagmc_single_volume.h5m", include_graveyard=True)

        vols = di.get_volumes_from_h5m("dagmc_single_volume.h5m")
        assert vols == [1, 2]

        mats = di.get_materials_from_h5m("dagmc_single_volume.h5m")
        assert "my_material_name_single" in mats
        assert "graveyard" in mats
        assert len(mats) == 2

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_single_volume.h5m")
        assert vols_and_mats == {1: "my_material_name_single", 2: "graveyard"}

    def test_dagmc_h5m_export_single_volume_custom_tags(self):
        """Exports a shape with a single volume and checks that it
        exist (volume id and custom material tag) in the resulting h5m file"""

        self.test_shape.rotation_angle = 180
        self.test_shape.export_dagmc_h5m("dagmc_custom_tag_single_volume.h5m", tags=["1"])

        vols = di.get_volumes_from_h5m("dagmc_custom_tag_single_volume.h5m")
        assert vols == [1]

        mats = di.get_materials_from_h5m("dagmc_custom_tag_single_volume.h5m")
        assert mats == ["1"]

        vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_single_volume.h5m")
        assert vols_and_mats == {1: "my_material_name_single"}

    def test_dagmc_h5m_export_mesh_size(self):
        """Exports h5m file with higher resolution mesh and checks that the
        file sizes increases"""

        self.test_shape.export_dagmc_h5m("dagmc_default.h5m", min_mesh_size=10, max_mesh_size=20)
        self.test_shape.export_dagmc_h5m("dagmc_bigger.h5m", min_mesh_size=2, max_mesh_size=9)

        assert Path("dagmc_bigger.h5m").stat().st_size > Path("dagmc_default.h5m").stat().st_size


if __name__ == "__main__":
    unittest.main()
