import os
import unittest
from pathlib import Path

import pytest

from paramak import RotateStraightShape


class test_object_properties(unittest.TestCase):
    def test_union_volume_addition(self):
        """fuses two RotateStraightShapes and checks that their fused volume is correct"""

        inner_box = RotateStraightShape(
            points=[(100, 100), (100, 200), (200, 200), (200, 100)], rotation_angle=20
        )

        outer_box = RotateStraightShape(
            points=[(200, 100), (200, 200), (500, 200), (500, 100)], rotation_angle=20
        )

        outer_box_and_inner_box = RotateStraightShape(
            points=[(200, 100), (200, 200), (500, 200), (500, 100)],
            rotation_angle=20,
            union=inner_box,
        )

        assert inner_box.volume + outer_box.volume == pytest.approx(
            outer_box_and_inner_box.volume, rel=0.01
        )

    def test_shape_rotation_angle_default(self):
        """checks that the default rotation angle of a RotateStraightShape is 360 degrees"""

        test_shape = RotateStraightShape(points=None)
        assert test_shape.rotation_angle == 360

    def test_shape_rotation_angle_setting_getting(self):
        """checks that the rotation angle of a RotateStraightShape can be set"""

        test_shape = RotateStraightShape(points=None)
        test_shape.rotation_angle = 180
        assert test_shape.rotation_angle == 180
        test_shape.rotation_angle = 90
        assert test_shape.rotation_angle == 90

    def test_shape_azimuth_placement_angle_default(self):
        """checks that the default azimuth placement angle of a RotateStraightShape is 0"""

        test_shape = RotateStraightShape(points=None)
        assert test_shape.azimuth_placement_angle == 0

    def test_shape_azimuth_placement_angle_setting_getting(self):
        """checks that the azimuth placement angle of a RotateStraightShape can be set to
        single values or a list of values"""

        test_shape = RotateStraightShape(points=None)
        test_shape.azimuth_placement_angle = 180
        assert test_shape.azimuth_placement_angle == 180
        test_shape.azimuth_placement_angle = 90
        assert test_shape.azimuth_placement_angle == 90
        test_shape.azimuth_placement_angle = [0, 90, 180, 360]
        assert test_shape.azimuth_placement_angle == [0, 90, 180, 360]

    def test_absolute_shape_volume(self):
        """creates a rotated straight shape using straight connections and checks that the
        volume is correct"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(3.141592654 * 20 * 20 * 20)

    def test_relative_shape_volume(self):
        """creates two rotated shapes using straight connections and checks that their
        relative volumes are correct"""

        test_shape_1 = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        test_shape_1.rotation_angle = 180
        test_shape_1.create_solid()

        test_shape_2 = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        test_shape_2.rotation_angle = 360
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(test_shape_2.volume * 0.5)

    def test_export_stp(self):
        """creates a RotateStraightShape and checks that an stp file of the shape can
        be exported with the correct suffix using the export_stp method"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        test_shape.rotation_angle = 360
        os.system("rm filename.stp filename.step")
        test_shape.export_stp("filename.stp")
        test_shape.export_stp("filename.step")
        assert Path("filename.stp").exists() is True
        assert Path("filename.step").exists() is True
        os.system("rm filename.stp filename.step")
        test_shape.export_stp("filename")
        assert Path("filename.stp").exists() is True
        os.system("rm filename.stp")

    def test_export_stl(self):
        """creates a RotateStraightShape and checks that an stl file of the shape
        can be exported with the correct suffix using the export_stl method"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        test_shape.rotation_angle = 360
        os.system("rm filename.stl")
        test_shape.export_stl("filename")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")
        test_shape.export_stl("filename.stl")
        assert Path("filename.stl").exists() is True
        os.system("rm filename.stl")

    def test_export_svg(self):
        """creates a RotateStraightShape and checks that an svg file of the shape
        can be exported with the correct suffix using the export_svg method"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])
        test_shape.rotation_angle = 360
        os.system("rm filename.svg")
        test_shape.export_svg("filename")
        assert Path("filename.svg").exists() is True
        os.system("rm filename.svg")
        test_shape.export_svg("filename.svg")
        assert Path("filename.svg").exists() is True
        os.system("rm filename.svg")

    def test_cut_volume(self):
        """creates a rotated shape using straight connections with another shape cut out
        and checks that the volume is correct"""

        inner_shape = RotateStraightShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], rotation_angle=180
        )

        outer_shape = RotateStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(589.048622)
        assert outer_shape.volume == pytest.approx(1908.517537)
        assert outer_shape_with_cut.volume == pytest.approx(
            1908.517537 - 589.048622)

    def test_initial_solid_construction(self):
        """creates a rotated shape using staright connections and checks that a cadquery solid with
        a unique hash value is created when .solid is called"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """checks that the same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the RotateStraightShape"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """checks that a new cadquery solid with a new unique hash value is constructed when
        shape.solid is called after changes to the RotateStraightShape have been made"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """checks that the hash value of a RotateStraightShape is not updated until a new cadquery
        solid has been created"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_conditional_solid_reconstruction_parameters(self):
        """checks that a new cadquery solid with a new unique hash value is created when the
        RotateStraightShape parameters of 'points', 'workplane', 'name', 'color', 'material_tag',
        'stp_filename', 'azimuth_placement_angle', 'rotation_angle' or 'cut' are changed"""

        # points
        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)],)
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.points = [(0, 0), (10, 30), (15, 50), (25, 5), (15, 0)]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # workplane
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], workplane="XZ",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.workplane = "YZ"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # name
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], name="test_name",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.name = "new_name"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # color
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], color=[0.5, 0.5, 0.5],
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.color = [0.1, 0.2, 0.8]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # material_tag
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], material_tag="test_material",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.material_tag = "new_material"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # stp_filename
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], stp_filename="test_filename.stp",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.stp_filename = "new_filename.stp"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # azimuth_placement_angle
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], azimuth_placement_angle=0,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.azimuth_placement_angle = 180
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # rotation_angle
        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.rotation_angle = 180
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # cut
        cut_shape = RotateStraightShape(points=[(5, 5), (5, 15), (15, 15)],)

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)],)
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.cut = cut_shape
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
