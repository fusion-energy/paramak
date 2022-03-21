from typing import Optional, Tuple

from paramak import RotateMixedShape


class RotateStraightShape(RotateMixedShape):
    """Rotates a 3d CadQuery solid from points connected with straight
    connections.

    Args:
        rotation_angle: The rotation angle to use when revolving the solid
            (degrees).
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
        rotation_angle: float = 360.0,
        color: Tuple[float, float, float, Optional[float]] = (
            0.89,
            0.101,
            0.109,
        ),
        name: str = "rotatestraightshape",
        **kwargs
    ):

        super().__init__(rotation_angle=rotation_angle, color=color, connection_type="straight", name=name, **kwargs)
