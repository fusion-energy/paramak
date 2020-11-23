
from paramak import ExtrudeMixedShape


class ExtrudeStraightShape(ExtrudeMixedShape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        stp_filename (str, optional): Defaults to "ExtrudeStraightShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeStraightShape.stl".
    """

    def __init__(
        self,
        distance,
        stp_filename="ExtrudeStraightShape.stp",
        stl_filename="ExtrudeStraightShape.stl",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            connection_type="straight",
            **kwargs
        )
