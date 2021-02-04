
from typing import Optional

from paramak import ExtrudeMixedShape


class ExtrudeStraightShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines.

    Args:
        distance: the extrusion distance to use (cm units if used for
            neutronics)
        stp_filename: Defaults to "ExtrudeStraightShape.stp".
        stl_filename: Defaults to "ExtrudeStraightShape.stl".
    """

    def __init__(
        self,
        distance: float,
        stp_filename: Optional[str] = "ExtrudeStraightShape.stp",
        stl_filename: Optional[str] = "ExtrudeStraightShape.stl",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="straight",
            **kwargs
        )
