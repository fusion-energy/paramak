from paramak import ExtrudeStraightShape

import numpy as np


class ToroidalFieldCoilCoatHanger(ExtrudeStraightShape):
    """Creates a coat hanger shaped toroidal field coil

    :param horizontal_start_point: the (x,z) coordinates of the inner
     upper point (cm)
    :type horizontal_start_point: tuple of two floats
    :param horizontal_length: the radial length of the horizontal
     section of the TF coil (cm)
    :type horizontal_length: tuple of two floats
    :param vertical_mid_point: the (x,z) coordinates of the mid point
     of the vertical section (cm)
    :type vertical_mid_point: tuple of two floats
    :param vertical_length: the (x,z) coordinates of the inner
     lower point (cm)
    :type vertical_length: tuple of two floats
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
        horizontal_start_point,
        horizontal_length,
        vertical_start_point,
        vertical_length,
        thickness,
        distance,
        number_of_coils,
        workplane="XZ",
        rotation_angle=360,
        solid=None,
        stp_filename="toroidal_field_coil.stp",
        color=None,
        azimuth_placement_angle=0,
        points=None,
        name=None,
        material_tag=None,
        cut=None,
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

        points = [self.horizontal_start_point,# upper right inner
                  (self.horizontal_start_point[0]+self.horizontal_length, self.horizontal_start_point[1]), 
                  (self.vertical_start_point[0],self.vertical_start_point[1]+0.5*self.vertical_length),# upper inner horizontal section 
                  (self.vertical_start_point[0],self.vertical_start_point[1]-0.5*self.vertical_length), # lower inner horizontal section
                  (self.horizontal_start_point[0]+self.horizontal_length, -self.horizontal_start_point[1]),# lower left vertical section
                  (self.horizontal_start_point[0], -self.horizontal_start_point[1]),# lower right vertical section

                  (self.horizontal_start_point[0], -self.horizontal_start_point[1]-self.thickness),
                  (self.horizontal_start_point[0]+self.horizontal_length, -self.horizontal_start_point[1]-self.thickness),
                  (self.horizontal_start_point[0]+self.horizontal_length+self.thickness, -self.horizontal_start_point[1]),# lower left vertical section
                  (self.vertical_start_point[0]+self.thickness,self.vertical_start_point[1]-0.5*self.vertical_length), # lower inner horizontal section
                  (self.vertical_start_point[0]+self.thickness,self.vertical_start_point[1]+0.5*self.vertical_length),# upper inner horizontal section 
                  (self.horizontal_start_point[0]+self.horizontal_length+ self.thickness, self.horizontal_start_point[1]), 
                  (self.horizontal_start_point[0]+self.horizontal_length, self.horizontal_start_point[1]+self.thickness), 
                  (self.horizontal_start_point[0], self.horizontal_start_point[1] + self.thickness)# upper right inner
        ]

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf coils"""

        angles = np.linspace(0, 360, self.number_of_coils, endpoint=False)

        self.azimuth_placement_angle = angles
