from paramak import RotateStraightShape


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
        stp_filename="CuttingWedgeFS.stp",
        stl_filename="CuttingWedgeFS.stl",
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
                'rotation angle = 360, cutting slice cannot be defined')

        else:
            max_dimension = self.shape.solid.largestDimension()

            points = [
                (0, max_dimension),
                (max_dimension, max_dimension),
                (max_dimension, -max_dimension),
                (0, -max_dimension)
            ]

            rotation_angle = 360 - self.shape.rotation_angle

            azimuth_placement_angle = self.shape.azimuth_placement_angle + self.shape.rotation_angle
            # azimuth_placement_angle setter allows > 360

        self.points = points
        self.rotation_angle = rotation_angle
        self.azimuth_placement_angle = azimuth_placement_angle
