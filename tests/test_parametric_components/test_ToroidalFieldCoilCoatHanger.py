
import paramak
import pytest
import unittest


class test_ToroidalFieldCoilCoatHanger(unittest.TestCase):
    def test_ToroidalFieldCoilCoatHanger_creation(self):
        """creates a tf coil using the ToroidalFieldCoilCoatHanger parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_start_point=(700, 0),
            vertical_length=500,
            thickness=50,
            distance=50,
            number_of_coils=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
    
    def test_ToroidalFieldCoilCoatHanger_absolute_volume(self):
        """creates a tf coil using the ToroidalFieldCoilCoatHanger parametric
        component and checks that the volume is correct"""

        test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_start_point=(700, 0),
            vertical_length=500,
            thickness=50,
            distance=30,
            number_of_coils=1,
        )

        assert test_shape.volume == pytest.approx((400*50*30*2) + ((50*50*30/2)*2) + (50*500*30) + (((150*250*30) - (((100*250)/2)*30) - (((100*250)/2)*30))*2) + (50*1000*30))

        # test_shape.with_inner_leg = False
        # assert test_shape.volume == pytest.approx((400*50*30*2) + ((50*50*30/2)*2) + (50*500*30) + (((150*250) - ((100*250/2)*2))*30))


    # def test_ToroidalFieldCoilCoatHanger_absolute_areas(self):
    #     """creates tf coils using the ToroidalFieldCoilCoatHanger parametric
    #     component and checks that the areas of the faces are correct"""

    #     test_shape = paramak.ToroidalFieldCoilCoatHanger(
    #         horizontal_start_point=(200, 500),
    #         horizontal_length=400,
    #         vertical_start_point=(700, 0),
    #         vertical_length=500,
    #         thickness=50,
    #         distance=30,
    #         number_of_coils=1,
    #     )

        # assert test_shape.area == pytest.approx((400*50*2*2) + ((50*50/2)*2*2) + (50*500*2) + (((150*250) - ((100*250/2)*2))*2) + (400*30*4) + (500*30*2) + (50*30*2) + ((29**0.5)*30*4) + (50*(2**0.5)*30))
        # assert len(test_shape.areas) == 20
        # assert test_shape.areas.count(pytest.approx(400*50*30)) == 2
        # assert test_shape.areas.count(pytest.approx())



    def test_ToroidalFieldCoilCoatHanger_rotation_angle(self):
        """creates a tf coil with a rotation_angle < 360 and checks that the correct
        cut is performed and the volume is correct"""

        test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_start_point=(700, 0),
            vertical_length=500,
            thickness=50,
            distance=50,
            number_of_coils=8,
        )

        test_shape.rotation_angle = 360
        test_shape.workplane = "XZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5, rel=0.01)

        test_shape.rotation_angle = 360
        test_shape.workplane = "YZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5, rel=0.01)

        # this test will remain commented until workplane issue #308 is resolved
        # currently causes terminal to crash due to large number of unions
        # test_shape.rotation_angle = 360
        # test_shape.workplane = "XY"
        # test_volume = test_shape.volume
        # test_shape.rotation_angle = 180
        # assert test_shape.volume == pytest.approx(test_volume * 0.5)
