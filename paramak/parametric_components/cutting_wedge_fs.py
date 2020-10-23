from paramak import RotateStraightShape

from collections import Iterable


class CuttingWedgeFS(RotateStraightShape):
    """Creates a wedge from a Shape that can be useful for cutting sector
    models.

    Args:
        shape (paramak.Shape): a paramak.Shape object that is used to find the
            height and radius of the wedge
        stp_filename (str, optional): Defaults to "CuttingWedgeFS.stp".
        stl_filename (str, optional): Defaults to "CuttingWedgeFS.stl".
        rotation_angle (float, optional): Defaults to 180.0.
        material_tag (str, optional): Defaults to "cutting_slice_mat".
    """

    def __init__(
        self,
        shape,
        stp_filename="CuttingWedgeAlternate.stp",
        stl_filename="CuttingWedgeAlternate.stl",
        material_tag="cutting_slice_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.shape = shape

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    def find_points(self):

        if self.shape.rotation_angle == 360:
            raise ValueError(
                'cutting_wedge cannot be created, rotation_angle must be < 360')

        else:

            max_x = 0
            max_y = 0

            if hasattr(self.shape, 'radius') and len(self.shape.points) == 1:
                max_x = self.shape.points[0][0] + self.shape.radius
                max_y = self.shape.points[0][1] + self.shape.radius

            elif len(self.shape.points) > 1:
                for point in self.shape.points:
                    if point[0] > max_x:
                        max_x = point[0]
                    if point[1] > max_y:
                        max_y = point[1]

            else:
                raise ValueError('cutting_wedge cannot be created')

            points = [
                (0, max_y * 2),
                (max_x * 2, max_y * 2),
                (max_x * 2, -max_y * 2),
                (0, -max_y * 2)
            ]

            rotation_angle = 360 - self.shape.rotation_angle

            if isinstance(self.shape.azimuth_placement_angle, Iterable):
                azimuth_placement_angle = self.shape.rotation_angle
            else:
                azimuth_placement_angle = self.shape.azimuth_placement_angle + self.shape.rotation_angle

        self.points = points
        self.rotation_angle = rotation_angle
        self.azimuth_placement_angle = azimuth_placement_angle
        self.workplane = self.shape.workplane
