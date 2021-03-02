
import math
import os
import shutil
import warnings
from collections import defaultdict
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import SubElement

import defusedxml.ElementTree as ET
import h5py
import matplotlib.pyplot as plt
import numpy as np

try:
    import openmc
except ImportError:
    warnings.warn('OpenMC not found, create_inital_particles \
            method not available', UserWarning)


def trelis_command_to_create_dagmc_h5m(
        faceting_tolerance: float,
        merge_tolerance: float,
        batch: bool = True,
) -> str:
    """Runs the Trelis executable command with the
    make_faceteted_neutronics_model.py script which produces a non water tight
    DAGMC h5m file.

    Arguments:
        faceting_tolerance: the tolerance to use when faceting surfaces.
        merge_tolerance: the tolerance to use when merging surfaces.
        batch: 

    Returns:
        The filename of the h5m file created
    """
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
        os.system(
            "trelis -batch -nographics make_faceteted_neutronics_model.py \"faceting_tolerance='" +
            str(faceting_tolerance) +
            "'\" \"merge_tolerance='" +
            str(merge_tolerance) +
            "'\"")
    else:
        os.system(
            "trelis make_faceteted_neutronics_model.py \"faceting_tolerance='" +
            str(faceting_tolerance) +
            "'\" \"merge_tolerance='" +
            str(merge_tolerance) +
            "'\"")

    os.system('rm make_faceteted_neutronics_model.py')

    if not Path("dagmc_not_watertight.h5m").is_file():
        raise FileNotFoundError(
            "The dagmc_not_watertight.h5m was not found \
            in the directory, the Trelis stage has failed")

    return "dagmc_not_watertight.h5m"


def make_watertight(
        input_filename: str = "dagmc_not_watertight.h5m",
        output_filename: str = "dagmc.h5m",
) -> str:
    """Runs the DAGMC make_watertight executable that seals the facetets of
    the geometry with specified input and output h5m files.

    Arguments:
        input_filename: the non watertight h5m file to make watertight.
        output_filename: the filename of the watertight h5m file.

    Returns:
        The filename of the h5m file created
    """

    if not Path(input_filename).is_file():
        raise FileNotFoundError("Failed to find {}".format(input_filename))

    os.system('rm {}'.format(output_filename))

    if os.system("make_watertight {} -o {}".format(input_filename,
                                                   output_filename)) != 0:
        raise ValueError(
            "make_watertight failed, check DAGMC is install and the \
                DAGMC/bin folder is in the path directory (Linux and Mac) \
                or set as an enviromental varible (Windows)")

    if not Path(output_filename).is_file():
        raise FileNotFoundError("Failed to produce dagmc.h5m")

    return output_filename


def define_moab_core_and_tags():
    """Creates a MOAB Core instance which can be built up by adding sets of
    triangles to the instance

    Returns:
        (pymoab Core): A pymoab.core.Core() instance
        (pymoab tag_handle): A pymoab.core.tag_get_handle() instance
    """

    try:
        from pymoab import core, types
    except ImportError as err:
        raise err('PyMoab not found, export_h5m method is not available')

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
        material_name (str): the material tag name to add. Will be prepended
            with mat:
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

    moab_core.tag_set_data(
        tags['name'],
        group_set,
        "mat:{}".format(material_name))
    moab_core.tag_set_data(tags['geom_dimension'], group_set, 4)

    # add the volume to this group set
    moab_core.add_entity(group_set, volume_set)

    return moab_core


def _save_2d_mesh_tally_as_png(
        score: str,
        filename: str,
        tally
) -> str:
    """Extracts 2D mesh tally results from a tally and saves the result as
    a png image.

    Arguments:
        score (str): The tally score to filter the tally with, e.g. ‘flux’,
            ‘heating’, etc.
        filename (str): The filename to use when saving the png output file
        tally (opencmc.tally()): The OpenMC to extract the mesh tally
            resutls  from.
    """

    try:
        import openmc
    except ImportError as err:
        raise err(
            'openmc not found, _save_2d_mesh_tally_as_png method is not \
            available')

    my_slice = tally.get_slice(scores=[score])
    tally_filter = tally.find_filter(filter_type=openmc.MeshFilter)
    shape = tally_filter.mesh.dimension.tolist()
    shape.remove(1)
    my_slice.mean.shape = shape

    fig = plt.subplot()
    fig.imshow(my_slice.mean).get_figure().savefig(filename, dpi=300)
    fig.clear()

    return filename


def get_neutronics_results_from_statepoint_file(
        statepoint_filename: str,
        fusion_power: Optional[float] = None
) -> dict:
    """Reads the statepoint file from the neutronics simulation
    and extracts the tally results.

    Arguments:
        statepoint_filename (str): The name of the statepoint file
        fusion_power (float): The fusion power of the reactor, which is used to
            scale some tallies. Defaults to None

    Returns:
        dict: a dictionary of the simulation results
    """

    try:
        import openmc
    except ImportError as err:
        raise err(
            'openmc not found, get_neutronics_results_from_statepoint_file \
            method is not available')

    # open the results file
    statepoint = openmc.StatePoint(statepoint_filename)

    results = defaultdict(dict)

    # access the tallies
    for tally in statepoint.tallies.values():

        if tally.name.endswith('TBR'):

            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"].sum()
            tally_std_dev = data_frame['std. dev.'].sum()
            results[tally.name] = {
                'result': tally_result,
                'std. dev.': tally_std_dev,
            }

        elif tally.name.endswith('heating'):

            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"].sum()
            tally_std_dev = data_frame['std. dev.'].sum()
            results[tally.name]['MeV per source particle'] = {
                'result': tally_result / 1e6,
                'std. dev.': tally_std_dev / 1e6,
            }

            if fusion_power is not None:
                results[tally.name]['Watts'] = {
                    'result': tally_result * 1.602176487e-19 * (fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                    'std. dev.': tally_std_dev * 1.602176487e-19 * (fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                }

        elif tally.name.endswith('flux'):

            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"].sum()
            tally_std_dev = data_frame['std. dev.'].sum()
            results[tally.name]['Flux per source particle'] = {
                'result': tally_result,
                'std. dev.': tally_std_dev,
            }

        elif tally.name.endswith('spectra'):
            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"]
            tally_std_dev = data_frame['std. dev.']
            results[tally.name]['Flux per source particle'] = {
                'energy': openmc.mgxs.GROUP_STRUCTURES['CCFE-709'].tolist(),
                'result': tally_result.tolist(),
                'std. dev.': tally_std_dev.tolist(),
            }

        elif '_on_2D_mesh' in tally.name:
            score = tally.name.split('_')[0]
            _save_2d_mesh_tally_as_png(
                score=score,
                tally=tally,
                filename=tally.name.replace(
                    '(',
                    '').replace(
                    ')',
                    '').replace(
                    ',',
                    '-'))

        elif '_on_3D_mesh' in tally.name:
            mesh_id = 1
            mesh = statepoint.meshes[mesh_id]

            xs = np.linspace(
                mesh.lower_left[0],
                mesh.upper_right[0],
                mesh.dimension[0] + 1
            )
            ys = np.linspace(
                mesh.lower_left[1],
                mesh.upper_right[1],
                mesh.dimension[1] + 1
            )
            zs = np.linspace(
                mesh.lower_left[2],
                mesh.upper_right[2],
                mesh.dimension[2] + 1
            )
            tally = statepoint.get_tally(name=tally.name)

            data = tally.mean[:, 0, 0]
            error = tally.std_dev[:, 0, 0]

            data = data.tolist()
            error = error.tolist()

            for content in [data, error]:
                for counter, i in enumerate(content):
                    if math.isnan(i):
                        content[counter] = 0.

            write_3d_mesh_tally_to_vtk(
                xs=xs,
                ys=ys,
                zs=zs,
                tally_label=tally.name,
                tally_data=data,
                error_data=error,
                outfile=tally.name.replace(
                    '(',
                    '').replace(
                    ')',
                    '').replace(
                    ',',
                    '-') +
                '.vtk')

        else:
            # this must be a standard score cell tally
            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"].sum()
            tally_std_dev = data_frame['std. dev.'].sum()
            results[tally.name]['events per source particle'] = {
                'result': tally_result,
                'std. dev.': tally_std_dev,
            }

    return results


def write_3d_mesh_tally_to_vtk(
        xs: np.linspace,
        ys: np.linspace,
        zs: np.linspace,
        tally_data: List[float],
        error_data: Optional[List[float]] = None,
        outfile: Optional[str] = '3d_mesh_tally_data.vtk',
        tally_label: Optional[str] = '3d_mesh_tally_data',
) -> str:
    """Converts regular 3d data into a vtk file for visualising the data.
    Programs that can visualise vtk files include Paraview
    https://www.paraview.org/ and VisIt
    https://wci.llnl.gov/simulation/computer-codes/visit

    Arguments:
        xs: A numpy array containing evenly spaced numbers from the lowest x
            coordinate value to the highest x coordinate value.
        ys: A numpy array containing evenly spaced numbers from the lowest y
            coordinate value to the highest y coordinate value.
        zs: A numpy array containing evenly spaced numbers from the lowest z
            coordinate value to the highest z coordinate value.
        tally_data: A list of data values to assign to the vtk dataset.
        error_data: A list of error data values to assign to the vtk dataset.
        outfile: The filename of the output vtk file.
        tally_label: The name to assign to the dataset in the vtk file.

    Returns:
        str: the filename of the file produced
    """
    try:
        import vtk
    except (ImportError, ModuleNotFoundError):
        msg = "Conversion to VTK requested," \
            "but the Python VTK module is not installed. Try pip install pyvtk"
        raise ImportError(msg)

    vtk_box = vtk.vtkRectilinearGrid()

    vtk_box.SetDimensions(len(xs), len(ys), len(zs))

    vtk_x_array = vtk.vtkDoubleArray()
    vtk_x_array.SetName('x-coords')
    vtk_x_array.SetArray(xs, len(xs), True)
    vtk_box.SetXCoordinates(vtk_x_array)

    vtk_y_array = vtk.vtkDoubleArray()
    vtk_y_array.SetName('y-coords')
    vtk_y_array.SetArray(ys, len(ys), True)
    vtk_box.SetYCoordinates(vtk_y_array)

    vtk_z_array = vtk.vtkDoubleArray()
    vtk_z_array.SetName('z-coords')
    vtk_z_array.SetArray(zs, len(zs), True)
    vtk_box.SetZCoordinates(vtk_z_array)

    tally = np.array(tally_data)
    tally_data = vtk.vtkDoubleArray()
    tally_data.SetName(tally_label)
    tally_data.SetArray(tally, tally.size, True)

    if error_data is not None:
        error = np.array(error_data)
        error_data = vtk.vtkDoubleArray()
        error_data.SetName("error_tag")
        error_data.SetArray(error, error.size, True)

    vtk_box.GetCellData().AddArray(tally_data)
    vtk_box.GetCellData().AddArray(error_data)

    writer = vtk.vtkRectilinearGridWriter()

    writer.SetFileName(outfile)

    writer.SetInputData(vtk_box)

    print('Writing %s' % outfile)

    writer.Write()

    return outfile


def create_inital_particles(
        source,
        number_of_source_particles: int = 2000
) -> str:
    """Accepts an openmc source and creates an inital_source.h5 that can be
    used to find intial xyz, direction and energy of the partice source.

    Arguments:
        source: (openmc.Source()): the OpenMC source to create an inital source
            file from.
        number_of_source_particles: The number of particle to sample.

    Returns:
        str: the filename of the h5 file produced
    """

    # MATERIALS

    # no real materials are needed for finding the source
    mats = openmc.Materials([])

    # GEOMETRY

    # just a minimal geometry
    outer_surface = openmc.Sphere(r=100000, boundary_type='vacuum')
    cell = openmc.Cell(region=-outer_surface)
    universe = openmc.Universe(cells=[cell])
    geom = openmc.Geometry(universe)

    # SIMULATION SETTINGS

    # Instantiate a Settings object
    sett = openmc.Settings()
    # this will fail but it will write the inital_source.h5 file first
    sett.run_mode = "eigenvalue"
    sett.particles = number_of_source_particles
    sett.batches = 1
    sett.inactive = 0
    sett.write_initial_source = True

    sett.source = source

    model = openmc.model.Model(geom, mats, sett)

    os.system('rm *.xml')
    model.export_to_xml()

    # this just adds write_initial_source == True to the settings.xml
    tree = ET.parse("settings.xml")
    root = tree.getroot()
    elem = SubElement(root, "write_initial_source")
    elem.text = "true"
    tree.write("settings.xml")

    # This will crash hence the try except loop, but it writes the
    # inital_source.h5
    try:
        openmc.run(output=False)
    except BaseException:
        pass

    return "initial_source.h5"


def extract_points_from_initial_source(
        input_filename: str = 'initial_source.h5',
        view_plane: str = 'RZ'
) -> list:
    """Reads in an inital source h5 file (generated by OpenMC), extracts point
    and projects them onto a view plane.

    Arguments:
        input_filename: the OpenMC source to create an inital source
            file from.
        view_plane: The plane to project. Options are 'XZ', 'XY', 'YZ',
            'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'. Defaults to 'RZ'. Defaults to
            'RZ'.

    Returns:
        list: list of points extracted
    """

    h5_file = h5py.File(input_filename, 'r')
    dset = h5_file['source_bank']

    points = []

    for particle in dset:
        if view_plane == 'XZ':
            points.append((particle[0][0], particle[0][2]))
        elif view_plane == 'XY':
            points.append((particle[0][0], particle[0][1]))
        elif view_plane == 'YZ':
            points.append((particle[0][1], particle[0][2]))
        elif view_plane == 'YX':
            points.append((particle[0][1], particle[0][0]))
        elif view_plane == 'ZY':
            points.append((particle[0][2], particle[0][1]))
        elif view_plane == 'ZX':
            points.append((particle[0][2], particle[0][0]))
        elif view_plane == 'RZ':
            xy_coord = math.pow(particle[0][0], 2) + \
                math.pow(particle[0][1], 2)
            points.append((math.sqrt(xy_coord), particle[0][2]))
        elif view_plane == 'XYZ':
            points.append((particle[0][0], particle[0][1], particle[0][2]))
        else:
            raise ValueError('view_plane value of ', view_plane,
                             ' is not supported')
    return points
