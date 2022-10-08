from typing import Optional, Tuple

from paramak import RotateMixedShape


class RotateSplineShape(RotateMixedShape):
    """Rotates a 3d CadQuery solid from points connected with splines.

    Args:
        rotation_angle: The rotation_angle to use when revolving the solid.
            Defaults to 360.0.
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
            0.415,
            0.239,
            0.603,
        ),
        name: str = "rotatesplineshape",
        **kwargs
    ):

        super().__init__(rotation_angle=rotation_angle, color=color, connection_type="spline", name=name, **kwargs)
