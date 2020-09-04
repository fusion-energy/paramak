import unittest

import pytest

from paramak import ExtrudeStraightShape


class test_object_properties(unittest.TestCase):
    def test_intersect_volume_2_shapes(self):
        """creates two extruded shapes using straight connections with the second shape
        intersecting the first and checks that the volume is correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=30
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=test_shape1,
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25)

    def test_intersect_volume_3_shapes(self):
        """creates three extruded shapes using straight connections with the second and
        third shapes intersecting the first and checks that the volume is correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=30
        )
        test_shape2 = ExtrudeStraightShape(
            points=[(0, 15), (0, 30), (30, 30), (30, 15)], distance=30
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=[test_shape1, test_shape2],
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25 * 0.5)

    def test_intersect_volume_3_extruded_shapes(self):
        """creates three different extruded shapes using straight connections with the
        second and third shapes intersecting the first and checks that the volume is
        correct"""

        test_shape1 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=10
        )
        test_shape2 = ExtrudeStraightShape(
            points=[(10, 10), (10, 30), (30, 30), (30, 10)], distance=3
        )
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            distance=30,
            intersect=[test_shape1, test_shape2],
        )

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30 * 0.25 * 0.1)

    def test_absolute_shape_volume(self):
        """creates an extruded shape at one placement angle using straight connections
        and checks that the volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=30
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(20 * 20 * 30)

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using straight
        connections and checks that their relative volumes are correct"""

        test_shape = ExtrudeStraightShape(
            points=[(5, 0), (5, 20), (15, 20), (15, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = 0

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 1)

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(10 * 20 * 10 * 4)

    def test_extruded_shape_with_overlap_volume(self):
        """creates two overlapping extruded shapes at different placement angles using
        straight connections and checks that their volume is correct"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (10, 20), (10, 0)], distance=10
        )

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(
            (10 * 20 * 10 * 4) - (5 * 20 * 5 * 4))

    def test_cut_volume(self):
        """creates an extruded shape using straight connections with another shape cut
        out and checks that the volume is correct"""

        inner_shape = ExtrudeStraightShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], distance=30
        )

        outer_shape = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], distance=30
        )

        outer_shape_with_cut = ExtrudeStraightShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], cut=inner_shape, distance=30,
        )

        assert inner_shape.volume == pytest.approx(5 * 5 * 30)
        assert outer_shape.volume == pytest.approx(9 * 9 * 30)
        assert outer_shape_with_cut.volume == pytest.approx(
            (9 * 9 * 30) - (5 * 5 * 30), abs=0.1
        )

    def test_initial_solid_construction(self):
        """creates and extruded shape using straight connections and checks that a cadquery
        solid with a unique hash value is created when .solid is called"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=20
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """checks that the same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the shape"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """checks that a new cadquery solid with a new unique has value is construced when
        shape.solid is called after changes to the ExtrudeStraightShape have been made"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """checks that the has value of an ExtrudeCircleShape is not updated until a new
        solid has been created"""

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_conditional_solid_reconstruction_parameters(self):
        """checks that a new cadquery solid with a new unique hash value is created when the shape
        properties of 'points', 'distance', 'workplane', 'name', 'color', 'material_tag', 'stp_filename',
        'azimuth_placement_angle', or 'cut' are changed"""

        # points
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.points = [(0, 0), (10, 30), (15, 50), (25, 5), (15, 0)]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # distance
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.distance = 30
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # workplane
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20, workplane="XZ",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.workplane = "YZ"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # name
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20, name="test_name",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.name = "new_name"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # color
        test_shape = ExtrudeStraightShape(
            points=[
                (0, 0), (0, 20), (20, 20)], distance=20, color=[
                0.5, 0.5, 0.5], )
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
            material_tag="test_material",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.material_tag = "new_material"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # stp_filename
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            distance=20,
            stp_filename="test_filename.stp",
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.stp_filename = "new_filename.stp"
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # azimuth_placement_angle
        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20, azimuth_placement_angle=0,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.azimuth_placement_angle = 180
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # cut
        cut_shape = ExtrudeStraightShape(
            points=[(5, 5), (5, 15), (15, 15)], distance=5)

        test_shape = ExtrudeStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], distance=20,
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.cut = cut_shape
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
