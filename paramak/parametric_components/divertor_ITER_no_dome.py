from paramak import ITERtypeDivertor
import math
import numpy as np


class ITERtypeDivertorNoDome(ITERtypeDivertor):
    """Creates a ITER-like divertor with inner and outer vertical targets

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid
        of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            dome=False,
            dome_height=None,
            dome_length=None,
            dome_thickness=None,
            dome_pos=None,
            **kwargs
        )
