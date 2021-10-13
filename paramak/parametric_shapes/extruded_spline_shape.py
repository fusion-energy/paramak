
from typing import Optional, Tuple

from paramak import ExtrudeMixedShape


class ExtrudeSplineShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with spline
    connections.

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics).
    """

    def __init__(
        self,
        distance: float,
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0.984, 0.603, 0.6),
        **kwargs
    ):

        super().__init__(
            distance=distance,
            connection_type="spline",
            color=color,
            **kwargs
        )
