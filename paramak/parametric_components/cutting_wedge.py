from paramak import RotateStraightShape


class CuttingWedge(RotateStraightShape):
    """Creates a wedge from height, radius and rotation angle arguments than
    can be useful for cutting sector models.

    Args:
        height: the vertical (z axis) height of the coil (cm).
        radius: the horizontal (x axis) width of the coil (cm).
        rotation_angle: Defaults to 180.0.
    """

    def __init__(self, height: float, radius: float, rotation_angle: float = 180.0, **kwargs) -> None:

        super().__init__(rotation_angle=rotation_angle, **kwargs)

        self.height = height
        self.radius = radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: float):
        self._height = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    def find_points(self):

        points = [
            (0, self.height / 2),
            (self.radius, self.height / 2),
            (self.radius, -self.height / 2),
            (0, -self.height / 2),
        ]

        self.points = points
