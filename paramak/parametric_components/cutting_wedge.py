from paramak import RotateStraightShape


class CuttingWedge(RotateStraightShape):

    def __init__(
        self,
        height,
        radius,
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
        