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
        workplane="XZ",
        rotation_angle=360,
        solid=None,
        stp_filename="poloidal_field_coil_case.stp",
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
