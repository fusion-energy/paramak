import math
from collections import Iterable

import numpy as np

import paramak


def coefficients_of_line_from_points(point1, point2):
    """Computes the m and c coefficients of the equation (y=mx+c) for
    a straight line from two points.
    Args:
        point1 (float, float): point 1 coordinates
        point2 (float, float): point 2 coordinates
    Returns:
        (float, float): m coefficient and c coefficient
    """
    points = [point1, point2]
    x_coords, y_coords = zip(*points)
    A = np.vstack([x_coords, np.ones(len(x_coords))]).T
    m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]
    return m, c


def cut_solid(solid, cutter):
    """
    Performs a boolean cut of a solid with another solid or iterable of solids.
    Args:
        solid Shape: the Shape that you want to cut from
        cutter Shape: the Shape(s) that you want to be the cutting object
    Returns:
        Shape: the original shape cut with the cutter shape(s)
    """
    # Allows for multiple cuts to be applied
    if isinstance(cutter, Iterable):
        for cutting_solid in cutter:
            solid = solid.cut(cutting_solid.solid)
    else:
        solid = solid.cut(cutter.solid)
    return solid


def diff_between_angles(a, b):
    """Calculates the difference between two angles a and b
    Args:
        a (float): angle in degree
        b (float): angle in degree
    Returns:
        float: difference between the two angles in degree.
    """
    c = (b - a) % 360
    if c > 180:
        c -= 360
    return c


def distance_between_two_points(A, B):
    """Computes the distance between two points
    Args:
        A (float, float): point A coordinates
        B (float, float): point B coordinates
    Returns:
        float: distance between A and B
    """
    xa, ya = A
    xb, yb = B
    u_vec = [xb - xa, yb - ya]
    return np.linalg.norm(u_vec)


def extend(A, B, L):
    """Creates a point C in (AB) direction so that \\|AC\\| = L
    Args:
        A (float, float): point A coordinates
        B (float, float): point B coordinates
        L (float): distance AC
    Returns:
        float, float: point C coordinates
    """
    xa, ya = A
    xb, yb = B
    u_vec = [xb - xa, yb - ya]
    u_vec /= np.linalg.norm(u_vec)

    xc = xa + L * u_vec[0]
    yc = ya + L * u_vec[1]
    return xc, yc


def find_center_point_of_circle(point1, point2, point3):
    """
    Calculates the center and the radius of a circle
    passing through 3 points.
    Args:
        point1 (float, float): point 1 coordinates
        point2 (float, float): point 2 coordinates
        point3 (float, float): point 3 coordinates
    Returns:
        float, float: center of the circle coordinates or
        None if 3 points on a line are input.
    """
    temp = point2[0] * point2[0] + point2[1] * point2[1]
    bc = (point1[0] * point1[0] + point1[1] * point1[1] - temp) / 2
    cd = (temp - point3[0] * point3[0] - point3[1] * point3[1]) / 2
    det = (point1[0] - point2[0]) * (point2[1] - point3[1]) - (
        point2[0] - point3[0]
    ) * (point1[1] - point2[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc * (point2[1] - point3[1]) - cd * (point1[1] - point2[1])) / det
    cy = ((point1[0] - point2[0]) * cd - (point2[0] - point3[0]) * bc) / det

    radius = np.sqrt((cx - point1[0]) ** 2 + (cy - point1[1]) ** 2)

    return (cx, cy), radius


def intersect_solid(solid, intersecter):
    """
    Performs a boolean intersection of a solid with another solid or iterable of
    solids.
    Args:
        solid Shape: the Shape that you want to intersect
        intersecter Shape: the Shape(s) that you want to be the intersecting object
    Returns:
        Shape: the original shape cut with the intersecter shape(s)
    """
    # Allows for multiple cuts to be applied
    if isinstance(intersecter, Iterable):
        for intersecting_solid in intersecter:
            solid = solid.intersect(intersecting_solid.solid)
    else:
        solid = solid.intersect(intersecter.solid)
    return solid


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    Args:
        origin (float, float): coordinates of origin point
        point (float, float): coordinates of point to be rotated
        angle (float): rotation angle in radians (counterclockwise)
    Returns:
        float, float: rotated point coordinates.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def union_solid(solid, joiner):
    """
    Performs a boolean union of a solid with another solid or iterable of solids
    Args:
        solid Shape: the Shape that you want to union from
        joiner Shape: the Shape(s) that you want to form the union with the
            solid
    Returns:
        Shape: the original shape union with the joiner shape(s)
    """
    # Allows for multiple unions to be applied
    if isinstance(joiner, Iterable):
        for joining_solid in joiner:
            solid = solid.union(joining_solid.solid)
    else:
        solid = solid.union(joiner.solid)
    return solid


def calculate_wedge_cut(self):
    """Calculates a wedge cut with the given rotation_angle"""

    if self.rotation_angle == 360:
        return None

    else:
        cutting_wedge = paramak.CuttingWedgeFS(self)
        if self.cut is None:
            self.cut = cutting_wedge
        else:
            if isinstance(self.cut, Iterable):
                cuts = [i for i in self.cut]
                cuts.append(cutting_wedge)
            else:
                self.cut = [self.cut, cutting_wedge]

        return None
