
import unittest
import paramak


class test_attribute_propagation_to_solid(unittest.TestCase):
    def test_InnerTfCoilsCircular_attributes(self):
        """checks that changing the attributes of InnerTfCoilsCircular affects
        the cadquery solid produced"""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )
        test_shape_volume = test_shape.volume

        test_shape.height = 1000
        assert test_shape_volume == test_shape.volume * 0.5
        test_shape.height = 500
        test_shape.inner_radius = 30
        assert test_shape_volume < test_shape.volume
        test_shape.inner_radius = 50
        test_shape.outer_radius = 170
        assert test_shape_volume < test_shape.volume

    def test_InnerTfCoilsCircular_gap_size(self):
        """checks that a ValueError is raised when a too large gap_size is used"""

        def test_InnerTfCoilsCircular_incorrect_gap_size():
            paramak.InnerTfCoilsCircular(
                height=100,
                inner_radius=20,
                outer_radius=40,
                number_of_coils=8,
                gap_size=20
            ).solid

        self.assertRaises(
            ValueError,
            test_InnerTfCoilsCircular_incorrect_gap_size
        )

    def test_InnerTfCoilsFlat_attributes(self):
        """checks that changing the attributes of InnerTfCoilsFlat affects the
        cadquery solid produced"""

        test_shape = paramak.InnerTfCoilsFlat(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )
        test_shape_volume = test_shape.volume

        test_shape.height = 1000
        assert test_shape_volume == test_shape.volume * 0.5
        test_shape.height = 500
        test_shape.inner_radius = 30
        assert test_shape_volume < test_shape.volume
        test_shape.inner_radius = 50
        test_shape.outer_radius = 170
        assert test_shape_volume < test_shape.volume

    def test_InnerTfCoilsFlat_gap_size(self):
        """checks that a ValueError is raised when a too large gap_size is used"""

        def test_InnerTfCoilsFlat_incorrect_gap_size():
            paramak.InnerTfCoilsFlat(
                height=100,
                inner_radius=20,
                outer_radius=40,
                number_of_coils=8,
                gap_size=20
            ).solid

        self.assertRaises(
            ValueError,
            test_InnerTfCoilsFlat_incorrect_gap_size
        )


class test_ParametricComponents(unittest.TestCase):
    def test_parametric_component_hash_value(self):
        """creates a parametric component and checks that a cadquery solid with
        a unique hash value is created when .solid is called. checks that the
        same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the
        parametric component. checks that a new cadquery solid with a new
        unique hash value is constructed when shape.solid is called after
        changes to the parametric component have been made. checks that the
        hash_value of a parametric component is not updated until a new
        cadquery solid has been created"""

        test_shape = paramak.CenterColumnShieldCylinder(
            height=100,
            inner_radius=20,
            outer_radius=40
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value
        assert test_shape.solid is not None
        assert initial_hash_value == test_shape.hash_value
        test_shape.height = 120
        assert initial_hash_value == test_shape.hash_value
        assert test_shape.solid is not None
        assert initial_hash_value != test_shape.hash_value


if __name__ == "__main__":
    unittest.main()
