from paramak import RotateMixedShape


class CenterColumnShieldCircular(RotateMixedShape):
    """A center column shield volume with a circular outer profile and constant
    cylindrical inner profile.

    :param height: height of the center column shield
    :type height: float
    :param inner_radius: inner radius of the center column shield
    :type inner_radius: float
    :param mid_radius: inner radius of the outer hyperbolic 
     profile of the center column shield
    :type mid_radius: float
    :param outer_radius: outer_radius of the center column shield
    :type outer_radius: float

    :return: a shape object that has generic functionality
    :rtype: a paramak shape
    """

    def __init__(
        self,
        height,
        inner_radius,
        mid_radius,
        outer_radius,
        workplane="XZ",
        rotation_angle=360,
        solid=None,
        stp_filename="center_column.stp",
        color=None,
        points=None,
        name="center_column",
        material_tag="center_column_material",
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
        self.mid_radius = mid_radius
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
    def mid_radius(self):
        return self._mid_radius

    @mid_radius.setter
    def mid_radius(self, mid_radius):
        self._mid_radius = mid_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius):
        self._outer_radius = outer_radius

    def find_points(self):
        """Finds the XZ points and connection types (straight and circle) that
        describe the 2D profile of the center column shield shape."""

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (self.outer_radius, self.height / 2, "circle"),
            (self.mid_radius, 0, "circle"),
            (self.outer_radius, -self.height / 2, "straight"),
            (self.inner_radius, -self.height / 2, "straight"),
            (self.inner_radius, 0, "straight"),
        ]

        self.points = points
