
from typing import Optional
from paramak import RotateStraightShape


class CuttingWedge(RotateStraightShape):
    """Creates a wedge from height, radius and rotation angle arguments than
    can be useful for cutting sector models.

    Args:
        height: the vertical (z axis) height of the coil (cm).
        radius: the horizontal (x axis) width of the coil (cm).
        stp_filename: Defaults to "CuttingWedge.stp".
        stl_filename: Defaults to "CuttingWedge.stl".
        rotation_angle: Defaults to 180.0.
        material_tag: Defaults to "cutting_slice_mat".

    """

    def __init__(
        self,
        height: float,
        radius: float,
        stp_filename: Optional[str] = "CuttingWedge.stp",
        stl_filename: Optional[str] = "CuttingWedge.stl",
        rotation_angle: Optional[float] = 180.0,
        material_tag: Optional[str] = "cutting_slice_mat",
        **kwargs
    ) -> None:

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
