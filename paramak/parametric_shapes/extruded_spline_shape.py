
from typing import Optional

from paramak import ExtrudeMixedShape


class ExtrudeSplineShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with spline
    connections.

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics).
        stp_filename: Defaults to "ExtrudeSplineShape.stp".
        stl_filename: Defaults to "ExtrudeSplineShape.stl".
    """

    def __init__(
        self,
        distance: float,
        stp_filename: Optional[str] = "ExtrudeSplineShape.stp",
        stl_filename: Optional[str] = "ExtrudeSplineShape.stl",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="spline",
            **kwargs
        )
