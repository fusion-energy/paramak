
from paramak import RotateStraightShape


class VacuumVessel(RotateStraightShape):
    """A cylindrical vessel volume with constant thickness.

    Arguments:
        height (float): height of the vessel.
        inner_radius (float): the inner radius of the vessel.
        thickness (float): thickness of the vessel
        stp_filename (str, optional): defaults to "VacuumVessel.stp".
        stl_filename (str, optional): defaults to "VacuumVessel.stl".
        material_tag (str, optional): defaults to "vacuum_vessel_mat".
    """

    def __init__(
        self,
        height,
        inner_radius,
        thickness,
        stp_filename="VacuumVessel.stp",
        stl_filename="VacuumVessel.stl",
        material_tag="vacuum_vessel_mat",
        **kwargs
    ):
        self.height = height
        self.inner_radius = inner_radius
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
            raise ValueError(
                'VacuumVessel.height must be a number. Not', value)
        if value <= 0:
            raise ValueError(
                'VacuumVessel.height must be a positive number above 0. Not', value)
        self._height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        assert value > 0
        self._inner_radius = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
            2D profile of the vessel shape."""
        thickness = self.thickness
        inner_radius = self.inner_radius
        height = self.height

        inner_points = [
            (0, height / 2),
            (inner_radius, height / 2),
            (inner_radius, -height / 2),
            (0, -height / 2),
        ]

        outer_points = [
            (0, height / 2 + thickness),
            (inner_radius + thickness, height / 2 + thickness),
            (inner_radius + thickness, -(height / 2 + thickness)),
            (0, -(height / 2 + thickness)),
        ]
        self.points = inner_points + outer_points[::-1]
