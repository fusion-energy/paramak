
import math

import numpy as np
from paramak import (RotateMixedShape, distance_between_two_points, extend,
                     rotate)


class ITERtypeDivertor(RotateMixedShape):
    """Creates an ITER-like divertor with inner and outer vertical targets and
    dome

    Args:
        anchors ((float, float), (float, float), optional): xz coordinates of
            points at the top of vertical targets.
            Defaults to ((450, -300), (561, -367)).
        coverages ((float, float), optional): coverages (anticlockwise) in
            degrees of the circular parts of vertical targets.
            Defaults to (90, 180).
        radii ((float, float), optional): radii (cm) of circular parts of the
            vertical targets. Defaults to (50, 25).
        lengths ((float, float), optional): leg length (cm) of the vertical
            targets. Defaults to (78, 87).
        dome (bool, optional): if set to False, the dome will not be created.
            Defaults to True.
        dome_height (float, optional): distance (cm) between the dome base and
            lower points. Defaults to 43.
        dome_length (float, optional): length of the dome. Defaults to 66.
        dome_thickness (float, optional): thickness of the dome.
            Defaults to 10.
        dome_pos (float, optional): relative location of the dome between
            vertical targets (0 inner, 1 outer). Ex: 0.5 will place the dome
            in between the targets. Defaults to 0.5.
        tilts ((float, float), optional): tilt angles (anticlockwise) in
            degrees for the vertical targets. Defaults to (-27, 0).
        stp_filename (str, optional): defaults to "ITERtypeDivertor.stp".
        stl_filename (str, optional): defaults to "ITERtypeDivertor.stl".
    """

    def __init__(
        self,
        anchors=((450, -300), (561, -367)),
        coverages=(90, 180),
        radii=(50, 25),
        lengths=(78, 87),
        dome=True,
        dome_height=43,
        dome_length=66,
        dome_thickness=10,
        dome_pos=0.5,
        tilts=(-27, 0),
        stp_filename="ITERtypeDivertor.stp",
        stl_filename="ITERtypeDivertor.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.IVT_anchor, self.OVT_anchor = anchors
        self.IVT_coverage, self.OVT_coverage = coverages
        self.IVT_radius, self.OVT_radius = radii
        self.IVT_length, self.OVT_length = lengths
        self.IVT_tilt, self.OVT_tilt = tilts
        self.dome = dome
        self.dome_length = dome_length
        self.dome_height = dome_height
        self.dome_pos = dome_pos
        self.dome_thickness = dome_thickness

    def _create_vertical_target_points(
            self, anchor, coverage, tilt, radius, length):
        """Creates a list of points for a vertical target

        Args:
            anchor (float, float): xz coordinates of point at
                the top of the vertical target.
            coverage (float): coverages (anticlockwise) in degrees of the
                circular part of the vertical target.
            tilt (float): tilt angle (anticlockwise) in
                degrees for the vertical target.
            radius (float): radius (cm) of circular part of the vertical
                target.
            length (float): leg length (cm) of the vertical target.

        Returns:
            list: list of x y coordinates
        """
        points = []
        base_circle_inner = anchor[0] + radius, anchor[1]
        A = rotate(base_circle_inner, anchor, coverage)
        A_prime = rotate(base_circle_inner, anchor, coverage / 2)
        C = (anchor[0], anchor[1] - length)

        A = rotate(anchor, A, tilt)
        A_prime = rotate(anchor, A_prime, tilt)
        C = rotate(anchor, C, tilt)
        # upper inner A
        points.append([A[0], A[1]])
        # A'
        points.append([A_prime[0], A_prime[1]])
        # B
        points.append([anchor[0], anchor[1]])
        # C
        points.append([C[0], C[1]])
        return points

    def _create_dome_points(
        self, C, F, dome_length, dome_height, dome_thickness, dome_pos
    ):
        """Creates a list of points for the dome alongside with their
        connectivity

        Args:
            C (float, float): coordinate of inner end of the dome
            F (float, float): coordinate of outer end of the dome
            dome_length (float): dome length (cm)
            dome_height (float): dome height (cm)
            dome_thickness (float): dome thickness (cm)
            dome_pos (float): position of the dome between the two ends.

        Returns:
            list: list of points with connectivity
                ([[x, z, 'connection_type'], [...]])
        """
        points = []

        dome_base = extend(C, F, dome_pos * distance_between_two_points(F, C))
        dome_lower_point = extend(
            dome_base, rotate(dome_base, C, -math.pi / 2), dome_height
        )

        D_prime = extend(
            dome_base,
            dome_lower_point,
            dome_height +
            dome_thickness)
        D = extend(
            dome_lower_point,
            rotate(dome_lower_point, D_prime, math.pi / 2),
            dome_length / 2,
        )
        E = extend(
            dome_lower_point,
            rotate(dome_lower_point, D_prime, -math.pi / 2),
            dome_length / 2,
        )

        # D
        points.append([D[0], D[1], "circle"])

        # D'
        points.append([D_prime[0], D_prime[1], "circle"])

        # E
        points.append([E[0], E[1], "straight"])
        return points

    def _create_casing_points(self, anchors, C, F, targets_lengths):
        """Creates a list of points for the casing alongside with their
        connectivity

        Args:
            anchors ((float, float), (float, float)): xz coordinates of points
                at the top of vertical targets.
            C (float, float): coordinate of inner end of the dome
            F (float, float): coordinate of outer end of the dome
            targets_lengths (float, float): leg lengths of the vertical targets

        Returns:
            list: list of points with connectivity
                ([[x, z, 'connection_type'], [...]])
        """
        B, G = anchors
        h1, h2 = targets_lengths
        points = []
        # I
        I_ = extend(C, F, distance_between_two_points(F, C) * 1.1)
        points.append([I_[0], I_[1], "straight"])
        # J
        J = extend(G, F, h2 * 1.2)
        points.append([J[0], J[1], "straight"])
        # K
        K = extend(B, C, h1 * 1.2)
        points.append([K[0], K[1], "straight"])
        # L
        L = extend(F, C, distance_between_two_points(F, C) * 1.1)
        points.append([L[0], L[1], "straight"])
        return points

    def find_points(self):
        """Finds the XZ points and connection types (straight and circle) that
        describe the 2D profile of the ITER-like divertor
        """

        # IVT points
        IVT_points = self._create_vertical_target_points(
            self.IVT_anchor,
            math.radians(self.IVT_coverage),
            math.radians(self.IVT_tilt),
            -self.IVT_radius,
            self.IVT_length,
        )
        # add connections
        connections = ["circle"] * 2 + ["straight"] * 2
        for i, connection in enumerate(connections):
            IVT_points[i].append(connection)

        # OVT points
        OVT_points = self._create_vertical_target_points(
            self.OVT_anchor,
            -math.radians(self.OVT_coverage),
            math.radians(self.OVT_tilt),
            self.OVT_radius,
            self.OVT_length,
        )
        # add connections
        connections = ["straight"] + ["circle"] * 2 + ["straight"]
        for i, connection in enumerate(connections):
            OVT_points[i].append(connection)
        # OVT_points need to be fliped for correct connections
        OVT_points = [[float(e[0]), float(e[1]), e[2]]
                      for e in np.flipud(OVT_points)]

        # Dome points
        dome_points = []
        if self.dome:
            dome_points = self._create_dome_points(
                IVT_points[-1][:2],
                OVT_points[0][:2],
                self.dome_length,
                self.dome_height,
                self.dome_thickness,
                self.dome_pos,
            )

        # casing points
        casing_points = self._create_casing_points(
            anchors=(self.IVT_anchor, self.OVT_anchor),
            C=IVT_points[-1][:2],
            F=OVT_points[0][:2],
            targets_lengths=(self.IVT_length, self.OVT_length),
        )

        # append all points
        points = IVT_points + dome_points + OVT_points + casing_points
        self.points = points
