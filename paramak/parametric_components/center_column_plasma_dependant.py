from paramak import RotateMixedShape
from paramak import Plasma


class CenterColumnShieldPlasmaHyperbola(RotateMixedShape):
    """A center column shield volume with a curvature controlled by the shape of the
    plasma and offsets specified at the plasma center and edges. Shield thickness is
    controlled by the relative values of the shield offsets and inner radius.

    Args:
        major_radius (float): the major radius of the plasma.
        minor_radius (float): the minor radius of the plasma.
        triangulation (float): the triangularity of the plasma.
        elongation (float): the elongation of the plasma.
        inner_radius (float): the inner radius of the center column shield.
        mid_offset (float): the offset of the shield from the plasma at the plasma center.
        edge_offset (float): the offset of the shield from the plasma at the plasma edge.

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to use when
            exportin as html graphs or png images.
        material_tag (str): The material name to use when exporting the neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
            rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a boolean intersect with
            this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by
            the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        height,
        inner_radius,
        mid_offset,
        edge_offset,
        name=None,
        color=None,
        material_tag="center_column_shield_mat",
        stp_filename="CenterColumnShieldPlasmaHyperbola.stp",
        stl_filename="CenterColumnShieldPlasmaHyperbola.stl",
        azimuth_placement_angle=0,
        rotation_angle=360,
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        elongation=2,
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XZ",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
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
            (self.inner_radius, -1 * self.height / 2, "straight"),
            (self.inner_radius, 0, "straight"),
        ]

        self.points = points
