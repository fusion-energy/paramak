from typing import Optional, Tuple

from paramak import ExtrudeMixedShape


class ExtrudeStraightShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines.

    Args:
        distance: the extrusion distance to use
        color: the color to use when exporting the shape to CAD formats that
            support color. A tuple of three floats each ranging between 0
            and 1.
        name: the name of the shape, used to name files when exporting and
            as a legend in plots.
        translate: distance to translate / move the shape by. Specified as
            a vector of (X,Y,Z) directions.
    """

    def __init__(
        self,
        distance: float,
        color: Tuple[float, float, float, Optional[float]] = (
            1.0,
            0.498,
            0.0,
        ),
        name: str = "extrudestraightshape",
        **kwargs
    ):

        super().__init__(distance=distance, connection_type="straight", color=color, name=name, **kwargs)
