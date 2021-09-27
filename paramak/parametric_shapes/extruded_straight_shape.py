
from typing import Optional, Tuple

from paramak import ExtrudeMixedShape


class ExtrudeStraightShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines.

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics)
    """

    def __init__(
        self,
        distance: float,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (1.0, 0.498, 0.0),
        **kwargs
    ):

        super().__init__(
            distance=distance,
            connection_type="straight",
            color=color,
            **kwargs
        )
