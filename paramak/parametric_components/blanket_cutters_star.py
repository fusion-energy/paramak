
from typing import Optional
from paramak import ExtrudeStraightShape


class BlanketCutterStar(ExtrudeStraightShape):
    """Creates an extruded shape with a rectangular section that is used to cut
    other components (eg. blankets and firstwalls) in order to create banana
    style blanket segments. Typically used to divide a blanket into vertical
    sections with a fixed gap between each section.

    Args:
        distance: extruded distance (cm) of the cutter which translates to being
            the gap size between blankets when the cutter is used to segment
            blankets.
        height: height (cm) of the port. Defaults to 2000.0.
        width: width (cm) of the port. Defaults to 2000.0.
        azimuth_placement_angle (list or float, optional): Defaults to
            [0., 36., 72., 108., 144., 180., 216., 252., 288., 324.]
        name: defaults to "blanket_cutter_star".
    """

    def __init__(
            self,
            distance: float,
            height: Optional[float] = 2000.,
            width: Optional[float] = 2000.,
            azimuth_placement_angle: Optional[float] = [
                0.,
                36.,
                72.,
                108.,
                144.,
                180.,
                216.,
                252.,
                288.,
                324.],
            name: Optional[str] = "blanket_cutter_star",
            **kwargs) -> None:

        super().__init__(
            extrude_both=True,
            name=name,
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
