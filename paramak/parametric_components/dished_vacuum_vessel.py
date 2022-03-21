from typing import Tuple

from paramak import RotateMixedShape
from paramak import (
    find_center_point_of_circle,
    rotate,
    distance_between_two_points,
    angle_between_two_points_on_circle,
    find_radius_of_circle,
)


class DishedVacuumVessel(RotateMixedShape):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange.

    Arguments:
        dish_height: the height of the dish section. This is also the chord
            heigh of the circle used to make the dish.
        cylinder_height: the height of the cylindrical section of the vacuum
            vessel.
        center_point: the x,z coordinates of the center of the vessel
        radius: the radius from which the centres of the vessel meets the outer
            circumference.
        thickness: the radial thickness of the vessel in cm.
    """

    def __init__(
        self,
        radius: float,
        center_point: Tuple[float, float],
        dish_height: float,
        cylinder_height: float,
        thickness: float,
        **kwargs,
    ):
        self.radius = radius
        self.thickness = thickness
        self.center_point = center_point
        self.dish_height = dish_height
        self.cylinder_height = cylinder_height

        super().__init__(**kwargs)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("VacuumVessel.radius must be a number. Not", value)
        if value <= 0:
            msg = "VacuumVessel.radius must be a positive number above 0. " f"Not {value}"
            raise ValueError(msg)
        self._radius = value

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        if not isinstance(value, (float, int)):
            msg = f"VacuumVessel.thickness must be a number. Not {value}"
            raise ValueError(msg)
        if value <= 0:
            msg = f"VacuumVessel.thickness must be a positive number above 0. Not {value}"
            raise ValueError(msg)
        self._thickness = value

    def find_points(self):
        """
        Finds the XZ points joined by straight and circle connections that
        describe the 2D profile of the vessel shape.
        """
        #          Top of dished vv
        #          6   -
        #                  -
        #          7  -       4
        #                8       -
        #                  -       3
        #                    -     |
        #                     9 -- 2
        #                     |    |
        #                     |    |
        #          c,p        |    |
        #                     |    |
        #                     |    |
        #                    10    1
        #                    -     |
        #                  -      15
        #                11       -
        #          12  -       14
        #                  -
        #          13   -
        #          Bottom of dished vv
        #
