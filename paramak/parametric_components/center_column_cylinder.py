
from paramak import RotateStraightShape


class CenterColumnShieldCylinder(RotateStraightShape):
    """A cylindrical center column shield volume with constant thickness.

    Arguments:
        height (float): height of the center column shield.
        inner_radius (float): the inner radius of the center column shield.
        outer_radius (float): the outer radius of the center column shield.
        stp_filename (str, optional): Defaults to
            "CenterColumnShieldCylinder.stp".
        stl_filename (str, optional): Defaults to
            "CenterColumnShieldCylinder.stl".
        material_tag (str, optional): Defaults to "center_column_shield_mat".
    """

    def __init__(
        self,
        height,
        inner_radius,
        outer_radius,
        stp_filename="CenterColumnShieldCylinder.stp",
        stl_filename="CenterColumnShieldCylinder.stl",
        material_tag="center_column_shield_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value is None:
            raise ValueError(
                "height of the CenterColumnShieldBlock cannot be None")
        self._height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        if hasattr(self, "outer_radius"):
            if value >= self.outer_radius:
                raise ValueError(
                    "inner_radius ({}) is larger than outer_radius ({})".format(
                        value, self.outer_radius))
        self._inner_radius = value

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, value):
        if hasattr(self, "inner_radius"):
            if value <= self.inner_radius:
                raise ValueError(
                    "inner_radius ({}) is larger than outer_radius ({})".format(
                        self.inner_radius, value))
        self._outer_radius = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
            2D profile of the center column shield shape."""

        points = [
            (self.inner_radius, self.height / 2),
            (self.outer_radius, self.height / 2),
            (self.outer_radius, -self.height / 2),
            (self.inner_radius, -self.height / 2),
        ]

        self.points = points
