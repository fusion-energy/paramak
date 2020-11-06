import numpy as np
from scipy.interpolate import interp1d
import sympy as sp

from paramak import BlanketFP


class BlanketFPPoloidalSegments(BlanketFP):

    def __init__(
        self,
        segments_angles=None,
        num_segments=7,
        **kwargs
    ):
        super().__init__(
            num_points=num_segments + 1,
            **kwargs
        )
        self.num_segments = num_segments
        self.segments_angles = segments_angles

    @property
    def segments_angles(self):
        return self._segments_angles

    @segments_angles.setter
    def segments_angles(self, value):
        if value is None:
            value = np.linspace(
                self.start_angle,
                self.stop_angle,
                num=self.num_segments + 1)
        self._segments_angles = value

    @property
    def num_segments(self):
        return self._num_segments

    @num_segments.setter
    def num_segments(self, value):
        self.num_points = value
        self._num_segments = value

    def find_points(self):
        points = super().find_points()

        # every points straight connections
        for p in points:
            p[-1] = 'straight'
        self.points = points[:-1]
