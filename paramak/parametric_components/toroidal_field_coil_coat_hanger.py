from paramak import ExtrudeMixedShape


class ToroidalFieldCoilCoatHanger(ExtrudeMixedShape):
    """Creates a rectangular poloidal field coil

    :param height: the vertical (Z axis) height of the coil (cm)
    :type height: float
    :param width: the horizontal (X axis) width of the coil (cm)
    :type width: float
    :param center_point: the center of the coil (X,Z) values (cm)
    :type center_point: tuple of floats

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_upper_point,
        upper_length,
        inner_mid_point,
        mid_length,
        inner_lower_point,
        lower_length,
        thickness,
        distance,
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

        self.inner_upper_point = inner_upper_point
        self.upper_length = upper_length
        self.inner_mid_point = inner_mid_point
        self.mid_length = mid_length
        self.inner_lower_point = inner_lower_point
        self.lower_length = lower_length
        self.thickness = thickness
        self.distance = distance

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        points = [
            (self.inner_lower_point),
            (
                self.inner_lower_point[0] + self.upper_length,
                self.inner_lower_point[1] + self.upper_length,
            ),
            # (),
            # (,),
        ]

        self.points = points
