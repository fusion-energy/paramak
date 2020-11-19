
from paramak import RotateStraightShape


class CuttingWedge(RotateStraightShape):
    """Creates a wedge from height, radius and rotation angle arguments than
    can be useful for cutting sector models.

    Args:
        height (float): the vertical (z axis) height of the coil (cm).
        radius (float): the horizontal (x axis) width of the coil (cm).
        stp_filename (str, optional): Defaults to "CuttingWedge.stp".
        stl_filename (str, optional): Defaults to "CuttingWedge.stl".
        rotation_angle (float, optional): Defaults to 180.0.
        material_tag (str, optional): Defaults to "cutting_slice_mat".

    """

    def __init__(
        self,
        height,
        radius,
        stp_filename="CuttingWedge.stp",
        stl_filename="CuttingWedge.stl",
        rotation_angle=180.0,
        material_tag="cutting_slice_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            rotation_angle=rotation_angle,
            **kwargs
        )

        self.height = height
        self.radius = radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    def find_points(self):

        points = [
            (0, self.height / 2),
            (self.radius, self.height / 2),
            (self.radius, -self.height / 2),
            (0, -self.height / 2)
        ]

        self.points = points
