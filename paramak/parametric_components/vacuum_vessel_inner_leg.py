
from paramak import RotateStraightShape


class VacuumVessel(RotateStraightShape):
    """A cylindrical vessel volume with constant thickness.

    Arguments:
        height (float): height of the vessel.
        inner_radius (float): the inner radius of the vessel.
        inner_leg_radius (float): the inner radius of the inner leg.
        thickness (float): thickness of the vessel
        stp_filename (str, optional): defaults to
            "CenterColumnShieldCylinder.stp".
        stl_filename (str, optional): defaults to
            "CenterColumnShieldCylinder.stl".
        material_tag (str, optional): defaults to "center_column_shield_mat".
    """

    def __init__(
        self,
        height,
        inner_radius,
        inner_leg_radius,
        thickness,
        stp_filename="CenterColumnShieldCylinder.stp",
        stl_filename="CenterColumnShieldCylinder.stl",
        material_tag="center_column_shield_mat",
        **kwargs
    ):
        self.height = height
        self.inner_radius = inner_radius
        self.inner_leg_radius = inner_leg_radius
        self.thickness = thickness
        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError('VacuumVessel.height must be a number. Not', value)
        if value <= 0:
            raise ValueError('VacuumVessel.height must be a positive number above 0. Not', value)
        self._height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        # todo check it is a positve number
        self._inner_radius = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
            2D profile of the vessel shape."""
        thickness = self.thickness
        inner_radius = self.inner_radius
        height = self.height
        inner_leg_radius = self.inner_leg_radius


        self.points = 

    # def create_solid(self):
    #     """Creates a 3d solid using points with straight edges. Individual
    #     solids in the compound can be accessed using .Solids()[i] where i is an
    #     int

    #        Returns:
    #           A CadQuery solid: A 3D solid volume
    #     """
    #     pass