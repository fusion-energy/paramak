
import warnings

import numpy as np
from paramak import BlanketFP, RotateStraightShape
from paramak.utils import (cut_solid, distance_between_two_points, extend,
                           rotate)
from scipy.optimize import minimize


class BlanketFPPoloidalSegments(BlanketFP):
    """Poloidally segmented Blanket inheriting from paramak.BlanketFP.

    Args:
        segments_angles (list, optional): If not None, the segments ends will
            be located at these angles. If None and if the constraints
            length_limits and nb_segments_limits are not None, segments angles
            will be linearly distributed. Else, an optimum configuration
            meeting the set requirements will be found. Defaults to None.
        num_segments (int, optional): Number of segments (igored if
            segments_angles is not None). Defaults to 7.
        length_limits ((float, float), optional): The minimum and maximum
            acceptable length of the segments. Ex: (100, 500), (100, None),
            (None, 300), None, (None, None). Defaults to None.
        nb_segments_limits ((float, float), optional): The minimum and maximum
            acceptable number of segments. Ex: (3, 10), (5, None), (None, 7),
            None, (None, None). Defaults to None.
        segments_gap (float, optional): Distance between segments. Defaults to
            0.0.
    """

    def __init__(
        self,
        segments_angles=None,
        num_segments=7,
        length_limits=None,
        nb_segments_limits=None,
        segments_gap=0.0,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )
        self.num_segments = num_segments
        self.length_limits = length_limits
        self.nb_segments_limits = nb_segments_limits
        self.segments_angles = segments_angles
        self.segments_gap = segments_gap
        self.segments_cutters = None

    @property
    def segments_angles(self):
        return self._segments_angles

    @segments_angles.setter
    def segments_angles(self, value):
        if value is not None:
            if self.start_angle is not None or self.stop_angle is not None:
                msg = "start_angle and stop_angle attributes will be " + \
                    "ignored if segments_angles is not None"
                warnings.warn(msg)
            elif self.num_segments is not None:
                msg = "num_segment attribute will be ignored if " + \
                    "segments_angles is not None"
                warnings.warn(msg)
        self._segments_angles = value

    @property
    def num_segments(self):
        return self._num_segments

    @num_segments.setter
    def num_segments(self, value):
        if value is not None:
            self.num_points = value + 1
        self._num_segments = value

    @property
    def segments_cutters(self):
        self.create_segment_cutters()
        return self._segments_cutters

    @segments_cutters.setter
    def segments_cutters(self, value):
        self._segments_cutters = value

    def get_angles(self):
        """Get the poloidal angles of the segments.

        Returns:
            list: the angles
        """
        if (self.length_limits, self.nb_segments_limits) != (None, None):
            angles = segments_optimiser(
                self.length_limits, self.nb_segments_limits,
                self.distribution, (self.start_angle, self.stop_angle),
                stop_on_success=True
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
        for point in points:
            point[-1] = 'straight'
        self.points = points[:-1]

    def create_solid(self):
        solid = super().create_solid()
        segments_cutters = self.segments_cutters
        if segments_cutters is not None:
            solid = cut_solid(solid, segments_cutters)
        self.solid = solid
        return solid

    def create_segment_cutters(self):
        """Creates a shape for cutting the blanket into segments and store it
        in segments_cutter attribute
        """
        if self.segments_gap > 0:
            # initialise main cutting shape
            cutting_shape = RotateStraightShape(
                rotation_angle=self.rotation_angle,
                azimuth_placement_angle=self.azimuth_placement_angle,
                union=[])
            # add points to the shape to avoid void solid
            cutting_shape.points = [
                (self.major_radius,
                 self.vertical_displacement),
                (self.major_radius +
                 self.minor_radius /
                 10,
                 self.vertical_displacement),
                (self.major_radius +
                 self.minor_radius /
                 10,
                 self.vertical_displacement +
                 self.minor_radius /
                 10),
                (self.major_radius,
                 self.vertical_displacement +
                 self.minor_radius /
                 10),
            ]

            # Create cutters for each gap
            for inner_point, outer_point in zip(
                    self.inner_points[:-1],
                    self.outer_points[-1::-1]):
                # initialise cutter for gap
                cutter = RotateStraightShape(
                    rotation_angle=self.rotation_angle,
                    azimuth_placement_angle=self.azimuth_placement_angle
                )
                # create rectangle of dimension |AB|*2.6 x self.segments_gap
                A = (inner_point[0], inner_point[1])
                B = (outer_point[0], outer_point[1])

                # increase rectangle length
                security_factor = 0.8
                local_thickness = distance_between_two_points(A, B)
                A = extend(A, B, -local_thickness * security_factor)
                B = extend(A, B, local_thickness * (1 + 2 * security_factor))
                # create points for cutter
                points_cutter = [
                    A,
                    B,
                    rotate(
                        B,
                        extend(
                            B,
                            A,
                            self.segments_gap),
                        angle=-np.pi / 2),
                    rotate(
                        A,
                        extend(
                            A,
                            B,
                            self.segments_gap),
                        angle=np.pi / 2)]
                cutter.points = points_cutter
                # add cutter to global cutting shape
                cutting_shape.union.append(cutter)

            self.segments_cutters = cutting_shape


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
        angles_with_extremums = [start_angle, *angles, stop_angle]

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
                return optimised_angles

    # return the results
    returned_angles = best[1]
    if returned_angles == []:
        msg = "Couldn't find optimum configuration for Blanket segments"
        raise ValueError(msg)

    return returned_angles
