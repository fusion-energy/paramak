from cadquery import Compound
from paramak import RotateMixedShape, CenterColumnShieldCylinder, ConstantThicknessDome


class DishedVacuumVessel(RotateMixedShape):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange.

    Arguments:
        radius: the radius from which the centres of the vessel meets the outer
            circumference.
        center_point: the x,z coordinates of the center of the vessel
        dish_height: the height of the dish section. This is also the chord
            heigh of the circle used to make the dish.
        cylinder_height: the height of the cylindrical section of the vacuum
            vessel.
        thickness: the radial thickness of the vessel in cm.
    """

    def __init__(
        self,
        radius: float = 300,
        center_point: float = 0,
        dish_height: float = 50,
        cylinder_height: float = 400,
        thickness: float = 15,
        name: str = "dished_vessel",
        **kwargs,
    ):
        self.radius = radius
        self.center_point = center_point
        self.dish_height = dish_height
        self.cylinder_height = cylinder_height
        self.thickness = thickness
        self.name = name

        super().__init__(name=name, **kwargs)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value: float):
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
    def thickness(self, value: float):
        if not isinstance(value, (float, int)):
            msg = f"VacuumVessel.thickness must be a number. Not {value}"
            raise ValueError(msg)
        if value <= 0:
            msg = f"VacuumVessel.thickness must be a positive number above 0. Not {value}"
            raise ValueError(msg)
        self._thickness = value

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        #
        #          -   -
        #                  -
        #          -  -       -
        #                -       -
        #                  -       -
        #                    -     |
        #                     |    |
        #                     |    |
        #                     |    |
        #          c,p        |    |
        #                     |    |
        #                     |    |
        #                     |    |
        #                    -     |
        #                  -      -
        #                -       -
        #          -  -       -
        #                  -
        #          -   -
        #

        cylinder_section = CenterColumnShieldCylinder(
            height=self.cylinder_height,
            inner_radius=self.radius - self.thickness,
            outer_radius=self.radius,
            center_height=self.center_point,
            rotation_angle=self.rotation_angle,
        )

        upper_dome_section = ConstantThicknessDome(
            thickness=self.thickness,
            chord_center_height=self.center_point + 0.5 * self.cylinder_height,
            chord_width=(self.radius - self.thickness) * 2,
            chord_height=self.dish_height,
            upper_or_lower="upper",
            rotation_angle=self.rotation_angle,
        )

        lower_dome_section = ConstantThicknessDome(
            thickness=self.thickness,
            chord_center_height=self.center_point - 0.5 * self.cylinder_height,
            chord_width=(self.radius - self.thickness) * 2,
            chord_height=self.dish_height,
            upper_or_lower="lower",
            rotation_angle=self.rotation_angle,
        )

        shapes = [lower_dome_section.solid.val(), upper_dome_section.solid.val(), cylinder_section.solid.val()]
        self.solid = Compound.makeCompound(shapes)
