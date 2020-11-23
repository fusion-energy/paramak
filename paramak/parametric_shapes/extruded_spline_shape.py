
from paramak import ExtrudeMixedShape


class ExtrudeSplineShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with spline
    connections.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics).
        stp_filename (str, optional): Defaults to "ExtrudeSplineShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeSplineShape.stl".
    """

    def __init__(
        self,
        distance,
        stp_filename="ExtrudeSplineShape.stp",
        stl_filename="ExtrudeSplineShape.stl",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="spline",
            **kwargs
        )
