from paramak import RotateMixedShape
from paramak import Plasma


class CenterColumnShieldPlasmaHyperbola(RotateMixedShape):
    """A center column shield volume with a curvature controlled by the shape of the
    plasma and offsets specified at the plasma center and edges. Shield thickness is
    controlled by the relative values of the shield offsets and inner radius.

    :param major_radius: the major radius of the plasma
    :type major_radius: float
    :param minor_radius: the minor radius of the plasma
    :type minor_radius: float
    :param triangularity: the triangularity of the plasma
    :type triangularity: float
    :param elongation: the elongation of the plasma
    :type elongation: float
    :param inner_radius: the inner radius of the center column shield
    :type inner_radius: float
    :param mid_offset: the offset of the shield from the plasma at the plasma center
    :type mid_offset: float
    :param edge_offset: the offset of the shield from the plasma at the plasma edge
    :type edge_offset: float

    :return: a shape object that has generic functionality
    :rtype: a paramak shape
    """

    def __init__(
        self,
        points=None,
        name=None,
        color=None,
        material_tag=None,
        stp_filename=None,
        workplane="XZ",
        azimuth_placement_angle=0,
        solid=None,
        rotation_angle=360,
        cut=None,
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        elongation=2,
        height=None,
        inner_radius=None,
        mid_offset=None,
        edge_offset=None,
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

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.elongation = elongation
        self.stp_filename = stp_filename
        self.height = height
        self.inner_radius = inner_radius
        self.mid_offset = mid_offset
        self.edge_offset = edge_offset

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, value):
        self._major_radius = value

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, value):
        self._minor_radius = value

    @property
    def triangularity(self):
        return self._triangularity

    @triangularity.setter
    def triangularity(self, value):
        self._triangularity = value

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, value):
        self._elongation = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        self._inner_radius = value

    @property
    def mid_offset(self):
        return self._mid_offset

    @mid_offset.setter
    def mid_offset(self, value):
        self._mid_offset = value

    @property
    def edge_offset(self):
        return self._edge_offset

    @edge_offset.setter
    def edge_offset(self, value):
        self._edge_offset = value

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the center column shield shape."""

        plasma = Plasma()

        plasma.major_radius = self.major_radius
        plasma.minor_radius = self.minor_radius
        plasma.triangularity = self.triangularity
        plasma.elongation = self.elongation
        plasma.rotation_angle = self.rotation_angle
        plasma.find_points()

        mid_x_point = (
            plasma.x_position_for_inside_arc - plasma.radius_of_inside_arc
        ) - self.mid_offset
        mid_z_point = 0

        top_x_point = plasma.x_point - self.edge_offset
        top_z_point = max(plasma.zs_inner_arc)

        bottom_x_point = plasma.x_point - self.edge_offset
        bottom_z_point = min(plasma.zs_inner_arc)

        if self.height <= abs(top_z_point) + abs(bottom_z_point):
            raise ValueError(
                "Center column height ({}) is smaller than plasma height ({})".format(
                    self.height, abs(top_z_point) + abs(bottom_z_point)
                )
            )

        if self.inner_radius >= mid_x_point:
            raise ValueError("Inner radius is too large")

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (top_x_point, self.height / 2, "straight"),
            (top_x_point, top_z_point, "spline"),
            (mid_x_point, mid_z_point, "spline"),
            (bottom_x_point, bottom_z_point, "straight"),
            (bottom_x_point, -1 * self.height / 2, "straight"),
            (self.inner_radius, -1 * self.height / 2, "straight"),
            (self.inner_radius, 0, "straight"),
        ]

        self.points = points
