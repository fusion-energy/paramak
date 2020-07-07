import numpy as np
import math
from paramak import ExtrudeMixedShape


class InnerTfCoilsCircular(ExtrudeMixedShape):
    """A tf coil volume with cylindrical inner and outer profiles and
    constant gaps between each coil.

    :param height: height of tf coils
    :type height: float
    :param inner_radius: inner radius of tf coils
    :type inner_radius: float
    :param outer_radius: outer radius of tf coils
    :type outer_radius: float
    :param number_of_coils: number of tf coils
    :type number_of_coils: int
    :param gap_size: gap between adjacent tf coils
    :type gap_size: float
    """

    def __init__(
        self,
        height,
        inner_radius,
        outer_radius,
        number_of_coils,
        gap_size,
        points=None,
        distance=None,
        workplane="XY",
        stp_filename=None,
        solid=None,
        color=None,
        azimuth_placement_angle=0,
        cut=None,
        material_tag=None,
        name=None,
        hash_value=None,
    ):

        super().__init__(
            points,
            distance,
            workplane,
            stp_filename,
            solid,
            color,
            azimuth_placement_angle,
            cut,
            material_tag,
            name,
            hash_value,
        )

        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.number_of_coils = number_of_coils
        self.gap_size = gap_size
        self.distance = height

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
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, distance):
        self._distance = distance

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, azimuth_placement_angle):
        self._azimuth_placement_angle = azimuth_placement_angle

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

    @property
    def number_of_coils(self):
        return self._number_of_coils

    @number_of_coils.setter
    def number_of_coils(self, number_of_coils):
        self._number_of_coils = number_of_coils

    @property
    def gap_size(self):
        return self._gap_size

    @gap_size.setter
    def gap_size(self, gap_size):
        self._gap_size = gap_size

    def find_points(self):
        """Finds the points that describe the 2D profile of the tf coil shape"""

        theta_inner = (
            (2 * math.pi * self.inner_radius) - (self.gap_size * self.number_of_coils)
        ) / (self.inner_radius * self.number_of_coils)
        omega_inner = math.asin(self.gap_size / (2 * self.inner_radius))

        theta_outer = (
            (2 * math.pi * self.outer_radius) - (self.gap_size * self.number_of_coils)
        ) / (self.outer_radius * self.number_of_coils)
        omega_outer = math.asin(self.gap_size / (2 * self.outer_radius))

        # inner points
        point_1 = (
            (self.inner_radius * math.cos(-omega_inner)),
            (-self.inner_radius * math.sin(-omega_inner)),
        )
        point_2 = (
            (
                self.inner_radius * math.cos(theta_inner / 2) * math.cos(-omega_inner)
                + self.inner_radius * math.sin(theta_inner / 2) * math.sin(-omega_inner)
            ),
            (
                -self.inner_radius * math.cos(theta_inner / 2) * math.sin(-omega_inner)
                + self.inner_radius * math.sin(theta_inner / 2) * math.cos(-omega_inner)
            ),
        )
        point_3 = (
            (
                self.inner_radius * math.cos(theta_inner) * math.cos(-omega_inner)
                + self.inner_radius * math.sin(theta_inner) * math.sin(-omega_inner)
            ),
            (
                -self.inner_radius * math.cos(theta_inner) * math.sin(-omega_inner)
                + self.inner_radius * math.sin(theta_inner) * math.cos(-omega_inner)
            ),
        )

        # outer points
        point_4 = (
            (self.outer_radius * math.cos(-omega_outer)),
            (-self.outer_radius * math.sin(-omega_outer)),
        )
        point_5 = (
            (
                self.outer_radius * math.cos(theta_outer / 2) * math.cos(-omega_outer)
                + self.outer_radius * math.sin(theta_outer / 2) * math.sin(-omega_outer)
            ),
            (
                -self.outer_radius * math.cos(theta_outer / 2) * math.sin(-omega_outer)
                + self.outer_radius * math.sin(theta_outer / 2) * math.cos(-omega_outer)
            ),
        )
        point_6 = (
            (
                self.outer_radius * math.cos(theta_outer) * math.cos(-omega_outer)
                + self.outer_radius * math.sin(theta_outer) * math.sin(-omega_outer)
            ),
            (
                -self.outer_radius * math.cos(theta_outer) * math.sin(-omega_outer)
                + self.outer_radius * math.sin(theta_outer) * math.cos(-omega_outer)
            ),
        )

        points = [
            (point_1[0], point_1[1], "circle"),
            (point_2[0], point_2[1], "circle"),
            (point_3[0], point_3[1], "straight"),
            (point_6[0], point_6[1], "circle"),
            (point_5[0], point_5[1], "circle"),
            (point_4[0], point_4[1], "straight"),
            (point_1[0], point_1[1], "straight"),
        ]  # we have overwritten the setter which automatically adds the endpoint=first point, so we need to specify it explicitely

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf coils"""

        angles = np.linspace(0, 360, self.number_of_coils, endpoint=False)

        self.azimuth_placement_angle = angles
