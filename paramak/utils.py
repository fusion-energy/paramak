
import math
from collections import Iterable
from hashlib import blake2b
from os import fdopen, remove
from shutil import copymode, move
from tempfile import mkstemp
from typing import Tuple, List

import cadquery as cq
import numpy as np

import paramak


def coefficients_of_line_from_points(
        point_a: Tuple[float, float], point_b: Tuple[float, float]) -> Tuple[float, float]:
    """Computes the m and c coefficients of the equation (y=mx+c) for
    a straight line from two points.

    Args:
        point_a: point 1 coordinates
        point_b: point 2 coordinates

    Returns:
        m coefficient and c coefficient
    """

    points = [point_a, point_b]
    x_coords, y_coords = zip(*points)
    coord_array = np.vstack([x_coords, np.ones(len(x_coords))]).T
    m, c = np.linalg.lstsq(coord_array, y_coords, rcond=None)[0]
    return m, c


def cut_solid(solid, cutter):
    """
    Performs a boolean cut of a solid with another solid or iterable of solids.

    Args:
        solid Shape: The Shape that you want to cut from
        cutter Shape: The Shape(s) that you want to be the cutting object

    Returns:
        Shape: The original shape cut with the cutter shape(s)
    """

    # Allows for multiple cuts to be applied
    if isinstance(cutter, Iterable):
        for cutting_solid in cutter:
            solid = solid.cut(cutting_solid.solid)
    else:
        solid = solid.cut(cutter.solid)
    return solid


def diff_between_angles(angle_a: float, angle_b: float) -> float:
    """Calculates the difference between two angles angle_a and angle_b

    Args:
        angle_a (float): angle in degree
        angle_b (float): angle in degree

    Returns:
        float: difference between the two angles in degree.
    """

    delta_mod = (angle_b - angle_a) % 360
    if delta_mod > 180:
        delta_mod -= 360
    return delta_mod


def distance_between_two_points(point_a: Tuple[float, float],
                                point_b: Tuple[float, float]) -> float:
    """Computes the distance between two points.

    Args:
        point_a (float, float): X, Y coordinates of the first point
        point_b (float, float): X, Y coordinates of the second point

    Returns:
        float: distance between A and B
    """

    xa, ya = point_a
    xb, yb = point_b
    u_vec = [xb - xa, yb - ya]
    return np.linalg.norm(u_vec)


def extend(point_a: Tuple[float, float], point_b: Tuple[float, float],
           L: float) -> Tuple[float, float]:
    """Creates a point C in (ab) direction so that \\|aC\\| = L

    Args:
        point_a (float, float): X, Y coordinates of the first point
        point_b (float, float): X, Y coordinates of the second point
        L (float): distance AC
    Returns:
        float, float: point C coordinates
    """

    xa, ya = point_a
    xb, yb = point_b
    u_vec = [xb - xa, yb - ya]
    u_vec /= np.linalg.norm(u_vec)

    xc = xa + L * u_vec[0]
    yc = ya + L * u_vec[1]
    return xc, yc


def find_center_point_of_circle(point_a: Tuple[float, float],
                                point_b: Tuple[float, float],
                                point3: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
    """
    Calculates the center and the radius of a circle
    passing through 3 points.
    Args:
        point_a (float, float): point 1 coordinates
        point_b (float, float): point 2 coordinates
        point3 (float, float): point 3 coordinates
    Returns:
        (float, float), float: center of the circle coordinates or
        None if 3 points on a line are input and the radius
    """

    temp = point_b[0] * point_b[0] + point_b[1] * point_b[1]
    bc = (point_a[0] * point_a[0] + point_a[1] * point_a[1] - temp) / 2
    cd = (temp - point3[0] * point3[0] - point3[1] * point3[1]) / 2
    det = (point_a[0] - point_b[0]) * (point_b[1] - point3[1]) - (
        point_b[0] - point3[0]
    ) * (point_a[1] - point_b[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc * (point_b[1] - point3[1]) - cd * (point_a[1] - point_b[1])) / det
    cy = ((point_a[0] - point_b[0]) * cd - (point_b[0] - point3[0]) * bc) / det

    radius = np.sqrt((cx - point_a[0]) ** 2 + (cy - point_a[1]) ** 2)

    return (cx, cy), radius


def intersect_solid(solid, intersecter):
    """
    Performs a boolean intersection of a solid with another solid or iterable of
    solids.
    Args:
        solid Shape: The Shape that you want to intersect
        intersecter Shape: The Shape(s) that you want to be the intersecting object
    Returns:
        Shape: The original shape cut with the intersecter shape(s)
    """

    # Allows for multiple cuts to be applied
    if isinstance(intersecter, Iterable):
        for intersecting_solid in intersecter:
            solid = solid.intersect(intersecting_solid.solid)
    else:
        solid = solid.intersect(intersecter.solid)
    return solid


def rotate(origin: Tuple[float, float], point: Tuple[float, float],
           angle: float):
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
        solid (Shape): The Shape that you want to union from
        joiner (Shape): The Shape(s) that you want to form the union with the
            solid
    Returns:
        Shape: The original shape union with the joiner shape(s)
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

    cutting_wedge = paramak.CuttingWedgeFS(self)
    return cutting_wedge


def add_thickness(x: List[float], y: List[float], thickness: float,
                  dy_dx: List[float] = None):
    """Computes outer curve points based on thickness

    Args:
        x (list): list of floats containing x values
        y (list): list of floats containing y values
        thickness (float): thickness of the magnet
        dy_dx (list): list of floats containing the first order
            derivatives

    Returns:
        (list, list): R and Z lists for outer curve points
    """

    if dy_dx is None:
        dy_dx = np.diff(y) / np.diff(x)

    x_outer, y_outer = [], []
    for i in range(len(dy_dx)):
        if dy_dx[i] == float('-inf'):
            nx, ny = -1, 0
        elif dy_dx[i] == float('inf'):
            nx, ny = 1, 0
        else:
            nx = -dy_dx[i]
            ny = 1
        if i != len(dy_dx) - 1:
            if x[i] < x[i + 1]:
                convex = False
            else:
                convex = True

        if convex:
            nx *= -1
            ny *= -1
        # normalise normal vector
        normal_vector_norm = (nx ** 2 + ny ** 2) ** 0.5
        nx /= normal_vector_norm
        ny /= normal_vector_norm
        # calculate outer points
        val_x_outer = x[i] + thickness * nx
        val_y_outer = y[i] + thickness * ny
        x_outer.append(val_x_outer)
        y_outer.append(val_y_outer)

    return x_outer, y_outer


def get_hash(shape, ignored_keys: List) -> str:
    """Computes a unique hash vaue for the shape.

    Args:
        shape (list): The paramak.Shape object to find the hash value for.
        ignored_keys (list, optional): list of shape.__dict__ keys to ignore
            when creating the hash.

    Returns:
        (list, list): R and Z lists for outer curve points
    """

    hash_object = blake2b()
    shape_dict = dict(shape.__dict__)

    if ignored_keys is not None:
        for key in ignored_keys:
            if key in shape_dict.keys():
                shape_dict[key] = None

    hash_object.update(str(list(shape_dict.values())).encode("utf-8"))
    value = hash_object.hexdigest()
    return value


def _replace(filename: str, pattern: str, subst: str) -> None:
    """Opens a file and replaces occurances of a particular string
        (pattern)with a new string (subst) and overwrites the file.
        Used internally within the paramak to ensure .STP files are
        in units of cm not the default mm.
    Args:
        filename (str): the filename of the file to edit
        pattern (str): the string that should be removed
        subst (str): the string that should be used in the place of the
            pattern string
    """
    # Create temp file
    file_handle, abs_path = mkstemp()
    with fdopen(file_handle, 'w') as new_file:
        with open(filename) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))

    # Copy the file permissions from the old file to the new file
    copymode(filename, abs_path)

    # Remove original file
    remove(filename)

    # Move new file
    move(abs_path, filename)


class FaceAreaSelector(cq.Selector):
    """A custom CadQuery selector the selects faces based on their area with a
    tolerance. The following useage example will fillet the faces of an extrude
    shape with an area of 0.5. paramak.ExtrudeStraightShape(points=[(1,1),(2,1),
    (2,2)], distance=5).solid.faces(FaceAreaSelector(0.5)).fillet(0.1)

    Args:
        area (float): The area of the surface to select.
        tolerance (float, optional): The allowable tolerance of the length
            (+/-) while still being selected by the custom selector.
    """

    def __init__(self, area, tolerance=0.1):
        self.area = area
        self.tolerance = tolerance

    def filter(self, objectList):
        """Loops through all the faces in the object checking if the face
        meets the custom selector requirments or not.

        Args:
            objectList (cadquery): The object to filter the faces from.

        Returns:
            objectList (cadquery): The face that match the selector area within
                the specified tolerance.
        """

        new_obj_list = []
        for obj in objectList:
            face_area = obj.Area()

            # Only return faces that meet the requirements
            if face_area > self.area - self.tolerance and face_area < self.area + self.tolerance:
                new_obj_list.append(obj)

        return new_obj_list


class EdgeLengthSelector(cq.Selector):
    """A custom CadQuery selector the selects edges  based on their length with
    a tolerance. The following useage example will fillet the inner edge of a
    rotated triangular shape. paramak.RotateStraightShape(points=[(1,1),(2,1),
    (2,2)]).solid.edges(paramak.EdgeLengthSelector(6.28)).fillet(0.1)

    Args:
        length (float): The length of the edge to select.
        tolerance (float, optional): The allowable tolerance of the length
            (+/-) while still being selected by the custom selector.

    """

    def __init__(self, length: float, tolerance: float = 0.1):
        self.length = length
        self.tolerance = tolerance

    def filter(self, objectList):
        """Loops through all the edges in the object checking if the edge
        meets the custom selector requirments or not.

        Args:
            objectList (cadquery): The object to filter the edges from.

        Returns:
            objectList (cadquery): The edge that match the selector length
                within the specified tolerance.
        """

        new_obj_list = []
        print('filleting edge#')
        for obj in objectList:

            edge_len = obj.Length()

            # Only return edges that meet our requirements
            if edge_len > self.length - self.tolerance and edge_len < self.length + self.tolerance:

                new_obj_list.append(obj)
        print('length(new_obj_list)', len(new_obj_list))
        return new_obj_list
