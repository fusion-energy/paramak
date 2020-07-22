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