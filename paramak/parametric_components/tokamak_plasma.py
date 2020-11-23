
import numpy as np
from paramak import RotateSplineShape


class Plasma(RotateSplineShape):
    """Creates a double null tokamak plasma shape that is controlled by 4
    shaping parameters.

    Args:
        elongation (float, optional): the elongation of the plasma.
            Defaults to 2.0.
        major_radius (float, optional): the major radius of the plasma (cm).
            Defaults to 450.0.
        minor_radius (int, optional): the minor radius of the plasma (cm).
            Defaults to 150.0.
        triangularity (float, optional): the triangularity of the plasma.
            Defaults to 0.55.
        vertical_displacement (float, optional): the vertical_displacement
            of the plasma (cm). Defaults to 0.0.
        num_points (int, optional): number of points to describe the
            shape. Defaults to 50.
        configuration (str, optional): plasma configuration
            ("non-null", "single-null", "double-null").
            Defaults to "non-null".
        x_point_shift (float, optional): shift parameters for locating the
            X points in [0, 1]. Defaults to 0.1.
        name (str, optional): Defaults to "plasma".
        material_tag (str, optional): defaults to "DT_plasma".
        stp_filename (str, optional): defaults to "plasma.stp".
        stl_filename (str, optional): defaults to "plasma.stl".
    """

    def __init__(
        self,
        elongation=2.0,
        major_radius=450.0,
        minor_radius=150.0,
        triangularity=0.55,
        vertical_displacement=0.0,
        num_points=50,
        configuration="non-null",
        x_point_shift=0.1,
        name="plasma",
        material_tag="DT_plasma",
        stp_filename="plasma.stp",
        stl_filename="plasma.stl",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        # properties needed for plasma shapes
        self.elongation = elongation
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.vertical_displacement = vertical_displacement
        self.num_points = num_points
        self.configuration = configuration
        self.x_point_shift = x_point_shift

        self.outer_equatorial_point = None
        self.inner_equatorial_point = None
        self.high_point = None
        self.low_point = None

    @property
    def high_point(self):
        self.high_point = (
            self.major_radius - self.triangularity * self.minor_radius,
            self.elongation * self.minor_radius + self.vertical_displacement,
        )
        return self._high_point

    @high_point.setter
    def high_point(self, value):
        self._high_point = value

    @property
    def low_point(self):
        self.low_point = (
            self.major_radius - self.triangularity * self.minor_radius,
            -self.elongation * self.minor_radius + self.vertical_displacement,
        )
        return self._low_point

    @low_point.setter
    def low_point(self, value):
        self._low_point = value

    @property
    def outer_equatorial_point(self):
        self.outer_equatorial_point = (
            self.major_radius + self.minor_radius, self.vertical_displacement)
        return self._outer_equatorial_point

    @outer_equatorial_point.setter
    def outer_equatorial_point(self, value):
        self._outer_equatorial_point = value

    @property
    def inner_equatorial_point(self):
        self.inner_equatorial_point = (
            self.major_radius - self.minor_radius, self.vertical_displacement)
        return self._inner_equatorial_point

    @inner_equatorial_point.setter
    def inner_equatorial_point(self, value):
        self._inner_equatorial_point = value

    @property
    def lower_x_point(self):
        self.compute_x_points()
        return self._lower_x_point

    @lower_x_point.setter
    def lower_x_point(self, value):
        self._lower_x_point = value

    @property
    def upper_x_point(self):
        self.compute_x_points()
        return self._upper_x_point

    @upper_x_point.setter
    def upper_x_point(self, value):
        self._upper_x_point = value

    @property
    def vertical_displacement(self):
        return self._vertical_displacement

    @vertical_displacement.setter
    def vertical_displacement(self, value):
        self._vertical_displacement = value

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, value):
        if value < 1:
            raise ValueError("minor_radius is out of range")
        else:
            self._minor_radius = value

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, value):
        if value < 1:
            raise ValueError("major_radius is out of range")
        else:
            self._major_radius = value

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, value):
        if value > 10 or value < 0:
            raise ValueError("elongation is out of range")
        else:
            self._elongation = value

    def compute_x_points(self):
        """Computes the location of X points based on plasma parameters and
        configuration

        Returns:
            ((float, float), (float, float)): lower and upper x points
            coordinates. None if no x points
        """
        lower_x_point, upper_x_point = None, None  # non-null config
        shift = self.x_point_shift
        elongation = self.elongation
        triangularity = self.triangularity
        if self.configuration in ["single-null", "double-null"]:
            # no X points for non-null config
            lower_x_point = (1 -
                             (1 +
                              shift) *
                             triangularity *
                             self.minor_radius, -
                             (1 +
                              shift) *
                             elongation *
                             self.minor_radius +
                             self.vertical_displacement, )

            if self.configuration == "double-null":
                # upper_x_point is up-down symmetrical
                upper_x_point = (
                    lower_x_point[0],
                    (1 + shift) * elongation * self.minor_radius
                    + self.vertical_displacement,
                )
        self.lower_x_point = lower_x_point
        self.upper_x_point = upper_x_point

    def find_points(self):
        """Finds the XZ points that describe the 2D profile of the plasma."""

        # create array of angles theta
        theta = np.linspace(0, 2 * np.pi, num=self.num_points, endpoint=False)

        # parametric equations for plasma
        def R(theta):
            return self.major_radius + self.minor_radius * np.cos(
                theta + self.triangularity * np.sin(theta)
            )

        def Z(theta):
            return (
                self.elongation * self.minor_radius * np.sin(theta)
                + self.vertical_displacement
            )

        self.points = np.stack((R(theta), Z(theta)), axis=1).tolist()
