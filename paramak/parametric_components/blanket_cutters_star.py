from typing import Iterable, Union

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
        height: float = 2000.0,
        width: float = 2000.0,
        azimuth_placement_angle: Union[float, Iterable[float]] = [
            0.0,
            36.0,
            72.0,
            108.0,
            144.0,
            180.0,
            216.0,
            252.0,
            288.0,
            324.0,
        ],
        name: str = "blanket_cutter_star",
        **kwargs
    ) -> None:

        super().__init__(
            extrude_both=True, name=name, azimuth_placement_angle=azimuth_placement_angle, distance=distance, **kwargs
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
