
from typing import Optional, Tuple

from paramak import RotateMixedShape


class RotateSplineShape(RotateMixedShape):
    """Rotates a 3d CadQuery solid from points connected with splines.

    Args:
        rotation_angle: The rotation_angle to use when revolving the solid.
            Defaults to 360.0.
        stp_filename: Defaults to "RotateSplineShape.stp".
        stl_filename: Defaults to "RotateSplineShape.stl".
    """

    def __init__(
        self,
        rotation_angle: Optional[float] = 360,
        stp_filename: Optional[str] = "RotateSplineShape.stp",
        stl_filename: Optional[str] = "RotateSplineShape.stl",
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.415, 0.239, 0.603),
        **kwargs
    ):

        super().__init__(
            rotation_angle=rotation_angle,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            connection_type="spline",
            **kwargs
        )
