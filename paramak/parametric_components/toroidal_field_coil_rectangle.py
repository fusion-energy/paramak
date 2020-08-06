from paramak import ExtrudeStraightShape
import numpy as np


class ToroidalFieldCoilRectangle(ExtrudeStraightShape):
    """Creates a rectangular shaped toroidal field coil

    :param inner_upper_point: the (x,z) coordinates of the inner
     upper point (cm)
    :type inner_upper_point: tuple of two float
    :param inner_mid_point: the (x,z) coordinates of the inner
     mid point (cm)
    :type inner_mid_point: tuple of two float
    :param inner_lower_point: the (x,z) coordinates of the inner
     lower point (cm)
    :type inner_lower_point: tuple of two float
    :param thickness: the thickness of the toroidal field coil
    :type thickness: float
    :param distance: the extrusion distance
    :type distance: float
    :param number_of_coils: the number of tf coils, this changes the
     azimuth_placement_angle dividing up 360 degrees by the number of coils 
    :type distance: int

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_upper_point,
        inner_mid_point,
        inner_lower_point,
        thickness,
        distance,
        number_of_coils,
        rotation_angle=360,
        stp_filename="ToroidalFieldCoilRectangle.stp",
        stl_filename="ToroidalFieldCoilRectangle.stl",
        color=None,
        azimuth_placement_angle=0,
        name=None,
        material_tag="outer_tf_coil_mat",
        **kwargs
    ):

        default_dict = {'points':None,
                        'workplane':"XZ",
                        'solid':None,
                        'hash_value':None,
                        'intersect':None,
                        'cut':None,
                        'union':None,
                        'tet_mesh':None,
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
            **default_dict
        )

        self.inner_upper_point = inner_upper_point
        self.inner_mid_point = inner_mid_point
        self.inner_lower_point = inner_lower_point
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
            (self.inner_upper_point),
            (self.inner_mid_point[0], self.inner_upper_point[1]),
            # (self.inner_mid_point),
            (self.inner_mid_point[0], self.inner_lower_point[1]),
            (self.inner_lower_point),
            (self.inner_lower_point[0], self.inner_lower_point[1] - self.thickness),
            (
                self.inner_mid_point[0] + self.thickness,
                self.inner_lower_point[1] - self.thickness,
            ),
            (self.inner_mid_point[0] + self.thickness, self.inner_mid_point[1]),
            (
                self.inner_mid_point[0] + self.thickness,
                self.inner_upper_point[1] + self.thickness,
            ),
            (self.inner_upper_point[0], self.inner_upper_point[1] + self.thickness),
        ]

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf coils"""

        angles = np.linspace(0, 360, self.number_of_coils, endpoint=False)

        self.azimuth_placement_angle = angles
