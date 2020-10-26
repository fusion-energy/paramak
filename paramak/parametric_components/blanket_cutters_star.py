
from paramak import ExtrudeStraightShape


class BlanketCutterStar(ExtrudeStraightShape):
    """Creates an extruded shape with a rectangular section that is used to cut
    other components (eg. blankets and firstwalls) in order to create banana
    stlye blanket segments. Typically used to divide a blanket into vertical
    sections with a fixed gap between each section.

    Args:
        distance (float): extruded distance (cm) of the cutter which translates
            to being the gap size between blankets when the cutter is used to
            segment blankets.
        azimuth_placement_angle (float, optional): the azimuth angle(s) used
            when positioning the shape. If an iterable of angles is provided,
            the shape is duplicated at all angles. Defaults to [0., 36.,
            72., 108., 144., 180., 216., 252., 288., 324.]
        height (float, optional): height (cm) of the port. Defaults to 2000
        width (float, optional): width (cm) of the port. Defaults to 2000
        stp_filename (str, optional): defaults to "BlanketCutterStar.stp".
        stl_filename (str, optional): defaults to "BlanketCutterStar.stl".
        name (str, optional): defaults to "blanket_cutter_star".
        material_tag (str, optional): defaults to
            "blanket_cutter_star_mat".
    """

    def __init__(
        self,
        distance,
        azimuth_placement_angle=[0., 36., 72., 108., 144., 180., 216., 252.,
                                 288., 324.],
        height=2000,
        width=2000,
        stp_filename="BlanketCutterStar.stp",
        stl_filename="BlanketCutterStar.stl",
        name="blanket_cutter_star",
        material_tag="blanket_cutter_star_mat",
        **kwargs
    ):

        super().__init__(
            extrude_both=True,
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            distance=distance,
            **kwargs
        )

        self.azimuth_placement_angle = azimuth_placement_angle
        self.height = height
        self.width = width
        self.distance = distance

    def find_points(self):

        points = [
            (0, -self.height / 2),
            (self.width, -self.height / 2),
            (self.width, self.height / 2),
            (0, self.height / 2),
        ]
        self.points = points
