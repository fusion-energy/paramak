from typing import Optional, Tuple, Union

from paramak import RotateMixedShape


class RotateStraightShape(RotateMixedShape):
    """Rotates a 3d CadQuery solid from points connected with straight
    connections.

    Args:
        rotation_angle: The rotation angle to use when revolving the solid
            (degrees).
    """

    # def __init__(
    #     self,
    rotation_angle: float = 360.0
    color: Union[Tuple[float, float, float, float], Tuple[float, float, float]] = (
        (0.89, 0.101, 0.109),
    )
    name: str = "rotatestraightshape"
    #     **kwargs
    # ):
    connection_type: str = "straight"
    # points:Union[tuple, list]=None

    # super().__init__(
    #     rotation_angle=rotation_angle,
    #     # color=color,
    #     connection_type="straight",
    #     name=name,
    #     **kwargs
    # )
