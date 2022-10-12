import math
from typing import Tuple

import numpy as np
from paramak import RotateMixedShape, distance_between_two_points, extend, rotate


class ITERtypeDivertor(RotateMixedShape):
    """Creates an ITER-like divertor with inner and outer vertical targets and
    dome

    Args:
        anchors: xz coordinates of points at the top of vertical targets.
        coverages: coverages (anticlockwise) in degrees of the circular parts
            of vertical targets.
        radii: radii (cm) of circular parts of the vertical targets.
        lengths: leg length (cm) of the vertical targets.
        dome: if set to False, the dome will not be created.
        dome_height: distance (cm) between the dome base and lower points.
        dome_length: length of the dome.
        dome_thickness: thickness of the dome.
        dome_pos: relative location of the dome between vertical targets
            (0 inner, 1 outer). Ex: 0.5 will place the dome in between the
            targets.
        tilts ((float, float), optional): tilt angles (anticlockwise) in
            degrees for the vertical targets.
    """

    def __init__(
        self,
        anchors: Tuple[Tuple[float, float], Tuple[float, float]] = ((450, -300), (561, -367)),
        coverages: Tuple[float, float] = (90, 180),
        radii: Tuple[float, float] = (50, 25),
        lengths: Tuple[float, float] = (78, 87),
        dome: bool = True,
        dome_height: float = 43,
        dome_length: float = 66,
        dome_thickness: float = 10,
        dome_pos: float = 0.5,
        tilts: Tuple[float, float] = (-27, 0),
        **kwargs
    ):

        super().__init__(**kwargs)

        self.ivt_anchor, self.ovt_anchor = anchors
        self.ivt_coverage, self.ovt_coverage = coverages
        self.ivt_radius, self.ovt_radius = radii
        self.ivt_length, self.ovt_length = lengths
        self.ivt_tilt, self.ovt_tilt = tilts
        self.dome = dome
        self.dome_length = dome_length
        self.dome_height = dome_height
        self.dome_pos = dome_pos
        self.dome_thickness = dome_thickness

    def _create_vertical_target_points(
        self, anchor: Tuple[float, float], coverage: float, tilt: float, radius: float, length: float
    ):
        """Creates a list of points for a vertical target

        Args:
            anchor: xz coordinates of point at the top of the vertical target.
            coverage: coverages (anticlockwise) in degrees of the circular part
                of the vertical target.
            tilt: tilt angle (anticlockwise) in degrees for the vertical target.
            radius: radius (cm) of circular part of the vertical target.
            length: leg length (cm) of the vertical target.

        Returns:
            list: list of x y coordinates
        """
        points = []
        base_circle_inner = anchor[0] + radius, anchor[1]
        A = rotate(base_circle_inner, anchor, coverage)
        A_prime = rotate(base_circle_inner, anchor, coverage / 2)
        c_coord = (anchor[0], anchor[1] - length)

        A = rotate(anchor, A, tilt)
        A_prime = rotate(anchor, A_prime, tilt)
        c_coord = rotate(anchor, c_coord, tilt)
        # upper inner A
        points.append([A[0], A[1]])
        # A'
        points.append([A_prime[0], A_prime[1]])
        # B
        points.append([anchor[0], anchor[1]])
        # C
        points.append([c_coord[0], c_coord[1]])
        return points

    def _create_dome_points(
        self,
        c_coord: Tuple[float, float],
        F: Tuple[float, float],
        dome_length: float,
        dome_height: float,
        dome_thickness: float,
        dome_pos: float,
    ):
        """Creates a list of points for the dome alongside with their
        connectivity

        Args:
            c_coord: coordinate of inner end of the dome
            F: coordinate of outer end of the dome
            dome_length: dome length (cm)
            dome_height: dome height (cm)
            dome_thickness: dome thickness (cm)
            dome_pos: position of the dome between the two ends.

        Returns:
            list: list of points with connectivity
                ([[x, z, 'connection_type'], [...]])
        """
        points = []

        dome_base = extend(c_coord, F, dome_pos * distance_between_two_points(F, c_coord))
        dome_lower_point = extend(dome_base, rotate(dome_base, c_coord, -math.pi / 2), dome_height)

        d_prime = extend(dome_base, dome_lower_point, dome_height + dome_thickness)
        D = extend(
            dome_lower_point,
            rotate(dome_lower_point, d_prime, math.pi / 2),
            dome_length / 2,
        )
        E = extend(
            dome_lower_point,
            rotate(dome_lower_point, d_prime, -math.pi / 2),
            dome_length / 2,
        )

        # D
        points.append([D[0], D[1], "circle"])

        # D'
        points.append([d_prime[0], d_prime[1], "circle"])

        # E
        points.append([E[0], E[1], "straight"])
        return points

    def _create_casing_points(
        self,
        anchors: Tuple[float, float],
        c_coord: Tuple[float, float],
        F: Tuple[float, float],
        targets_lengths: Tuple[float, float],
    ):
        """Creates a list of points for the casing alongside with their
        connectivity

        Args:
            anchors: xz coordinates of points at the top of vertical targets.
            c_coord: coordinate of inner end of the dome
            F: coordinate of outer end of the dome
            targets_lengths: leg lengths of the vertical targets

        Returns:
            list: list of points with connectivity
                ([[x, z, 'connection_type'], [...]])
        """
        B, G = anchors
        h1, h2 = targets_lengths
        points = []
        # I
        I_ = extend(c_coord, F, distance_between_two_points(F, c_coord) * 1.1)
        points.append([I_[0], I_[1], "straight"])
        # J
        J = extend(G, F, h2 * 1.2)
        points.append([J[0], J[1], "straight"])
        # K
        K = extend(B, c_coord, h1 * 1.2)
        points.append([K[0], K[1], "straight"])
        # L
        L = extend(F, c_coord, distance_between_two_points(F, c_coord) * 1.1)
        points.append([L[0], L[1], "straight"])
        return points

    def find_points(self):
        """Finds the XZ points and connection types (straight and circle) that
        describe the 2D profile of the ITER-like divertor
        """

        # ivt points
        ivt_points = self._create_vertical_target_points(
            self.ivt_anchor,
            math.radians(self.ivt_coverage),
            math.radians(self.ivt_tilt),
            -self.ivt_radius,
            self.ivt_length,
        )
        # add connections
        connections = ["circle"] * 2 + ["straight"] * 2
        for i, connection in enumerate(connections):
            ivt_points[i].append(connection)

        # ovt points
        ovt_points = self._create_vertical_target_points(
            self.ovt_anchor,
            -math.radians(self.ovt_coverage),
            math.radians(self.ovt_tilt),
            self.ovt_radius,
            self.ovt_length,
        )
        # add connections
        connections = ["straight"] + ["circle"] * 2 + ["straight"]
        for i, connection in enumerate(connections):
            ovt_points[i].append(connection)
        # ovt_points need to be fliped for correct connections
        ovt_points = [[float(e[0]), float(e[1]), e[2]] for e in np.flipud(ovt_points)]

        # Dome points
        dome_points = []
        if self.dome:
            dome_points = self._create_dome_points(
                ivt_points[-1][:2],
                ovt_points[0][:2],
                self.dome_length,
                self.dome_height,
                self.dome_thickness,
                self.dome_pos,
            )

        # casing points
        self.casing_points = self._create_casing_points(
            anchors=(self.ivt_anchor, self.ovt_anchor),
            c_coord=ivt_points[-1][:2],
            F=ovt_points[0][:2],
            targets_lengths=(self.ivt_length, self.ovt_length),
        )

        # append all points
        points = ivt_points + dome_points + ovt_points + self.casing_points
        self.points = points
