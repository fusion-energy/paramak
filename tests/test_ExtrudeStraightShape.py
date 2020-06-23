
import unittest

import pytest

from paramak import ExtrudeStraightShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates an extruded shape with one placement angle using straight \
                connections and checks the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=30
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30)

    def test_extruded_shape_volume(self):
        """creates an extruded shape with multiple placement angles using straight \
                connections and checks the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(5, 0), (5, 20), (15, 20), (15, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = 0

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 1)

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 4)

    def test_extruded_shape_with_overlap_volume(self):
        """creates an extruded shape with multiple placement angles with overlap \
                using straight connections and checks the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (10, 20), (10, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx((10 * 20 * 10 * 4) - (5 * 20 * 5 * 4))

    def test_cut_volume(self):
        """creates an extruded shape with one placement angle using straight \
                connections with another shape cut out and checks the volume \
                is correct"""

        inner_shape = ExtrudeStraightShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], distance=30
        )

        outer_shape = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], distance=30
        )

        outer_shape_with_cut = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            distance=30,
        )

        assert inner_shape.volume == pytest.approx(5 * 5 * 30)
        assert outer_shape.volume == pytest.approx(9 * 9 * 30)
        assert outer_shape_with_cut.volume == pytest.approx(
            (9 * 9 * 30) - (5 * 5 * 30), abs=0.1
        )

    def test_initial_solid_construction(self):
        """tests that a cadquery solid with a unique hash is constructed when .solid is called"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=20
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """tests that the same cadquery solid with the same unique hash is returned when shape.solid is called again when no changes have been made to the shape"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """tests that a new cadquery solid with a new unique hash is constructed when .solid is called again after changes have been made to the shape"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """tests that the hash_value of the shape is not updated until a new solid has been created"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_conditional_solid_reconstruction_parameters(self):
        """tests that a new cadquery solid with a new unique hash is created when the shape properties of points, distance, workplane, name, color, material_tag, stp_filename, azimuth_placement_angle or cut are changed"""

        # points
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.points = [(0, 0), (10, 30), (15, 50), (25, 5), (15, 0)]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # distance
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.distance = 30
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # workplane
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            workplane="XZ",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.workplane = "YZ"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value
        
        # name
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            name='test_name',
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.name = 'new_name'
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # color
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            color=[0.5, 0.5, 0.5],
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.color = [0.1, 0.2, 0.8]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # material_tag
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            material_tag='test_material',
        )        
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.material_tag = 'new_material'
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # stp_filename
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            stp_filename='test_filename.stp',
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.stp_filename = 'new_filename.stp'
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # azimuth_placement_angle
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            azimuth_placement_angle=0,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.azimuth_placement_angle = 180
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # cut
        cut_shape = ExtrudeStraightShape(
            points=[(5, 5), (5, 15), (15, 15)],
            distance=5
        )

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.cut = cut_shape
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
