import math
import numpy as np


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.

    Args:
        origin (float, float): coordinates of origin point
        point (float, float): coordinates of point to be rotated
        angle (float): rotaton angle in radians (counterclockwise)
    Returns:
        float, float: rotated point coordinates
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def extend(A, B, L):
    """Creates a point C in (AB) direction so that |AC| = L

    Args:
        A (float, float): point A coordinates
        B (float, float): point B coordinates
        L (float): distance AC

    Returns:
        float, float: point C coordinates
    """
    xa, ya = A
    xb, yb = B
    u_vec = [xb-xa, yb-ya]
    u_vec /= np.linalg.norm(u_vec)

    xc = xa + L*u_vec[0]
    yc = ya + L*u_vec[1]
    return xc, yc


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
    u_vec = [xb-xa, yb-ya]
    return np.linalg.norm(u_vec)
