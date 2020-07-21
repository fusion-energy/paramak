from paramak import RotateMixedShape
import math
import numpy as np


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def extend(A, B, L):
    """Creates a point C in (AB) direction so that |AC| = L
    """
    xa, ya = A
    xb, yb = B
    u_vec = [xb-xa, yb-ya]
    u_vec /= np.linalg.norm(u_vec)

    xc = xa + L*u_vec[0]
    yc = ya + L*u_vec[1]
    return xc, yc


def distance_between_two_points(A, B):
    xa, ya = A
    xb, yb = B
    u_vec = [xb-xa, yb-ya]
    return np.linalg.norm(u_vec)


def angle_between_two_vectors(u, v):
    unit_u = u / np.linalg.norm(u)
    unit_v = v / np.linalg.norm(v)
    dot_product = np.dot(unit_u, unit_v)
    angle = np.arccos(dot_product)
    return angle


class ITERtypeDivertor(RotateMixedShape):

    def __init__(
        self,
        anchors,
        coverages,
        radii,
        lengths,
        dome_height,
        dome_length,
        dome_thickness,
        dome_pos=0.5,
        tilts=(0, 0),
        rotation_angle=360,
        workplane="XZ",
        points=None,
        stp_filename=None,
        azimuth_placement_angle=0,
        solid=None,
        color=None,
        name=None,
        material_tag=None,
        cut=None,
            ):

        super().__init__(
            points,
            workplane,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            solid,
            rotation_angle,
            cut,
        )

        self.IVT_anchor, self.OVT_anchor = anchors
        self.IVT_coverage, self.OVT_coverage = coverages
        self.IVT_radius, self.OVT_radius = radii
        self.IVT_length, self.OVT_length = lengths
        self.IVT_tilt, self.OVT_tilt = tilts
        self.dome_length = dome_length
        self.dome_height = dome_height
        self.dome_pos = dome_pos
        self.dome_thickness = dome_thickness
    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    def create_IVT_points(self, B, coverage, tilt, R, h):
        points = []
        base_circle_inner = B[0] - R, B[1]
        A = rotate(base_circle_inner, B, coverage)
        A_prime = rotate(base_circle_inner, B, coverage/2)
        C = (B[0], B[1] - h)

        A = rotate(B, A, tilt)
        A_prime = rotate(B, A_prime, tilt)
        C = rotate(B, C, tilt)
        # upper inner A
        points.append([A[0], A[1], 'circle'])
        # A'
        points.append([A_prime[0], A_prime[1], 'circle'])
        # B
        points.append([B[0], B[1], 'straight'])
        # C
        points.append([C[0], C[1], 'straight'])
        return points

    def create_OVT_points(self, G, coverage, tilt, R, h):
        points = []
        base_circle_outer = G[0] + R, G[1]
        F = G[0], G[1] - h
        G_prime = rotate(base_circle_outer, G, -coverage/2)
        H = rotate(base_circle_outer, G, -coverage)

        H = rotate(G, H, tilt)
        G_prime = rotate(G, G_prime, tilt)
        F = rotate(G, F, tilt)

        # F
        points.append([F[0], F[1], 'straight'])
        # G
        points.append([G[0], G[1], 'circle'])
        # G'
        points.append([G_prime[0], G_prime[1], 'circle'])
        # H
        points.append([H[0], H[1], 'straight'])
        return points

    def create_dome_points(self, C, F, dome_length, dome_height, dome_thickness, dome_pos):
        points = []

        dome_base = extend(C, F, dome_pos*distance_between_two_points(F, C))
        dome_lower_point = extend(dome_base, rotate(dome_base, C, -math.pi/2), dome_height)

        D_prime = extend(dome_base, dome_lower_point, dome_height + dome_thickness)
        D = extend(dome_lower_point, rotate(dome_lower_point, D_prime, math.pi/2), dome_length/2)
        E = extend(dome_lower_point, rotate(dome_lower_point, D_prime, -math.pi/2), dome_length/2)

        # D
        points.append([D[0], D[1], 'circle'])

        # D'
        points.append([D_prime[0], D_prime[1], 'circle'])

        # E
        points.append([E[0], E[1], 'straight'])
        return points

    def create_casing_points(self, B, C, F, G, targets_lengths):
        h1, h2 = targets_lengths
        points = []
        # I
        I = extend(C, F, distance_between_two_points(F, C)*1.1)
        points.append([I[0], I[1], 'straight'])
        # J
        J = extend(G, F, h2*1.2)
        points.append([J[0], J[1], 'straight'])
        # K
        K = extend(B, C, h1*1.2)
        points.append([K[0], K[1], 'straight'])
        # L
        L = extend(F, C, distance_between_two_points(F, C)*1.1)
        points.append([L[0], L[1], 'straight'])
        return points

    def find_points(self):

        # IVT
        IVT_points = self.create_IVT_points(self.IVT_anchor, self.IVT_coverage, self.IVT_tilt, self.IVT_radius, self.IVT_length)

        # OVT

        OVT_points = self.create_OVT_points(self.OVT_anchor, self.OVT_coverage, self.OVT_tilt, self.OVT_radius, self.OVT_length)

        # Dome

        dome_points = self.create_dome_points(IVT_points[-1][:2], OVT_points[0][:2], self.dome_length, self.dome_height, self.dome_thickness, self.dome_pos)

        # casing
        casing_points = self.create_casing_points(B=self.IVT_anchor, C=IVT_points[-1][:2], F=OVT_points[0][:2], G=self.OVT_anchor, targets_lengths=(self.IVT_length, self.OVT_length))

        points = IVT_points + dome_points + OVT_points + casing_points
        points.append(points[0])  # don't know why it's needed
        self.points = points
