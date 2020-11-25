
from paramak import ExtrudeStraightShape


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
        azimuth_placement_angle (list, optional): Defaults
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
        self.main_cutting_shape = \
            ExtrudeStraightShape(
                distance=self.gap_size / 2.0,
                azimuth_placement_angle=self.azimuth_placement_angle,
            )
        self.find_points()

    @property
    def distance(self):
        self.distance = self.gap_size / 2.0 + self.thickness
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, value):
        self._cut = value

    def find_points(self):

        points = [
            (0, -self.height / 2),
            (self.width, -self.height / 2),
            (self.width, self.height / 2),
            (0, self.height / 2)
        ]

        self.main_cutting_shape.points = points
        if self.cut is None:
            self.cut = [self.main_cutting_shape]
        elif not isinstance(self.cut, list) and \
                self.cut != self.main_cutting_shape:
            self.cut = [self.cut, self.main_cutting_shape]
        elif self.main_cutting_shape not in self.cut:
            self.cut.append(self.main_cutting_shape)

        self.points = points[:-1]
