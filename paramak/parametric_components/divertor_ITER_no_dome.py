from paramak import ITERtypeDivertor
import math
import numpy as np


class ITERtypeDivertorNoDome(ITERtypeDivertor):
    """Creates an ITER-like divertor with inner and outer vertical targets
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
