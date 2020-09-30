from paramak import RotateStraightShape


class CuttingWedgeFS(RotateStraightShape):

    def __init__(
        self,
        shape,
        name=None,
        color=(0.5, 0.5, 0.5),
        stp_filename="CuttingSlice.stp",
        stl_filename="CuttingSlice.stl",
        rotation_angle=360,
        material_tag="cutting_slice_mat",
        azimuth_placement_angle=0,
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XZ",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
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
            azimuth_placement_angle = 360 - self.shape.rotation_angle

        self.points = points
        self.rotation_angle = rotation_angle
        self.azimuth_placement_angle = azimuth_placement_angle
