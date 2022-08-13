from paramak import RotateStraightShape


class VacuumVessel(RotateStraightShape):
    """A cylindrical vessel volume with constant thickness.

    Arguments:
        height: height of the vessel.
        inner_radius: the inner radius of the vessel.
        thickness: thickness of the vessel
    """

    def __init__(self, height: float, inner_radius: float, thickness: float, **kwargs):
        self.height = height
        self.inner_radius = inner_radius
        self.thickness = thickness
        super().__init__(**kwargs)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("VacuumVessel.height must be a number. Not " f"{value}")
        if value <= 0:
            msg = "VacuumVessel.height must be a positive number above 0. " f"Not {value}"
            raise ValueError(msg)
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
