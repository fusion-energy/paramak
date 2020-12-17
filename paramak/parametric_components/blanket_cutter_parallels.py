
from paramak import ExtrudeStraightShape
from paramak.utils import cut_solid


class BlanketCutterParallels(ExtrudeStraightShape):
    """Creates an extruded shape with a parallel rectangular section repeated
    around the reactor. The shape is used to cut other components (eg. blankets
    and firstwalls) in order to create a banana section of the blankets with
    parrallel sides.Typically used to divide a blanket into vertical
    sections with a fixed distance between each section.

    Args:
        thickness (float): extruded distance (cm) of the cutter which
            translates to being the gap size between blankets when the cutter
            is used to segment blankets.
        gap_size (float): the distance between the inner edges of the two
            parrallel extrusions
        height (float, optional): height (cm) of the port. Defaults to 2000.0.
        width (float, optional): width (cm) of the port. Defaults to 2000.0.
        azimuth_placement_angle (list or float, optional): Defaults
            to [0., 36., 72., 108., 144., 180., 216., 252., 288., 324.]
        stp_filename (str, optional): Defaults to "BlanketCutterParallels.stp".
        stl_filename (str, optional): Defaults to "BlanketCutterParallels.stl".
        name (str, optional): Defaults to "blanket_cutter_Parallels".
        material_tag (str, optional): Defaults to
            "blanket_cutter_parallels_mat".
    """

    def __init__(
        self,
        thickness,
        gap_size,
        height=2000.,
        width=2000.,
        azimuth_placement_angle=[0., 36., 72., 108., 144., 180., 216., 252.,
                                 288., 324.],
        stp_filename="BlanketCutterParallels.stp",
        stl_filename="BlanketCutterParallels.stl",
        name="blanket_cutter_parallels",
        material_tag="blanket_cutter_parallels_mat",
        **kwargs
    ):
        self.main_cutting_shape = \
            ExtrudeStraightShape(
                distance=gap_size / 2.0,
                azimuth_placement_angle=azimuth_placement_angle,
            )
        self.gap_size = gap_size
        self.thickness = thickness
        super().__init__(
            distance=self.distance,
            azimuth_placement_angle=azimuth_placement_angle,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            name=name,
            material_tag=material_tag,
            **kwargs
        )
        self.height = height
        self.width = width

    @property
    def distance(self):
        self.distance = self.gap_size / 2.0 + self.thickness
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def gap_size(self):
        return self._gap_size

    @gap_size.setter
    def gap_size(self, value):
        self.main_cutting_shape.distance = value / 2.0
        self._gap_size = value

    @property
    def azimuth_placement_angle(self):
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self.main_cutting_shape.azimuth_placement_angle = value
        self._azimuth_placement_angle = value

    def find_points(self):

        points = [
            (0, -self.height / 2),
            (self.width, -self.height / 2),
            (self.width, self.height / 2),
            (0, self.height / 2)
        ]

        self.main_cutting_shape.points = points

        self.points = points[:-1]

    def create_solid(self):
        solid = super().create_solid()
        solid = cut_solid(solid, self.main_cutting_shape)
        self.solid = solid

        return solid
