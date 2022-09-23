import math
from collections.abc import Iterable
from hashlib import blake2b
from os import fdopen, remove
from pathlib import Path
from shutil import copymode, move
from tempfile import mkstemp
from typing import List, Optional, Tuple, Union

import cadquery as cq
import numpy as np
import plotly.graph_objects as go
from cadquery import importers
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from cadquery.occ_impl import shapes
import OCP


def export_solids_to_brep_object(
    solids: Iterable,
):
    """Returns a brep object from a iterable of solids with merged surfaces.

    Args:
        solids: a list of cadquery solids

    Returns:
        brep cadquery object
    """

    # TODO bring non merge capability back
    # if not merge:
    #     geometry_to_save = cq.Compound.makeCompound([self.solid, self.graveyard.solid.val()])
    #     geometry_to_save.exportBrep(str(path_filename))

    bldr = OCP.BOPAlgo.BOPAlgo_Splitter()

    if len(solids) == 1:
        return solids[0].val()

    for solid in solids:
        # checks if solid is a compound as .val() is not needed for compounds
        if isinstance(solid, cq.occ_impl.shapes.Compound):
            bldr.AddArgument(solid.wrapped)
        else:
            bldr.AddArgument(solid.val().wrapped)

    bldr.SetNonDestructive(True)

    bldr.Perform()

    bldr.Images()

    merged_solid = cq.Compound(bldr.Shape())

    return merged_solid


def export_solids_to_brep(
    solids: Iterable,
    filename: str = "reactor.brep",
):
    """Exports a brep file for the Reactor.solid.

    Args:
        solids: a list of cadquery solids
        filename: the filename of exported the brep file.

    Returns:
        filename of the brep created
    """

    path_filename = Path(filename)

    if path_filename.suffix != ".brep":
        msg = "When exporting a brep file the filename must end with .brep"
        raise ValueError(msg)

    path_filename.parents[0].mkdir(parents=True, exist_ok=True)

    merged_solid = export_solids_to_brep_object(solids)

    merged_solid.exportBrep(str(path_filename))

    return str(path_filename)


def export_solids_to_dagmc_h5m(
    solids: List,
    filename: str = "dagmc.h5m",
    min_mesh_size: float = 5,
    max_mesh_size: float = 20,
    verbose: bool = False,
    volume_atol: float = 0.000001,
    center_atol: float = 0.000001,
    bounding_box_atol: float = 0.000001,
    tags: List[str] = None,
):
    if verbose:
        print("solids", solids, "\n")
        print("tags", tags, "\n")
    if len(tags) != len(solids):
        msg = (
            "When specifying tags then there must be one tag for "
            f"every shape. Currently there are {len(tags)} tags "
            f"provided and {len(solids)} shapes"
        )
        raise ValueError(msg)

    compound_expanded_tags = []
    # solids could contain compounds
    for tag, solid in zip(tags, solids):
        # before accessing the .val() check it exists
        if hasattr(solid, "val"):
            # if it is a compound then we need more material tags
            if isinstance(solid.val(), cq.occ_impl.shapes.Compound):
                additional_tags = [tag] * len(solid.val().Solids())
                compound_expanded_tags = compound_expanded_tags + additional_tags
            else:
                compound_expanded_tags.append(tag)
            # if it is a compound then we need more material tags
        elif isinstance(solid, cq.occ_impl.shapes.Compound):
            additional_tags = [tag] * len(solid.Solids())
            compound_expanded_tags = compound_expanded_tags + additional_tags
        else:
            compound_expanded_tags.append(tag)

    if verbose:
        print("compound_expanded_tags", compound_expanded_tags, "\n")

    # a local import is used here as these packages need Moab to work
    from brep_to_h5m import mesh_brep, mesh_to_h5m_in_memory_method
    import brep_part_finder as bpf

    # saves the reactor as a Brep file with merged surfaces
    brep_shape = export_solids_to_brep_object(solids=solids)

    brep_file_part_properties = bpf.get_part_properties_from_shapes(brep_shape)

    if verbose:
        print("brep_file_part_properties", brep_file_part_properties, "\n")

    shape_properties = bpf.get_part_properties_from_shapes(solids)
    # for counter, solid in enumerate(solids):

    #     shape_properties[counter] = bpf.get_part_properties_from_shape(solid)

    if verbose:
        print("shape_properties", shape_properties)

    # request to find part ids that are mixed up in the Brep file
    # using the volume, center, bounding box that we know about when creating the
    # CAD geometry in the first place

    brep_and_shape_part_ids = bpf.get_matching_part_ids(
        brep_part_properties=brep_file_part_properties,
        shape_properties=shape_properties,
        volume_atol=volume_atol,
        center_atol=center_atol,
        bounding_box_atol=bounding_box_atol,
    )
    if verbose:
        print(f"brep_and_shape_part_ids={brep_and_shape_part_ids}")

    material_tags_in_brep_order = []
    for (brep_id, shape_id) in brep_and_shape_part_ids:
        material_tags_in_brep_order.append(compound_expanded_tags[shape_id - 1])

    if verbose:
        print(f"material_tags_in_brep_order={material_tags_in_brep_order}")

    # gmsh requires an actual brep file to load
    tmp_brep_filename = mkstemp(suffix=".brep", prefix="paramak_")[1]
    brep_shape.exportBrep(tmp_brep_filename)

    gmsh, volumes = mesh_brep(
        brep_filename=tmp_brep_filename,
        min_mesh_size=min_mesh_size,
        max_mesh_size=max_mesh_size,
    )

    if verbose:
        gmsh_filename = mkstemp(suffix=".msh", prefix="paramak_")[1]
        print(f"written gmsh file to {gmsh_filename}")
        gmsh.write(gmsh_filename)

    h5m_filename = mesh_to_h5m_in_memory_method(
        volumes=volumes,
        material_tags=material_tags_in_brep_order,
        h5m_filename=filename,
    )

    if verbose:
        print(f"written brep file to {tmp_brep_filename}")
    else:
        # temporary brep is deleted using os.remove
        remove(tmp_brep_filename)

    return h5m_filename


def get_bounding_box(solid) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Calculates a bounding box for the Shape and returns the coordinates of
    the corners lower-left and upper-right. This function is useful when
    creating OpenMC mesh tallies as the bounding box is required in this form"""

    if isinstance(solid, (cq.Compound, shapes.Solid)):

        bound_box = solid.BoundingBox()
        # previous method lopped though solids but this is not needed
        # for single_solid in solid.Solids():
        #     bound_box = single_solid.BoundingBox()

    else:
        bound_box = solid.val().BoundingBox()

    lower_left = (bound_box.xmin, bound_box.ymin, bound_box.zmin)

    upper_right = (bound_box.xmax, bound_box.ymax, bound_box.zmax)

    return (lower_left, upper_right)


def get_center_of_bounding_box(solid):
    """Calculates the geometric center of the solids bounding box"""

    bounding_box = get_bounding_box(solid)

    center = (
        (bounding_box[0][0] + bounding_box[1][0]) / 2,
        (bounding_box[0][1] + bounding_box[1][1]) / 2,
        (bounding_box[0][2] + bounding_box[1][2]) / 2,
    )

    return center


def get_largest_dimension(solid):
    """Calculates the extent of the geometry in the x,y and z axis and returns
    the largest of the three."""

    bounding_box = get_bounding_box(solid)

    largest_dimension = max(
        abs(bounding_box[0][0] - bounding_box[0][1]),
        abs(bounding_box[0][2] - bounding_box[1][0]),
        abs(bounding_box[1][1] - bounding_box[1][2]),
    )

    return largest_dimension


def get_largest_distance_from_origin(solid):
    """Calculates the distance from (0, 0, 0) to the furthest part of
    the geometry. This distance is returned as an positive value."""

    bounding_box = get_bounding_box(solid)

    largest_dimension = max(
        (
            abs(bounding_box[0][0]),
            abs(bounding_box[0][1]),
            abs(bounding_box[0][2]),
            abs(bounding_box[1][0]),
            abs(bounding_box[1][1]),
            abs(bounding_box[1][2]),
        )
    )

    return largest_dimension


def transform_curve(edge, tolerance: Optional[float] = 1e-3):
    """Converts a curved edge into a series of straight lines (facetets) with
    the provided tolerance.

    Args:
        edge (cadquery.Wire): The CadQuery wire to redraw as a series of
            straight lines (facet)
        tolerance: faceting toleranceto use when faceting cirles and
            splines. Defaults to 1e-3.

    Returns:
        cadquery.Wire
    """

    curve = edge._geomAdaptor()  # adapt the edge into curve
    start = curve.FirstParameter()
    end = curve.LastParameter()

    points = GCPnts_QuasiUniformDeflection(curve, tolerance, start, end)
    verts = (cq.Vector(points.Value(i + 1)) for i in range(points.NbPoints()))

    return cq.Wire.makePolygon(verts)


def facet_wire(
    wire,
    facet_splines: Optional[bool] = True,
    facet_circles: Optional[bool] = True,
    tolerance: Optional[float] = 1e-3,
):
    """Converts specified curved edge types from a wire into a series of
    straight lines (facetets) with the provided tol (tolerance).

    Args:
        wire (cadquery.Wire): The CadQuery wire to select edge from which will
            be redraw as a series of straight lines (facet).
        facet_splines: If True then spline edges will be faceted. Defaults
            to True.
        facet_splines: If True then circle edges will be faceted.Defaults
            to True.
        tolerance: faceting toleranceto use when faceting cirles and
            splines. Defaults to 1e-3.

    Returns:
        cadquery.Wire
    """
    edges = []

    types_to_facet = []
    if facet_splines:
        types_to_facet.append("BSPLINE")
    if facet_circles:
        types_to_facet.append("CIRCLE")

    if isinstance(wire, cq.occ_impl.shapes.Edge):
        # this is for when a edge is passed
        iterable_of_wires = [wire]
    elif isinstance(wire, cq.occ_impl.shapes.Wire):
        # this is for imported stp files
        iterable_of_wires = wire.Edges()
    else:
        # this is for cadquery generated solids
        iterable_of_wires = wire.val().Edges()

    for edge in iterable_of_wires:
        if edge.geomType() in types_to_facet:
            edges.extend(transform_curve(edge, tolerance=tolerance).Edges())
        else:
            edges.append(edge)

    return edges


def coefficients_of_line_from_points(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> Tuple[float, float]:
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


def angle_between_two_points_on_circle(
    point_1: Tuple[float, float], point_2: Tuple[float, float], radius_of_circle: float
):

    separation = distance_between_two_points(point_1, point_2)
    isos_tri_term = (2 * math.pow(radius_of_circle, 2) - math.pow(separation, 2)) / (2 * math.pow(radius_of_circle, 2))
    angle = math.acos(isos_tri_term)
    return angle


def distance_between_two_points(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """Computes the distance between two points.

    Args:
        point_a (float, float): X, Y coordinates of the first point
        point_b (float, float): X, Y coordinates of the second point

    Returns:
        float: distance between A and B
    """

    xa, ya = point_a[0], point_a[1]
    xb, yb = point_b[0], point_b[1]
    u_vec = [xb - xa, yb - ya]
    return np.linalg.norm(u_vec)


def extend(point_a: Tuple[float, float], point_b: Tuple[float, float], L: float) -> Tuple[float, float]:
    """Creates a point C in (ab) direction so that \\|aC\\| = L

    Args:
        point_a (float, float): X, Y coordinates of the first point
        point_b (float, float): X, Y coordinates of the second point
        L (float): distance AC
    Returns:
        float, float: point C coordinates
    """

    xa, ya = point_a[0], point_a[1]
    xb, yb = point_b[0], point_b[1]
    u_vec = [xb - xa, yb - ya]
    u_vec /= np.linalg.norm(u_vec)

    xc = xa + L * u_vec[0]
    yc = ya + L * u_vec[1]
    return xc, yc


def find_center_point_of_circle(
    point_a: Tuple[float, float],
    point_b: Tuple[float, float],
    point_3: Tuple[float, float],
) -> Union[Tuple[float, float], None]:
    """
    Calculates the center of a circle passing through 3 points.
    Args:
        point_a: point 1 coordinates
        point_b: point 2 coordinates
        point_3: point 3 coordinates
    Returns:
        center of the circle coordinates or None if 3 points on a line are
        input and the radius
    """

    temp = point_b[0] * point_b[0] + point_b[1] * point_b[1]
    bc = (point_a[0] * point_a[0] + point_a[1] * point_a[1] - temp) / 2
    cd = (temp - point_3[0] * point_3[0] - point_3[1] * point_3[1]) / 2
    det = (point_a[0] - point_b[0]) * (point_b[1] - point_3[1]) - (point_b[0] - point_3[0]) * (point_a[1] - point_b[1])

    if abs(det) < 1.0e-6:
        return None

    # Center of circle
    cx = (bc * (point_b[1] - point_3[1]) - cd * (point_a[1] - point_b[1])) / det
    cy = ((point_a[0] - point_b[0]) * cd - (point_b[0] - point_3[0]) * bc) / det

    return (cx, cy)


def find_radius_of_circle(
    center_point: Tuple[float, float],
    edge_point: Tuple[float, float],
) -> float:
    """Calculates the radius of a circle.

    Args:
        center_point: x, y coordinates of the center of te circle
        edge_point: x, y coordinates of a point on the edge of the circle
    Returns:
        the radius of the circle
    """

    if center_point == edge_point:
        return np.inf

    radius = np.sqrt((center_point[0] - edge_point[0]) ** 2 + (center_point[1] - edge_point[1]) ** 2)

    return radius


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


def rotate(origin: Tuple[float, float], point: Tuple[float, float], angle: float):
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
    px, py = point[0], point[1]

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

    from paramak import CuttingWedgeFS

    cutting_wedge = CuttingWedgeFS(self)
    return cutting_wedge


def add_thickness(x: List[float], y: List[float], thickness: float, dy_dx: List[float] = None) -> Tuple[list, list]:
    """Computes outer curve points based on thickness

    Args:
        x (list): list of floats containing x values
        y (list): list of floats containing y values
        thickness (float): thickness of the magnet
        dy_dx (list): list of floats containing the first order
            derivatives

    Returns:
        R and Z lists for outer curve points
    """

    if dy_dx is None:
        dy_dx = np.diff(y) / np.diff(x)

    x_outer, y_outer = [], []
    for i in range(len(dy_dx)):
        if dy_dx[i] == float("-inf"):
            nx, ny = -1, 0
        elif dy_dx[i] == float("inf"):
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
        # normalize normal vector
        normal_vector_norm = (nx**2 + ny**2) ** 0.5
        nx /= normal_vector_norm
        ny /= normal_vector_norm
        # calculate outer points
        val_x_outer = x[i] + thickness * nx
        val_y_outer = y[i] + thickness * ny
        x_outer.append(val_x_outer)
        y_outer.append(val_y_outer)

    return x_outer, y_outer


def get_hash(shape, ignored_keys: List = None) -> str:
    """Computes a unique hash value for the shape.

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
    """Opens a file and replaces occurrences of a particular string
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
    with fdopen(file_handle, "w") as new_file:
        with open(filename) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))

    # Copy the file permissions from the old file to the new file
    copymode(filename, abs_path)

    # Remove original file
    remove(filename)

    # Move new file
    move(abs_path, filename)


def plotly_trace(
    points: Union[List[Tuple[float, float]], List[Tuple[float, float, float]]],
    mode: str = "markers+lines",
    name: str = None,
    color: Union[Tuple[float, float, float], Tuple[float, float, float, float]] = None,
) -> Union[go.Scatter, go.Scatter3d]:
    """Creates a plotly trace representation of the points of the Shape
    object. This method is intended for internal use by Shape.export_html.

    Args:
        points: A list of tuples containing the X, Z points of to add to
            the trace.
        mode: The mode to use for the Plotly.Scatter graph. Options include
            "markers", "lines" and "markers+lines". Defaults to
            "markers+lines"
        name: The name to use in the graph legend color

    Returns:
        plotly trace: trace object
    """

    if color is None:
        color_string = "rgb(125, 125, 125)"
    else:
        color_list = [i * 255 for i in color]

        if len(color_list) == 3:
            color_string = "rgb(" + str(color_list).strip("[]") + ")"
        elif len(color_list) == 4:
            color_string = "rgba(" + str(color_list).strip("[]") + ")"

    if name is None:
        name = "Shape not named"
    else:
        name = name

    text_values = []

    for i, point in enumerate(points):
        text = f"point number= {i} <br> x={point[0]} <br> y= {point[1]}"
        if len(point) == 3:
            text = text + f"<br> z= {point[2]} <br>"

        text_values.append(text)

    if all(len(entry) == 3 for entry in points):
        trace = go.Scatter3d(
            x=[row[0] for row in points],
            y=[row[1] for row in points],
            z=[row[2] for row in points],
            mode=mode,
            marker={"size": 3, "color": color_string},
            name=name,
        )

        return trace

    trace = go.Scatter(
        x=[row[0] for row in points],
        y=[row[1] for row in points],
        hoverinfo="text",
        text=text_values,
        mode=mode,
        marker={"size": 5, "color": color},
        name=name,
    )

    return trace


def extract_points_from_edges(
    edges: Union[List[cq.Wire], cq.Wire],
    view_plane: Optional[str] = "XZ",
) -> Union[Tuple[float, float, float], Tuple[float, float]]:
    """Extracts points (coordinates) from a CadQuery Edge, optionally projects
    the points to a plane and returns the points.

    Args:
        edges (CadQuery.Wires): The edges to extract points (coordinates from).
        view_plane: The axis to view the points and faceted edges from. The
            options are 'XZ', 'XY', 'YZ', 'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'.
            Defaults to 'RZ'.

    Returns:
        List of Tuples: A list of tuples with float entries for every point
    """

    if isinstance(edges, Iterable):
        list_of_edges = edges
    else:
        list_of_edges = [edges]

    points = []

    for edge in list_of_edges:
        for vertex in edge.Vertices():
            if view_plane == "XZ":
                points.append((vertex.X, vertex.Z))
            elif view_plane == "XY":
                points.append((vertex.X, vertex.Y))
            elif view_plane == "YZ":
                points.append((vertex.Y, vertex.Z))
            elif view_plane == "YX":
                points.append((vertex.Y, vertex.X))
            elif view_plane == "ZY":
                points.append((vertex.Z, vertex.Y))
            elif view_plane == "ZX":
                points.append((vertex.Z, vertex.X))
            elif view_plane == "RZ":
                xy_coord = math.pow(vertex.X, 2) + math.pow(vertex.Y, 2)
                points.append((math.sqrt(xy_coord), vertex.Z))
            elif view_plane == "XYZ":
                points.append((vertex.X, vertex.Y, vertex.Z))
            else:
                raise ValueError("view_plane value of ", view_plane, " is not supported")
    return points


def load_stp_file(filename: str, scale_factor: float = 1.0):
    """Loads a stp file and makes the 3D solid and wires available for use.

    Args:
        filename: the filename used to save the html graph.
        scale_factor: a scaling factor to apply to the geometry that can be
            used to increase the size or decrease the size of the geometry.
            Useful when converting the geometry to cm for use in neutronics
            simulations.

    Returns:
        CadQuery.solid, CadQuery.Wires: solid and wires belonging to the object
    """

    part = importers.importStep(str(filename)).val()

    scaled_part = part.scale(scale_factor)
    solid = scaled_part
    wire = scaled_part.Wires()
    return solid, wire


def export_wire_to_html(
    wires,
    filename=None,
    view_plane: str = "RZ",
    facet_splines: bool = True,
    facet_circles: bool = True,
    tolerance: float = 1e-3,
    title: Optional[str] = None,
    mode="markers+lines",
):
    """Creates a html graph representation of the points within the wires.
    Edges of certain types (spines and circles) can optionally be faceted.
    If filename provided doesn't end with .html then .html will be added.
    Viewed from the XZ plane

    Args:
        wires (CadQuery.Wire): the wire (edge) or list of wires to plot points
            from and to optionally facet.
        filename: the filename used to save the html graph. If None then no
            html file will saved but a ploty figure will still be returned.
            Defaults to None.
        view_plane: The axis to view the points and faceted edges from. The
            options are 'XZ', 'XY', 'YZ', 'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'.
            Defaults to 'RZ'
        facet_splines: If True then spline edges will be faceted. Defaults to
            True.
        facet_circles: If True then circle edges will be faceted. Defaults to
            True.
        tolerance: faceting toleranceto use when faceting cirles and splines.
            Defaults to 1e-3.
        title: the title of the plotly plot.
        mode: the plotly trace mode to use when plotting the data. Options
            include 'markers+lines', 'markers', 'lines'. Defaults to 'lines'.

    Returns:
        plotly.Figure(): figure object
    """

    fig = go.Figure()
    fig.update_layout(title=title, hovermode="closest")

    if view_plane == "XYZ":
        fig.update_layout(
            title=title,
            scene_aspectmode="data",
            scene=dict(
                xaxis_title=view_plane[0],
                yaxis_title=view_plane[1],
                zaxis_title=view_plane[2],
            ),
        )
    else:

        fig.update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1),
            xaxis_title=view_plane[0],
            yaxis_title=view_plane[1],
        )

    if isinstance(wires, list):
        list_of_wires = wires
    else:
        list_of_wires = [wires]

    for counter, wire in enumerate(list_of_wires):

        edges = facet_wire(
            wire=wire,
            facet_splines=facet_splines,
            facet_circles=facet_circles,
            tolerance=tolerance,
        )

        points = extract_points_from_edges(edges=edges, view_plane=view_plane)

        fig.add_trace(plotly_trace(points=points, mode=mode, name="edge " + str(counter)))

    for counter, wire in enumerate(list_of_wires):

        if isinstance(wire, cq.occ_impl.shapes.Edge):
            # this is for when an edge is passed
            edges = wire
        elif isinstance(wire, cq.occ_impl.shapes.Wire):
            # this is for imported stp files
            edges = wire.Edges()
        else:
            # this is for cadquery generated solids
            edges = wire.val().Edges()

        points = extract_points_from_edges(edges=edges, view_plane=view_plane)

        fig.add_trace(plotly_trace(points=points, mode="markers", name="points on wire " + str(counter)))

    if filename is not None:

        Path(filename).parents[0].mkdir(parents=True, exist_ok=True)

        path_filename = Path(filename)

        if path_filename.suffix != ".html":
            path_filename = path_filename.with_suffix(".html")

        fig.write_html(str(path_filename))

        print("Exported html graph to ", path_filename)

    return fig


def convert_circle_to_spline(
    p_0: Tuple[float, float],
    p_1: Tuple[float, float],
    p_2: Tuple[float, float],
    tolerance: Optional[float] = 0.1,
) -> List[Tuple[float, float, str]]:
    """Converts three points on the edge of a circle into a series of points
    on the edge of the circle. This is done by creating a circle edge from the
    the points provided (p_0, p_1, p_2), facets the circle with the provided
    tolerance to extracts the points on the faceted edge and returns them.

    Args:
        p_0: coordinates of the first point
        p_1: coordinates of the second point
        p_2: coordinates of the third point
        tolerance: the precision of the faceting.

    Returns:
        The new points
    """

    # work plane is arbitrarily selected and has no impact of function
    solid = cq.Workplane("XZ").center(0, 0)
    solid = solid.moveTo(p_0[0], p_0[1]).threePointArc(p_1, p_2)
    edge = solid.vals()[0]

    new_edge = transform_curve(edge, tolerance=tolerance)

    points = extract_points_from_edges(edges=new_edge, view_plane="XZ")

    return points


class FaceAreaSelector(cq.Selector):
    """A custom CadQuery selector the selects faces based on their area with a
    tolerance. The following useage example will fillet the faces of an extrude
    shape with an area of 0.5. paramak.ExtrudeStraightShape(points=[(1,1),
    (2,1), (2,2)], distance=5).solid.faces(FaceAreaSelector(0.5)).fillet(0.1)

    Args:
        area (float): The area of the surface to select.
        tolerance (float, optional): The allowable tolerance of the length
            (+/-) while still being selected by the custom selector.
    """

    def __init__(self, area, tolerance=0.1):
        self.area = area
        self.tolerance = tolerance

    def filter(self, object_list):
        """Loops through all the faces in the object checking if the face
        meets the custom selector requirements or not.

        Args:
            object_list (cadquery): The object to filter the faces from.

        Returns:
            object_list (cadquery): The face that match the selector area within
                the specified tolerance.
        """

        new_obj_list = []
        for obj in object_list:
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

    def filter(self, object_list):
        """Loops through all the edges in the object checking if the edge
        meets the custom selector requirements or not.

        Args:
            object_list (cadquery): The object to filter the edges from.

        Returns:
            object_list (cadquery): The edge that match the selector length
                within the specified tolerance.
        """

        new_obj_list = []
        print("filleting edge#")
        for obj in object_list:

            edge_len = obj.Length()

            # Only return edges that meet our requirements
            if edge_len > self.length - self.tolerance and edge_len < self.length + self.tolerance:

                new_obj_list.append(obj)
        print("length(new_obj_list)", len(new_obj_list))
        return new_obj_list


def patch_workplane():
    """Going from CadQuery 2.1 to 2.2, the 'distance' arg to extrude was renamed 'until'.
    This patch ensures that either version works fine using 'until'.
    """
    from cadquery import Workplane

    if "distance" in Workplane.extrude.__code__.co_varnames:
        extrude_func = Workplane.extrude

        def extrude(*args, **kwargs):
            if "until" in kwargs.keys():
                kwargs["distance"] = kwargs.pop("until")
            return extrude_func(*args, **kwargs)

        Workplane.extrude = extrude
