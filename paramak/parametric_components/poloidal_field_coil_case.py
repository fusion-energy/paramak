from paramak import RotateStraightShape


class PoloidalFieldCoilCase(RotateStraightShape):
    """Creates a casing for a reactangular coil from inputs that
    describe the existing coil and the thickness of the casing required

    :param height: the vertical (Z axis) height of the coil (cm)
    :type height: float
    :param width: the horizontal (X axis) width of the coil (cm)
    :type width: float
    :param center_point: the center of the coil (X,Z) values (cm)
    :type center_point: tuple of floats
    :param casing_thickness: the thickness of the coil casing (cm)
    :type casing_thickness: tuple of floats

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        casing_thickness,
        coil_height,
        coil_width,
        center_point,
        rotation_angle=360,
        stp_filename="PoloidalFieldCoilCase.stp",
        color=None,
        azimuth_placement_angle=0,
        name=None,
        material_tag="pf_coil_case_mat",
        **kwargs
    ):

        default_dict = {'points':None,
                        'workplane':"XZ",
                        'solid':None,
                        'hash_value':None,
                        'intersect':None,
                        'cut':None
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            **default_dict
        )

        self.center_point = center_point
        self.height = coil_height
        self.width = coil_width
        self.casing_thickness = casing_thickness

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, value):
        self._center_point = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil case shape."""

        points = [
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper right
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),  # lower right
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] - self.height / 2.0,
            ),  # lower left
            (
                self.center_point[0] - self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper left
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper right
            (
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - (self.casing_thickness + self.width / 2.0),
                self.center_point[1] - (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] - (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + (self.casing_thickness + self.width / 2.0),
                self.center_point[1] + (self.casing_thickness + self.height / 2.0),
            ),
            (
                self.center_point[0] + self.width / 2.0,
                self.center_point[1] + self.height / 2.0,
            ),  # upper right
        ]

        self.points = points
