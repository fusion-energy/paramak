from paramak import RotateStraightShape


class PoloidalFieldCoilCaseFC(RotateStraightShape):
    """Creates a casing for a reactangular poloidal field coil by building
    around an existing coil (which is passed as an argument on construction)

    :param pf_coil: a pf coil object with a set width, heigh and center point
    :type pf_coil: PoloidalFieldCoil object
    :param casing_thickness: the thickness of the coil casing (cm)
    :type casing_thickness: tuple of floats

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        pf_coil,
        casing_thickness,
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

        self.center_point = pf_coil.center_point
        self.height = pf_coil.height
        self.width = pf_coil.width
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
