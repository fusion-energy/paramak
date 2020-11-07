import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import minimize
import sympy as sp
import warnings

from paramak import BlanketFP, distance_between_two_points


class BlanketFPPoloidalSegments(BlanketFP):

    def __init__(
        self,
        segments_angles=None,
        num_segments=7,
        length_limits=None,
        nb_segments_limits=None,
        stop_on_success=True,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )
        self.num_segments = num_segments
        self.length_limits = length_limits
        self.nb_segments_limits = nb_segments_limits
        self.segments_angles = segments_angles
        self.stop_on_success = stop_on_success

    @property
    def segments_angles(self):
        return self._segments_angles

    @segments_angles.setter
    def segments_angles(self, value):
        if value is not None:
            if self.start_angle is not None or self.stop_angle is not None:
                msg = "start_angle and stop_angle attributes will be " + \
                    "ignored if segments_angles is not None"
                warnings.warn(msg, UserWarning)
            elif self.num_segments is not None:
                msg = "num_segment attribute will be ignored if " + \
                    "segments_angles is not None"
                warnings.warn(msg, UserWarning)
        self._segments_angles = value

    @property
    def num_segments(self):
        return self._num_segments

    @num_segments.setter
    def num_segments(self, value):
        if value is not None:
            self.num_points = value + 1
        self._num_segments = value

    def get_angles(self):
        if (self.length_limits, self.nb_segments_limits) != (None, None):
            angles = segments_optimiser(
                self.length_limits, self.nb_segments_limits,
                self.distribution, (self.start_angle, self.stop_angle),
                stop_on_success=self.stop_on_success
            )
        elif self.segments_angles is None:
            angles = np.linspace(
                self.start_angle, self.stop_angle,
                num=self.num_segments + 1)
        else:
            angles = self.segments_angles
        return angles

    def find_points(self):
        points = super().find_points(angles=self.get_angles())

        # every points straight connections
        for p in points:
            p[-1] = 'straight'
        self.points = points[:-1]


def compute_lengths_from_angles(angles, distribution):
    """Computes the length of segments between a set of points on a (x,y)
    distribution.

    Args:
        angles (list): Contains the angles of the points (degree)
        distribution (callable): function taking an angle as argument and
            returning (x,y) coordinates.

    Returns:
        list: contains the lengths of the segments.
    """
    points = []
    for angle in angles:
        points.append(distribution(angle))

    lengths = []
    for i in range(len(points) - 1):
        lengths.append(distance_between_two_points(points[i], points[i + 1]))
    return lengths


def segments_optimiser(length_limits, nb_segments_limits, distribution, angles,
                       stop_on_success=True):
    """Optimiser segmenting a given R(theta), Z(theta) distribution of points
    with constraints regarding the number of segments and the length of the
    segments.

    Args:
        length_limits ((float, float)): The minimum and maximum acceptable
            length of the segments. Ex: (100, 500), (100, None), (None, 300),
            None, (None, None)
        nb_segments_limits ((int, int)): The minimum and maximum acceptable
            number of segments. Ex: (3, 10), (5, None), (None, 7),
            None, (None, None)
        distribution (callable): function taking an angle as argument and
            returning (x,y) coordinates.
        angles ((float, float)): the start and stop angles of the distribution.
        stop_on_sucess (bool, optional): If set to True, the optimiser will
            stop as soon as a configuration meets the requirements.

    Returns:
        list: list of optimised angles
    """
    if length_limits is None:
        min_length, max_length = None, None
    else:
        min_length, max_length = length_limits

    if nb_segments_limits is None:
        min_nb_segments, max_nb_segments = None, None
    else:
        min_nb_segments, max_nb_segments = nb_segments_limits

    if min_length is None:
        min_length = 0
    if max_length is None:
        max_length = float('inf')
    if min_nb_segments is None:
        min_nb_segments = 1
    if max_nb_segments is None:
        max_nb_segments = 50

    start_angle, stop_angle = angles

    # define cost function
    def cost_function(angles):
        angles_with_extremums = [start_angle] + \
            [angle for angle in angles] + [stop_angle]

        lengths = compute_lengths_from_angles(
            angles_with_extremums, distribution)

        cost = 0
        for length in lengths:
            if not min_length <= length <= max_length:
                cost += min(abs(min_length - length), abs(max_length - length))
        return cost

    # test for several numbers of segments the best config
    best = [float("inf"), []]

    for nb_segments in range(min_nb_segments, max_nb_segments + 1):
        # initialise angles to linspace
        list_of_angles = \
            np.linspace(start_angle, stop_angle, num=nb_segments + 1)

        # use scipy minimize to find best set of angles
        res = minimize(
            cost_function, list_of_angles[1:-1], method="Nelder-Mead")

        # complete the optimised angles with extrema
        optimised_angles = [start_angle] + \
            [angle for angle in res.x] + [stop_angle]

        # check that the optimised angles meet the lengths requirements
        lengths = compute_lengths_from_angles(optimised_angles, distribution)
        break_the_rules = False
        for length in lengths:
            if not min_length <= length <= max_length:
                break_the_rules = True
                break
        if not break_the_rules:
            # compare with previous results and get the minimum
            # cost function value
            best = min(best, [res.fun, optimised_angles], key=lambda x: x[0])
            if stop_on_success:
                print('The optimised angles are ', optimised_angles)
                return optimised_angles

    # return the results
    returned_angles = best[1]
    if returned_angles == []:
        msg = "Couldn't find optimum configuration for Blanket segments"
        raise ValueError(msg)
    else:
        print('The optimised angles are ', optimised_angles)
        return returned_angles
