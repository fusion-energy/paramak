from paramak import RotateStraightShape


class CenterColumnShieldCylinder(RotateStraightShape):
    """A cylindrical center column shield volume with constant thickness.

    :param height: height of the center column shield
    :type height: float
    :param inner_radius: the inner radius of the center column shield
    :type inner_radius: float
    :param outer_radius: the outer radius of the center column shield
    :type outer_radius: float

    :return: a shape object that has generic functionality
    :rtype: a paramak shape object
    """

    def __init__(
        self,
        height,
        inner_radius,
        outer_radius,
        points=None,
        name=None,
        color=None,
        workplane="XZ",
        stp_filename="center_column_shield.stp",
        rotation_angle=360,
        solid=None,
        material_tag=None,
        azimuth_placement_angle=0,
        cut=None,
        hash_value=None,
    ):

        super().__init__(
            points,
            workplane,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            solid,
            rotation_angle,
            cut,
            hash_value,
        )

        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius):
        self._inner_radius = inner_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius):
        self._outer_radius = outer_radius

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the center column shield shape."""

        if self.inner_radius >= self.outer_radius:
            raise ValueError(
                "inner_radius ({}) is larger than outer_radius ({})".format(
                    self.inner_radius, self.outer_radius
                )
            )

        if self.height is None:
            raise ValueError("height of the CenterColumnShieldBlock must be set")

        points = [
            (self.inner_radius, self.height / 2),
            (self.outer_radius, self.height / 2),
            (self.outer_radius, -self.height / 2),
            (self.inner_radius, -self.height / 2),
            (self.inner_radius, self.height / 2),
        ]

        self.points = points
