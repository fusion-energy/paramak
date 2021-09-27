
from typing import Optional, Tuple

from paramak import RotateMixedShape


class RotateStraightShape(RotateMixedShape):
    """Rotates a 3d CadQuery solid from points connected with straight
    connections.

    Args:
        rotation_angle: The rotation angle to use when revolving the solid
            (degrees).
    """

    def __init__(
        self,
        rotation_angle: Optional[float] = 360.,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.89, 0.101, 0.109),
        **kwargs
    ):

        super().__init__(
            rotation_angle=rotation_angle,
            color=color,
            connection_type="straight",
            **kwargs
        )
