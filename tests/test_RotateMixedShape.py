import unittest

import pytest

from paramak import RotateMixedShape
import os
from pathlib import Path


class test_object_properties(unittest.TestCase):
    def test_union_volume_addition(self):
        """fuses two RotateMixedShapes and checks that their fused volume
        is correct"""

        inner_box = RotateMixedShape(
            points=[
                (100, 100, "straight"),
                (100, 200, "straight"),
                (200, 200, "straight"),
                (200, 100, "straight"),
            ],
            rotation_angle=20,
        )

        outer_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ],
            rotation_angle=20,
        )

        outer_box_and_inner_box = RotateMixedShape(
            points=[
                (200, 100, "straight"),
                (200, 200, "straight"),
                (500, 200, "straight"),
                (500, 100, "straight"),
            ],
            rotation_angle=20,
            union=inner_box,
        )

        assert inner_box.volume + outer_box.volume == pytest.approx(
            outer_box_and_inner_box.volume
        )

    def test_absolute_shape_volume(self):
        """creates rotated shapes using mixed connections and checks the volumes
        are correct"""

        test_shape = RotateMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "spline"),
                (20, 20, "spline"),
                (20, 0, "spline"),
            ]
        )

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 100

        test_shape2 = RotateMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "spline"),
                (20, 20, "spline"),
                (20, 0, "spline"),
            ]
        )

        test_shape2.rotation_angle = 180
        test_shape2.create_solid()

        assert test_shape2.solid is not None
        assert 2 * test_shape2.volume == test_shape.volume

    def test_shape_volume_with_multiple_azimuth_placement_angles(self):
        """creates rotated shapes at multiple placement angles using mixed connections
        and checks the volumes are correct"""

        test_shape = RotateMixedShape(
            points=[
                (1, 1, "straight"),
                (1, 20, "spline"),
                (20, 20, "spline"),
                (20, 1, "spline"),
            ]
        )

        test_shape.rotation_angle = 10
        test_shape.azimuth_placement_angle = [0, 90, 180, 270]
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 100

        test_shape2 = RotateMixedShape(
            points=[
                (1, 1, "straight"),
                (1, 20, "spline"),
                (20, 20, "spline"),
                (20, 1, "spline"),
            ]
        )

        test_shape2.rotation_angle = 5
        test_shape2.azimuth_placement_angle = [0, 90, 180, 270]
        test_shape2.create_solid()

        assert test_shape2.solid is not None
        assert 2 * test_shape2.volume == pytest.approx(test_shape.volume)

        test_shape3 = RotateMixedShape(
            points=[
                (1, 1, "straight"),
                (1, 20, "spline"),
                (20, 20, "spline"),
                (20, 1, "spline"),
            ]
        )

        test_shape3.rotation_angle = 20
        test_shape3.azimuth_placement_angle = [0, 180]
        test_shape3.create_solid()

        assert test_shape3.solid is not None
        assert test_shape3.volume == pytest.approx(test_shape.volume)

    def test_incorrect_connections(self):
        """creates rotated straight shapes to check errors are correctly raised when
        specifying connections"""

        def incorrect_string_for_connection_type():
            """checks ValueError is raised when an invalid connection type is specified"""

            test_shape = RotateMixedShape(
                points=[
                    (0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    (20, 0, "not_a_valid_entry"),
                ]
            )

        self.assertRaises(ValueError, incorrect_string_for_connection_type)

        def incorrect_number_of_connections_function():
            """checks ValueError is raised when an incorrect number of connections is
            specified"""

            test_shape = RotateMixedShape(
                points=[(0, 200, "straight"), (200, 100), (0, 0, "spline"), ]
            )

            test_shape.create_solid()

        self.assertRaises(ValueError, incorrect_number_of_connections_function)

    def test_cut_volume(self):
        """creates a rotated shape using mixed connections with another shape cut out
        and checks that the volume is correct"""

        inner_shape = RotateMixedShape(
            points=[
                (5, 5, "straight"),
                (5, 10, "spline"),
                (10, 10, "spline"),
                (10, 5, "spline"),
            ],
            rotation_angle=180,
        )

        outer_shape = RotateMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            rotation_angle=180,
        )

        outer_shape_cut = RotateMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline"),
            ],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(862.5354)
        assert outer_shape.volume == pytest.approx(2854.5969)
        assert outer_shape_cut.volume == pytest.approx(2854.5969 - 862.5354)

    def test_initial_solid_construction(self):
        """creates a rotated shape using mixed connections and checks that a cadquery solid with
        a unique hash value is created when .solid is called"""

        test_shape = RotateMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "spline"),
                (20, 20, "spline"),
                (20, 0, "straight"),
            ],
            rotation_angle=360,
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """checks that the same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the RotateMixedShape"""

        test_shape = RotateMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "spline"),
                (20, 20, "spline"),
                (20, 0, "straight"),
            ],
            rotation_angle=360,
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """checks that a new cadquery solid with a new unique hash value is constructed when .solid
        is called after changes to the RotateMixedShape have been made"""

        test_shape = RotateMixedShape(
            points=[(0, 0, "straight"), (0, 20, "spline"), (20, 20, "spline"), ],
            rotation_angle=360,
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """checks that the hash value of a RotateMixedShape is not updated until a new cadquery
        solid has been created"""

        test_shape = RotateMixedShape(
            points=[(0, 0, "straight"), (0, 20, "spline"), (20, 20, "spline"), ],
            rotation_angle=360,
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_mixed_shape_with_straight_and_circle(self):
        """creates a rotated shape with straight and circular connections and checks
        the volume is correct"""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
        )
        assert test_shape.volume > 10 * 10

    def test_export_stp(self):
        """creates a RotateMixedShape and checks that an stp file of the shape can be
        exported using the export_stp method"""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
        )
        os.system("rm tests/test.stp")
        test_shape.export_stp("tests/test.stp")
        assert Path("tests/test.stp").exists() is True
        os.system("rm tests/test.stp")

        test_shape.stp_filename = "tests/test.stp"
        test_shape.export_stp()
        assert Path("tests/test.stp").exists() is True
        os.system("rm tests/test.stp")

    def test_export_stl(self):
        """creates a RotateMixedShape and checks that an stl file of the shape can be
        exported using the export_stl method"""

        test_shape = RotateMixedShape(
            points=[
                (10, 20, "straight"),
                (10, 10, "straight"),
                (20, 10, "circle"),
                (40, 15, "circle"),
                (20, 20, "straight"),
            ],
            rotation_angle=10,
        )
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test.stl")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")
        test_shape.export_stl("tests/test")
        assert Path("tests/test.stl").exists() is True
        os.system("rm tests/test.stl")


if __name__ == "__main__":
    unittest.main()
