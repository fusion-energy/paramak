
from typing import Optional
from paramak import Plasma, RotateMixedShape


class CenterColumnShieldPlasmaHyperbola(RotateMixedShape):
    """A center column shield volume with a curvature controlled by the shape
    of the plasma and offsets specified at the plasma center and edges. Shield
    thickness is controlled by the relative values of the shield offsets and
    inner radius.

    Args:
        height: height of the center column shield.
        inner_radius: the inner radius of the center column shield.
        mid_offset: the offset of the shield from the plasma at the plasma
            center.
        edge_offset: the offset of the shield from the plasma at the plasma
            edge.
        major_radius: the major radius of the plasma. Defaults to 450.0.
        minor_radius: the minor radius of the plasma. Defaults to 150.0.
        triangularity: the triangularity of the plasma. Defaults to 0.55.
        elongation: the elongation of the plasma. Defaults to 2.0.
        material_tag: Defaults to "center_column_shield_mat".
        stp_filename: Defaults to "CenterColumnShieldPlasmaHyperbola.stp".
        stl_filename: Defaults to "CenterColumnShieldPlasmaHyperbola.stl".
    """

    def __init__(
        self,
        height: float,
        inner_radius: float,
        mid_offset: float,
        edge_offset: float,
        major_radius: Optional[float] = 450.0,
        minor_radius: Optional[float] = 150.0,
        triangularity: Optional[float] = 0.55,
        elongation: Optional[float] = 2.0,
        material_tag: Optional[str] = "center_column_shield_mat",
        stp_filename: Optional[str] = "CenterColumnShieldPlasmaHyperbola.stp",
        stl_filename: Optional[str] = "CenterColumnShieldPlasmaHyperbola.stl",
        **kwargs
    ) -> None:

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
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

        if self.height <= abs(plasma.high_point[1]) + abs(plasma.low_point[1]):
            raise ValueError(
                "Center column height ({}) is smaller than plasma height ({})".format(
                    self.height, abs(plasma.high_point[1]) + abs(plasma.low_point[1])
                )
            )

        if self.inner_radius >= plasma.inner_equatorial_point[0] - \
                self.mid_offset:
            raise ValueError("Inner radius is too large")

        points = [
            (self.inner_radius, 0, "straight"),
            (self.inner_radius, self.height / 2, "straight"),
            (plasma.high_point[0] - self.edge_offset, self.height / 2, "straight"),
            (plasma.high_point[0] - self.edge_offset, plasma.high_point[1], "spline"),
            (
                plasma.inner_equatorial_point[0] - self.mid_offset,
                plasma.inner_equatorial_point[1],
                "spline",
            ),
            (plasma.low_point[0] - self.edge_offset, plasma.low_point[1], "straight"),
            (plasma.low_point[0] - self.edge_offset, -1 * self.height / 2, "straight"),
            (self.inner_radius, -1 * self.height / 2, "straight")
        ]

        self.points = points
