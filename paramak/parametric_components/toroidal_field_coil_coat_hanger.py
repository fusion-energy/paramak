from paramak import ExtrudeStraightShape

import numpy as np


class ToroidalFieldCoilCoatHanger(ExtrudeStraightShape):
    """Creates a coat hanger shaped toroidal field coil.

    Args:
        horizontal_start_point (tuple of 2 floats): the (x,z) coordinates of the
            inner upper point (cm).
        horizontal_length (tuple of 2 floats): the radial length of the horizontal
            section of the TF coil (cm).
        vertical_mid_point (tuple of 2 points): the (x,z) coordinates of the mid point
            of the vertical section (cm).
        vertical_length (tuple of 2 floats): the radial length of the vertical section
            of the TF coil (cm).
        thickness (float): the thickness of the toroidal field coil.
        distance (float): the extrusion distance.
        number_of_coils (int): the number of tf coils. This changes with azimuth_placement_angle
            dividing up 360 degrees by the number of coils.

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
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        horizontal_start_point,
        horizontal_length,
        vertical_start_point,
        vertical_length,
        thickness,
        distance,
        number_of_coils,
        rotation_angle=360,
        stp_filename="ToroidalFieldCoilCoatHangar.stp",
        stl_filename="ToroidalFieldCoilCoatHangar.stl",
        color=None,
        azimuth_placement_angle=0,
        name=None,
        material_tag="outer_tf_coil_mat",
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
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            azimuth_placement_angle=azimuth_placement_angle,
            material_tag=material_tag,
            name=name,
            hash_value=None,
            **default_dict
        )

        self.horizontal_start_point = horizontal_start_point
        self.horizontal_length = horizontal_length
        self.vertical_start_point = vertical_start_point
        self.vertical_length = vertical_length
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, azimuth_placement_angle):
        self._azimuth_placement_angle = azimuth_placement_angle

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        points = [
            self.horizontal_start_point,  # upper right inner
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1],
            ),
            (
                self.vertical_start_point[0],
                self.vertical_start_point[1] + 0.5 * self.vertical_length,
            ),  # upper inner horizontal section
            (
                self.vertical_start_point[0],
                self.vertical_start_point[1] - 0.5 * self.vertical_length,
            ),  # lower inner horizontal section
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1],
            ),  # lower left vertical section
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1],
            ),  # lower right vertical section
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1] - self.thickness,
            ),
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1] - self.thickness,
            ),
            (
                self.horizontal_start_point[0]
                + self.horizontal_length
                + self.thickness,
                -self.horizontal_start_point[1],
            ),  # lower left vertical section
            (
                self.vertical_start_point[0] + self.thickness,
                self.vertical_start_point[1] - 0.5 * self.vertical_length,
            ),  # lower inner horizontal section
            (
                self.vertical_start_point[0] + self.thickness,
                self.vertical_start_point[1] + 0.5 * self.vertical_length,
            ),  # upper inner horizontal section
            (
                self.horizontal_start_point[0]
                + self.horizontal_length
                + self.thickness,
                self.horizontal_start_point[1],
            ),
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1] + self.thickness,
            ),
            (
                self.horizontal_start_point[0],
                self.horizontal_start_point[1] + self.thickness,
            ),  # upper right inner
        ]

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf coils"""

        angles = np.linspace(0, 360, self.number_of_coils, endpoint=False)

        self.azimuth_placement_angle = angles
