
import os
import unittest
from pathlib import Path

import paramak
import pytest


class TestShape(unittest.TestCase):

    def test_shape_default_properties(self):
        """Creates a Shape object and checks that the points attribute has
        a default of None."""

        test_shape = paramak.Shape()

        assert test_shape.points is None

    def test_azimuth_placement_angle_getting_setting(self):
        """Checks that the azimuth_placement_angle of a Shape can be
        changed to a single value or iterable."""

        test_shape = paramak.Shape()

        assert test_shape.azimuth_placement_angle == 0
        test_shape.azimuth_placement_angle = 180
        assert test_shape.azimuth_placement_angle == 180
        test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        assert test_shape.azimuth_placement_angle == [0, 90, 180, 270]

    def test_incorrect_color_values(self):
        """Checks that an error is raised when the color of a shape is
        defined as an invalid string."""

        def incorrect_color_string():
            paramak.Shape(color=('1', '0', '1'))

        self.assertRaises(
            ValueError,
            incorrect_color_string
        )

    def test_incorrect_workplane(self):
        """Creates Shape object with incorrect workplane and checks ValueError
        is raised."""

        test_shape = paramak.Shape()

        def incorrect_workplane():
            """Creates Shape object with unacceptable workplane."""

            test_shape.workplane = "AB"

        self.assertRaises(ValueError, incorrect_workplane)

    def test_incorrect_points(self):
        """Creates Shape objects and checks errors are raised correctly when
        specifying points."""

        test_shape = paramak.Shape()

        def incorrect_points_end_point_is_start_point():
            """Checks ValueError is raised when the start and end points are
            the same."""

            test_shape.points = [(0, 200), (200, 100), (0, 0), (0, 200)]

        self.assertRaises(
            ValueError,
            incorrect_points_end_point_is_start_point)

        def incorrect_points_missing_z_value():
            """Checks ValueError is raised when a point is missing a z
            value."""

            test_shape.points = [(0, 200), (200), (0, 0), (0, 50)]

        self.assertRaises(ValueError, incorrect_points_missing_z_value)

        def incorrect_points_not_a_list():
            """Checks ValueError is raised when the points are not a list."""

            test_shape.points = (0, 0), (0, 20), (20, 20), (20, 0)

        self.assertRaises(ValueError, incorrect_points_not_a_list)

        def incorrect_points_wrong_number_of_entries():
            """Checks ValueError is raised when individual points dont have 2
            or 3 entries."""

            test_shape.points = [(0, 0), (0, 20), (20, 20, 20, 20)]

        self.assertRaises(ValueError, incorrect_points_wrong_number_of_entries)

        def incorrect_x_point_value_type():
            """Checks ValueError is raised when X point is not a number."""

            test_shape.points = [("string", 0), (0, 20), (20, 20)]

        self.assertRaises(ValueError, incorrect_x_point_value_type)

        def incorrect_y_point_value_type():
            """Checks ValueError is raised when Y point is not a number."""

            test_shape.points = [(0, "string"), (0, 20), (20, 20)]

        self.assertRaises(ValueError, incorrect_y_point_value_type)

    def test_create_limits(self):
        """Creates a Shape object and checks that the create_limits function
        returns the expected values for x_min, x_max, z_min and z_max."""

        test_shape = paramak.Shape()

        test_shape.points = [
            (0, 0),
            (0, 10),
            (0, 20),
            (10, 20),
            (20, 20),
            (20, 10),
            (20, 0),
            (10, 0),
        ]

        assert test_shape.create_limits() == (0.0, 20.0, 0.0, 20.0)

        # test with a component which has a find_points method
        test_shape2 = paramak.Plasma()
        test_shape2.create_limits()
        assert test_shape2.x_min is not None

    def test_create_limits_error(self):
        """Checks error is raised when no points are given."""

        test_shape = paramak.Shape()

        def limits():
            test_shape.create_limits()
        self.assertRaises(ValueError, limits)

    def test_export_2d_image(self):
        """Creates a Shape object and checks that a png file of the object with
        the correct suffix can be exported using the export_2d_image method."""

        test_shape = paramak.Shape()
        test_shape.points = [(0, 0), (0, 20), (20, 20), (20, 0)]
        os.system("rm filename.png")
        test_shape.export_2d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        test_shape.export_2d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")

    def test_initial_solid_construction(self):
        """Creates a shape and checks that a cadquery solid with a unique hash
        value is created when .solid is called."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """Checks that the same cadquery solid with the same unique hash value
        is returned when shape.solid is called again after no changes have been
        made to the Shape."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.solid is not None
        initial_hash_value = test_shape.hash_value
        assert test_shape.solid is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """Checks that a new cadquery solid with a new unique hash value is
        constructed when shape.solid is called after changes to the Shape have
        been made."""

        test_shape = paramak.RotateStraightShape(
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
        """Checks that the hash value of a Shape is not updated until a new
        cadquery solid has been created."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_material_tag_warning(self):
        """Checks that a warning is raised when a Shape has a material tag >
        28 characters."""

        test_shape = paramak.Shape()

        def warning_material_tag():

            test_shape.material_tag = "abcdefghijklmnopqrstuvwxyz12345"

        self.assertWarns(UserWarning, warning_material_tag)

    def test_invalid_material_tag(self):
        """Checks a ValueError is raised when a Shape has an invalid material
        tag."""

        test_shape = paramak.Shape()

        def invalid_material_tag():

            test_shape.material_tag = 123

        self.assertRaises(ValueError, invalid_material_tag)

    def test_export_html(self):
        """Checks a plotly figure of the Shape is exported by the export_html
        method with the correct filename with RGB and RGBA colors."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        os.system("rm filename.html")
        test_shape.export_html('filename')
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")
        test_shape.color = (1, 0, 0, 0.5)
        test_shape.export_html('filename')
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")

    def test_export_html_with_points_None(self):
        """Checks that an error is raised when points is None and export_html
        """
        test_shape = paramak.Shape()

        def export():
            test_shape.export_html("out.html")
        self.assertRaises(ValueError, export)

    def test_invalid_stp_filename(self):
        """Checks ValueError is raised when invalid stp filenames are used."""

        def invalid_filename_suffix():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename="filename.invalid_suffix"
            )

        self.assertRaises(ValueError, invalid_filename_suffix)

        def invalid_filename_type():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename=123456
            )

        self.assertRaises(ValueError, invalid_filename_type)

    def test_invalid_stl_filename(self):
        """Checks ValueError is raised when invalid stl filenames are used."""

        def invalid_filename_suffix():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename="filename.invalid_suffix"
            )

        self.assertRaises(ValueError, invalid_filename_suffix)

        def invalid_filename_type():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename=123456
            )

        self.assertRaises(ValueError, invalid_filename_type)

    def test_invalid_color(self):
        """Checks ValueError is raised when invalid colors are used."""

        def invalid_color_type():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                color=255
            )

        self.assertRaises(ValueError, invalid_color_type)

        def invalid_color_length():

            paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                color=(255, 255, 255, 1, 1)
            )

        self.assertRaises(ValueError, invalid_color_length)

    def test_volumes_add_up_to_total_volume_Compound(self):
        """Checks the volume and volumes attributes are correct types
        and that the volumes sum to equalt the volume for a Compound."""

        test_shape = paramak.PoloidalFieldCoilSet(
            heights=[10, 10],
            widths=[20, 20],
            center_points=[(15, 15), (50, 50)]
        )

        assert isinstance(test_shape.volume, float)
        assert isinstance(test_shape.volumes, list)
        assert isinstance(test_shape.volumes[0], float)
        assert isinstance(test_shape.volumes[1], float)
        assert len(test_shape.volumes) == 2
        assert sum(test_shape.volumes) == pytest.approx(test_shape.volume)

    def test_volumes_add_up_to_total_volume(self):
        """Checks the volume and volumes attributes are correct types
        and that the volumes sum to equalt the volume."""

        test_shape = paramak.PoloidalFieldCoil(
            center_point=(100, 100),
            height=50,
            width=50
        )

        assert isinstance(test_shape.volume, float)
        assert isinstance(test_shape.volumes, list)
        assert isinstance(test_shape.volumes[0], float)
        assert len(test_shape.volumes) == 1
        assert sum(test_shape.volumes) == pytest.approx(test_shape.volume)

    def test_areas_add_up_to_total_area_Compound(self):
        """Checks the area and areas attributes are correct types
        and that the areas sum to equalt the area for a Compound."""

        test_shape = paramak.PoloidalFieldCoilSet(
            heights=[10, 10],
            widths=[20, 20],
            center_points=[(15, 15), (50, 50)]
        )

        assert isinstance(test_shape.area, float)
        assert isinstance(test_shape.areas, list)
        assert isinstance(test_shape.areas[0], float)
        assert isinstance(test_shape.areas[1], float)
        assert isinstance(test_shape.areas[2], float)
        assert isinstance(test_shape.areas[3], float)
        assert isinstance(test_shape.areas[4], float)
        assert isinstance(test_shape.areas[5], float)
        assert isinstance(test_shape.areas[6], float)
        assert isinstance(test_shape.areas[7], float)
        assert len(test_shape.areas) == 8
        assert sum(test_shape.areas) == pytest.approx(test_shape.area)

    def test_areas_add_up_to_total_area(self):
        """Checks the area and areas attributes are correct types
        and that the areas sum to equalt the area."""

        test_shape = paramak.PoloidalFieldCoil(
            center_point=(100, 100),
            height=50,
            width=50
        )

        assert isinstance(test_shape.area, float)
        assert isinstance(test_shape.areas, list)
        assert isinstance(test_shape.areas[0], float)
        assert isinstance(test_shape.areas[1], float)
        assert isinstance(test_shape.areas[2], float)
        assert isinstance(test_shape.areas[3], float)
        assert len(test_shape.areas) == 4
        assert sum(test_shape.areas) == pytest.approx(test_shape.area)

    def test_trace(self):
        """Test trace method is populated"""

        test_shape = paramak.PoloidalFieldCoil(
            center_point=(100, 100),
            height=50,
            width=50,
            name="coucou"
        )
        assert test_shape._trace() is not None

    def test_create_patch_error(self):
        """Checks _create_patch raises a ValueError when points is None."""

        test_shape = paramak.Shape()

        def patch():
            test_shape._create_patch()
        self.assertRaises(ValueError, patch)

    def test_create_patch_alpha(self):
        """Checks _create_patch returns a patch when alpha is given."""

        test_shape = paramak.PoloidalFieldCoil(
            center_point=(100, 100),
            height=50,
            width=50,
            color=(0.5, 0.5, 0.5, 0.1)
        )
        assert test_shape._create_patch() is not None

    def test_azimuth_placement_angle_error(self):
        """Checks an error is raised when invalid value for
        azimuth_placement_angle is set.
        """

        test_shape = paramak.Shape()

        def angle_str():
            test_shape.azimuth_placement_angle = "coucou"

        def angle_str_in_Iterable():
            test_shape.azimuth_placement_angle = [0, "coucou"]

        self.assertRaises(ValueError, angle_str)
        self.assertRaises(ValueError, angle_str_in_Iterable)

    def test_name_error(self):
        """Checks an error is raised when invalid value for name is set."""

        test_shape = paramak.Shape()

        def name_float():
            test_shape.name = 2.0

        def name_int():
            test_shape.name = 1

        def name_list():
            test_shape.name = ['coucou']

        self.assertRaises(ValueError, name_float)
        self.assertRaises(ValueError, name_int)
        self.assertRaises(ValueError, name_list)

    def test_tet_mesh_error(self):
        """Checks an error is raised when invalid value for tet_mesh is set.
        """

        test_shape = paramak.Shape()

        def tet_mesh_float():
            test_shape.tet_mesh = 2.0

        def tet_mesh_int():
            test_shape.tet_mesh = 1

        def tet_mesh_list():
            test_shape.tet_mesh = ['coucou']

        self.assertRaises(ValueError, tet_mesh_float)
        self.assertRaises(ValueError, tet_mesh_int)
        self.assertRaises(ValueError, tet_mesh_list)

    def test_get_rotation_axis(self):
        """Creates a shape and test the expected rotation_axis is the correct
        values for several cases
        """
        shape = paramak.Shape()
        expected_dict = {
            "X": [(-1, 0, 0), (1, 0, 0)],
            "-X": [(1, 0, 0), (-1, 0, 0)],
            "Y": [(0, -1, 0), (0, 1, 0)],
            "-Y": [(0, 1, 0), (0, -1, 0)],
            "Z": [(0, 0, -1), (0, 0, 1)],
            "-Z": [(0, 0, 1), (0, 0, -1)],
        }
        # test with axis from string
        for axis in expected_dict:
            shape.rotation_axis = axis
            assert shape.get_rotation_axis()[0] == expected_dict[axis]
            assert shape.get_rotation_axis()[1] == axis

        # test with axis from list of two points
        expected_axis = [(-1, -2, -3), (1, 4, 5)]
        shape.rotation_axis = expected_axis
        assert shape.get_rotation_axis()[0] == expected_axis
        assert shape.get_rotation_axis()[1] == "custom_axis"

        # test with axis from workplane
        shape.rotation_axis = None

        workplanes = ["XY", "XZ", "YZ"]
        expected_axis = ["Y", "Z", "Z"]
        for wp, axis in zip(workplanes, expected_axis):
            shape.workplane = wp
            assert shape.get_rotation_axis()[0] == expected_dict[axis]
            assert shape.get_rotation_axis()[1] == axis

        # test with axis from path_workplane
        for wp, axis in zip(workplanes, expected_axis):
            shape.path_workplane = wp
            assert shape.get_rotation_axis()[0] == expected_dict[axis]
            assert shape.get_rotation_axis()[1] == axis

    def test_rotation_axis_error(self):
        """Checks errors are raised when incorrect values of rotation_axis are
        set
        """
        incorrect_values = [
            "coucou",
            2,
            2.2,
            [(1, 1, 1), 'coucou'],
            [(1, 1, 1), 1],
            [(1, 1, 1), 1.0],
            [(1, 1, 1), (1, 1, 1)],
            [(1, 1, 1), (1, 0, 1, 2)],
            [(1, 1, 1, 2), (1, 0, 2)],
            [(1, 1, 2), [1, 0, 2]],
            [(1, 1, 1)],
            [(1, 1, 1), (1, 'coucou', 1)],
            [(1, 1, 1), (1, 0, 1), (1, 2, 3)],
        ]
        shape = paramak.Shape()

        def set_value():
            shape.rotation_axis = incorrect_values[i]

        for i in range(len(incorrect_values)):
            self.assertRaises(ValueError, set_value)


if __name__ == "__main__":
    unittest.main()
