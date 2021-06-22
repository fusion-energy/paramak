
import math
import os
import shutil
import subprocess
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
from remove_dagmc_tags import remove_tags

import paramak


def trelis_command_to_create_dagmc_h5m(
        faceting_tolerance: float,
        merge_tolerance: float,
        material_key_name: Optional[str] = 'material_tag',
        geometry_key_name: Optional[str] = 'stp_filename',
        batch: Optional[bool] = True,
        h5m_filename: str = 'dagmc_not_watertight.h5m',
        manifest_filename: str = 'manifest.json',
        cubit_filename: str = 'dagmc.cub',
        trelis_filename: str = 'dagmc.trelis',
        geometry_details_filename: str = 'geometry_details.json',
        surface_reflectivity_name: str = 'reflective',
) -> List[str]:
    """Runs the Trelis executable command with the
    make_faceteted_neutronics_model.py script which produces a non water tight
    DAGMC h5m file.

    Arguments:
        faceting_tolerance: the tolerance to use when faceting surfaces.
        merge_tolerance: the tolerance to use when merging surfaces.
        material_key_name: the dictionary key containing the str or int to use
            as the material identifier.
        geometry_key_name: the dictionary key containing the str to uses as the
            CAD file identifier.
        batch: Run the Trelis command in batch model with no GUI (True) or with
            the GUI enabled (False).
        h5m_filename: the filename of the DAGMC h5m file produced. This is not
            water tight at this stage.
        manifest_filename: The filename of the json file containing a list of
            material_keys and geometry_keys.
        cubit_filename: The output filename of the file. If None then no cubit
            file will be exported.
        trelis_filename: The output filename of the file. If None then no
            trelis file will be exported.
        geometry_details_filename: The output filename of the JSON file
            containing details of the DAGMC geometry. This includes the
            resulting volume numbers of the input CAD files, which can be
            useful for specifying tallies. If None then no JSON fie will be
            exported.
        surface_reflectivity_name: The tag to assign to the reflective boundary
            in the resulting DAGMC geometry Shift requires "spec.reflect" and
            MCNP requires "boundary:Reflecting".

    Returns:
        The filename of the h5m file created
    """
    output_filenames = [
        h5m_filename,
        trelis_filename,
        cubit_filename,
        geometry_details_filename]
    filenames_extensions = ['.h5m', '.trelis', '.cub', '.json']

    path_output_filenames = []

    for output_file, extension in zip(output_filenames, filenames_extensions):

        if output_file is not None:
            path_filename = Path(output_file)

            if path_filename.suffix != extension:
                path_filename = path_filename.with_suffix(extension)

            path_filename.parents[0].mkdir(parents=True, exist_ok=True)

            path_output_filenames.append(str(path_filename))

    shutil.copy(
        src=Path(__file__).parent.absolute() / Path('parametric_neutronics') /
        'make_faceteted_neutronics_model.py',
        dst=Path().absolute()
    )

    if not Path("make_faceteted_neutronics_model.py").is_file():
        raise FileNotFoundError(
            "The make_faceteted_neutronics_model.py was not found in the \
            directory")

    os.system('rm dagmc_not_watertight.h5m')

    if batch:
        trelis_cmd = 'trelis -batch -nographics'
    else:
        trelis_cmd = 'trelis'

    os.system(
        trelis_cmd +
        " make_faceteted_neutronics_model.py \"faceting_tolerance='" +
        str(faceting_tolerance) +
        "'\" \"merge_tolerance='" +
        str(merge_tolerance) +
        "'\" \"material_key_name='" +
        str(material_key_name) +
        "'\" \"geometry_key_name='" +
        str(geometry_key_name) +
        "'\" \"h5m_filename='" +
        str(h5m_filename) +
        "'\" \"manifest_filename='" +
        str(manifest_filename) +
        "'\" \"cubit_filename='" +
        str(cubit_filename) +
        "'\" \"trelis_filename='" +
        str(trelis_filename) +
        "'\" \"geometry_details_filename='" +
        str(geometry_details_filename) +
        "'\" \"surface_reflectivity_name='" +
        str(surface_reflectivity_name) +
        "'\"")

    os.system('rm make_faceteted_neutronics_model.py')

    if not Path(h5m_filename).is_file():
        raise FileNotFoundError(
            "The h5m file " + h5m_filename + " was not found \
            in the directory, the Trelis stage has failed")

    return path_output_filenames


def make_watertight(
        input_filename: str = "dagmc_not_watertight.h5m",
        output_filename: str = "dagmc.h5m",
) -> str:
    """Runs the DAGMC make_watertight executable that seals the facetets of
    the geometry with specified input and output h5m files. Not needed for
    h5m file produced with pymoab method.

    Arguments:
        input_filename: the non watertight h5m file to make watertight.
        output_filename: the filename of the watertight h5m file.

    Returns:
        The filename of the h5m file created
    """

    if not Path(input_filename).is_file():
        raise FileNotFoundError("Failed to find {}".format(input_filename))

    os.system('rm {}'.format(output_filename))

    try:
        output = subprocess.check_output(
            "make_watertight {} -o {}".format(input_filename, output_filename),
            shell=True,
            universal_newlines=True,
        )
        print(output)
    except BaseException:
        raise NameError(
            "make_watertight failed, check DAGMC is install and the DAGMC/bin "
            "folder is in the path directory (Linux and Mac) or set as an "
            "enviromental varible (Windows)")

    if not Path(output_filename).is_file():
        raise FileNotFoundError("Failed to produce dagmc.h5m")

    return output_filename


def export_vtk(
    h5m_filename: str,
    filename: Optional[str] = 'dagmc.vtk',
    include_graveyard: Optional[bool] = False
):
    """Produces a vtk geometry compatable from the dagmc h5m file. This is
    useful for checking the geometry that is used for transport.

    Arguments:
        filename: filename of vtk outputfile. If the filename does not end
            with .vtk then .vtk will be added.
        h5m_filename: filename of h5m outputfile. If the filename does not
            end with .h5m then .h5m will be added.
        include_graveyard: optionally include the graveyard in the vtk file

    Returns:
        filename of the vtk file produced
    """

    path_h5m_filename = Path(h5m_filename)
    if path_h5m_filename.suffix != ".h5m":
        path_h5m_filename = path_h5m_filename.with_suffix(".h5m")

    if path_h5m_filename.is_file() is False:
        raise FileNotFoundError(
            'h5m_filename not found in location', path_h5m_filename
        )

    path_filename = Path(filename)
    if path_filename.suffix != ".vtk":
        path_filename = path_filename.with_suffix(".vtk")

    if include_graveyard:
        tags_to_remove = None
    else:
        tags_to_remove = [
            'graveyard.stp',
            'mat:graveyard',
            'reflective',
            'mat:vacuum',
            'cuttingwedge.stp']
    remove_tags(
        input=str(path_h5m_filename),
        output=str(path_filename),
        tags=tags_to_remove
    )

    return str(path_filename)


def define_moab_core_and_tags():
    """Creates a MOAB Core instance which can be built up by adding sets of
    triangles to the instance

    Returns:
        (pymoab Core): A pymoab.core.Core() instance
        (pymoab tag_handle): A pymoab.core.tag_get_handle() instance
    """

    try:
        from pymoab import core, types
    except ImportError:
        raise ImportError(
            'PyMoab not found, export_h5m method is not available')

    # create pymoab instance
    moab_core = core.Core()

    tags = dict()

    sense_tag_name = "GEOM_SENSE_2"
    sense_tag_size = 2
    tags['surf_sense'] = moab_core.tag_get_handle(
        sense_tag_name,
        sense_tag_size,
        types.MB_TYPE_HANDLE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)

    tags['category'] = moab_core.tag_get_handle(
        types.CATEGORY_TAG_NAME,
        types.CATEGORY_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)
    tags['name'] = moab_core.tag_get_handle(
        types.NAME_TAG_NAME,
        types.NAME_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)
    tags['geom_dimension'] = moab_core.tag_get_handle(
        types.GEOM_DIMENSION_TAG_NAME,
        1,
        types.MB_TYPE_INTEGER,
        types.MB_TAG_DENSE,
        create_if_missing=True)

    # Global ID is a default tag, just need the name to retrieve
    tags['global_id'] = moab_core.tag_get_handle(types.GLOBAL_ID_TAG_NAME)

    return moab_core, tags


def add_stl_to_moab_core(
        moab_core,
        surface_id: int,
        volume_id: int,
        material_name: str,
        tags,
        stl_filename: str):
    """Computes the m and c coefficients of the equation (y=mx+c) for
    a straight line from two points.

    Args:
        moab_core (pymoab.core.Core):
        surface_id (int): the id number to apply to the surface
        volume_id (int): the id numbers to apply to the volumes
        material_name (str): the material tag name to add. the value provided
            will be prepended with "mat:" unless it is "reflective" which is
            a special case and therefore will remain as is.
        tags (pymoab tag_handle): the MOAB tags
        stl_filename (str): the filename of the stl file to load into the moab
            core

    Returns:
        (pymoab Core): An updated pymoab.core.Core() instance
    """

    surface_set = moab_core.create_meshset()
    volume_set = moab_core.create_meshset()

    # recent versions of MOAB handle this automatically
    # but best to go ahead and do it manually
    moab_core.tag_set_data(tags['global_id'], volume_set, volume_id)

    moab_core.tag_set_data(tags['global_id'], surface_set, surface_id)

    # set geom IDs
    moab_core.tag_set_data(tags['geom_dimension'], volume_set, 3)
    moab_core.tag_set_data(tags['geom_dimension'], surface_set, 2)

    # set category tag values
    moab_core.tag_set_data(tags['category'], volume_set, "Volume")
    moab_core.tag_set_data(tags['category'], surface_set, "Surface")

    # establish parent-child relationship
    moab_core.add_parent_child(volume_set, surface_set)

    # set surface sense
    sense_data = [volume_set, np.uint64(0)]
    moab_core.tag_set_data(tags['surf_sense'], surface_set, sense_data)

    # load the stl triangles/vertices into the surface set
    moab_core.load_file(stl_filename, surface_set)

    group_set = moab_core.create_meshset()
    moab_core.tag_set_data(tags['category'], group_set, "Group")

    # reflective is a special case that should not have mat: in front
    if not material_name == 'reflective':
        dag_material_tag = "mat:{}".format(material_name)
    else:
        dag_material_tag = material_name

    moab_core.tag_set_data(
        tags['name'],
        group_set,
        dag_material_tag
    )
    moab_core.tag_set_data(tags['geom_dimension'], group_set, 4)

    # add the volume to this group set
    moab_core.add_entity(group_set, volume_set)

    return moab_core


def transform_curve(edge, tolerance: float = 1e-3):
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
        facet_splines: bool = True,
        facet_circles: bool = True,
        tolerance: float = 1e-3
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
        types_to_facet.append('BSPLINE')
    if facet_circles:
        types_to_facet.append('CIRCLE')

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


def find_center_point_of_circle(
        point_a: Tuple[float, float],
        point_b: Tuple[float, float],
        point_3: Tuple[float, float]
) -> Tuple[Tuple[float, float], float]:
    """
    Calculates the center and the radius of a circle
    passing through 3 points.
    Args:
        point_a (float, float): point 1 coordinates
        point_b (float, float): point 2 coordinates
        point_3 (float, float): point 3 coordinates
    Returns:
        (float, float), float: center of the circle coordinates or
        None if 3 points on a line are input and the radius
    """

    temp = point_b[0] * point_b[0] + point_b[1] * point_b[1]
    bc = (point_a[0] * point_a[0] + point_a[1] * point_a[1] - temp) / 2
    cd = (temp - point_3[0] * point_3[0] - point_3[1] * point_3[1]) / 2
    det = (point_a[0] - point_b[0]) * (point_b[1] - point_3[1]) - (
        point_b[0] - point_3[0]
    ) * (point_a[1] - point_b[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc * (point_b[1] - point_3[1]) -
          cd * (point_a[1] - point_b[1])) / det
    cy = ((point_a[0] - point_b[0]) * cd -
          (point_b[0] - point_3[0]) * bc) / det

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


def plotly_trace(
        points: Union[List[Tuple[float, float]], List[Tuple[float, float, float]]],
        mode: str = "markers+lines",
        name: str = None,
        color: Union[Tuple[float, float, float], Tuple[float, float, float, float]] = None
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

    if color is not None:
        color_list = [i * 255 for i in color]

        if len(color_list) == 3:
            color = "rgb(" + str(color_list).strip("[]") + ")"
        elif len(color_list) == 4:
            color = "rgba(" + str(color_list).strip("[]") + ")"

    if name is None:
        name = "Shape not named"
    else:
        name = name

    text_values = []

    for i, point in enumerate(points):
        text = "point number= {} <br> x={} <br> y= {}".format(
            i, point[0], point[1])
        if len(point) == 3:
            text = text + "<br> z= {} <br>".format(point[2])

        text_values.append(text)

    if all(len(entry) == 3 for entry in points):
        trace = go.Scatter3d(
            x=[row[0] for row in points],
            y=[row[1] for row in points],
            z=[row[2] for row in points],
            mode=mode,
            marker={"size": 3, "color": color},
            name=name
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
    view_plane: str = 'XZ',
):
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
            if view_plane == 'XZ':
                points.append((vertex.X, vertex.Z))
            elif view_plane == 'XY':
                points.append((vertex.X, vertex.Y))
            elif view_plane == 'YZ':
                points.append((vertex.Y, vertex.Z))
            elif view_plane == 'YX':
                points.append((vertex.Y, vertex.X))
            elif view_plane == 'ZY':
                points.append((vertex.Z, vertex.Y))
            elif view_plane == 'ZX':
                points.append((vertex.Z, vertex.X))
            elif view_plane == 'RZ':
                xy_coord = math.pow(vertex.X, 2) + math.pow(vertex.Y, 2)
                points.append((math.sqrt(xy_coord), vertex.Z))
            elif view_plane == 'XYZ':
                points.append((vertex.X, vertex.Y, vertex.Z))
            else:
                raise ValueError('view_plane value of ', view_plane,
                                 ' is not supported')
    return points


def load_stp_file(
    filename: str,
    scale_factor: float = 1.
):
    """Loads a stp file and makes the 3D solid and wires avaialbe for use.

    Args:
        filename: the filename used to save the html graph.
        scale_factor: a scaling factor to apply to the geometry that can be
            used to increase the size or decrease the size of the geometry.
            Useful when converting the geometry to cm for use in neutronics
            simulations.

    Returns:
        CadQuery.solid, CadQuery.Wires: soild and wires belonging to the object
    """

    part = importers.importStep(str(filename)).val()

    scaled_part = part.scale(scale_factor)
    solid = scaled_part
    wire = scaled_part.Wires()
    return solid, wire


def export_wire_to_html(
    wires,
    filename=None,
    view_plane='RZ',
    facet_splines: bool = True,
    facet_circles: bool = True,
    tolerance: float = 1e-3,
    title=None,
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

    if view_plane == 'XYZ':
        fig.update_layout(
            title=title,
            scene_aspectmode='data',
            scene=dict(
                xaxis_title=view_plane[0],
                yaxis_title=view_plane[1],
                zaxis_title=view_plane[2],
            ),
        )
    else:

        fig.update_layout(
            yaxis=dict(scaleanchor="x",
                       scaleratio=1),
            xaxis_title=view_plane[0],
            yaxis_title=view_plane[1]
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
            tolerance=tolerance
        )

        points = paramak.utils.extract_points_from_edges(
            edges=edges,
            view_plane=view_plane
        )

        fig.add_trace(
            plotly_trace(
                points=points,
                mode=mode,
                name='edge ' + str(counter)
            )
        )

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

        points = paramak.utils.extract_points_from_edges(
            edges=edges,
            view_plane=view_plane)

        fig.add_trace(plotly_trace(
            points=points,
            mode="markers",
            name='points on wire ' + str(counter)
        )
        )

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
        tolerance: Optional[float] = 0.1
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
    solid = cq.Workplane('XZ').center(0, 0)
    solid = solid.moveTo(p_0[0], p_0[1]).threePointArc(p_1, p_2)
    edge = solid.vals()[0]

    new_edge = paramak.utils.transform_curve(edge, tolerance=tolerance)

    points = paramak.utils.extract_points_from_edges(
        edges=new_edge,
        view_plane='XZ'
    )

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
        meets the custom selector requirments or not.

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
        meets the custom selector requirments or not.

        Args:
            object_list (cadquery): The object to filter the edges from.

        Returns:
            object_list (cadquery): The edge that match the selector length
                within the specified tolerance.
        """

        new_obj_list = []
        print('filleting edge#')
        for obj in object_list:

            edge_len = obj.Length()

            # Only return edges that meet our requirements
            if edge_len > self.length - self.tolerance and edge_len < self.length + self.tolerance:

                new_obj_list.append(obj)
        print('length(new_obj_list)', len(new_obj_list))
        return new_obj_list
