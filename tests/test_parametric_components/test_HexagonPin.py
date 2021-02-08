
import math
import unittest

import paramak
import pytest


class TestHexagonPin(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.HexagonPin(
            length_of_side=5, distance=42., center_point=(0, 0))

    def test_setting_parameters(self):
        """Checks that the default parameters and user parameters are set"""

        assert self.test_shape.length_of_side == 5
        assert self.test_shape.distance == 42.
        assert self.test_shape.center_point == (0, 0)
        assert self.test_shape.stp_filename == "HexagonPin.stp"
        assert self.test_shape.stl_filename == "HexagonPin.stl"
        assert self.test_shape.name == "hexagon_pin"
        assert self.test_shape.material_tag == "hexagon_pin_mat"

    def test_volume(self):
        """Checks the volume against the actual value"""

        length = self.test_shape.length_of_side
        distance = self.test_shape.distance

        hexagon_face_area = (3 * math.sqrt(3) / 2) * math.pow(length, 2)
        # this needs a pytest.approx() as the volumes are not exact
        assert pytest.approx(self.test_shape.volume,
                             rel=0.1) == hexagon_face_area * distance

    def test_distance_impacts_volume(self):
        """Checks that changing the distance argument results in the
        expected volume change"""

        test_shape_volume = self.test_shape.volume

        self.test_shape.distance = self.test_shape.distance * 2

        assert pytest.approx(test_shape_volume * 2,
                             rel=0.1) == self.test_shape.volume

    def test_length_of_sides_impacts_volume(self):
        """Checks that changing the length_of_sides argument results in a the
        expected volume change"""

        test_shape_volume = self.test_shape.volume

        self.test_shape.length_of_side = self.test_shape.length_of_side * 2

        assert pytest.approx(test_shape_volume * 4,
                             rel=0.1) == self.test_shape.volume

    def test_areas_are_correct(self):
        """Tests the areas of the faces are the correct sizes"""

        test_shape_areas = self.test_shape.areas

        length = self.test_shape.length_of_side
        distance = self.test_shape.distance

        hexagon_face_area = (3 * math.sqrt(3) / 2) * math.pow(length, 2)

        assert len(test_shape_areas) == 8
        assert test_shape_areas.count(pytest.approx(hexagon_face_area,
                                                    rel=0.1)) == 2
        assert test_shape_areas.count(pytest.approx(length * distance,
                                                    rel=0.1)) == 6
