import numpy as np
from scipy.interpolate import interp1d
import sympy as sp
import warnings

from paramak import BlanketFP


class BlanketFPPoloidalSegments(BlanketFP):

    def __init__(
        self,
        segments_angles=None,
        num_segments=7,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )
        self.num_segments = num_segments
        self.segments_angles = segments_angles

    @property
    def segments_angles(self):
        return self._segments_angles

    @segments_angles.setter
    def segments_angles(self, value):
        if self.start_angle is not None or self.stop_angle is not None:
            msg = "start_angle and stop_angle attributes will be " + \
                "ignored if segments_angles is not None"
            warnings.warn(msg, UserWarning)
        elif self.num_segments is not None:
            msg = "num_segment attribute will be ignored if " + \
                "segments_angles is not None"
            warnings.warn(msg, UserWarning)
        elif value is None:
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
        if value is not None:
            self.num_points = value + 1
        self._num_segments = value

    def find_points(self):
        points = super().find_points(angles=self.segments_angles)

        # every points straight connections
        for p in points:
            p[-1] = 'straight'
        self.points = points[:-1]
