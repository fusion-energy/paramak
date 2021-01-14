
import math
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


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
    print("mat:{}".format(material_name))
    moab_core.tag_set_data(
        tags['name'],
        group_set,
        "mat:{}".format(material_name))
    moab_core.tag_set_data(tags['geom_dimension'], group_set, 4)

    # add the volume to this group set
    moab_core.add_entity(group_set, volume_set)

    return moab_core


def _save_2d_mesh_tally_as_png(score: str, filename: str, tally):
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


def get_neutronics_results_from_statepoint_file(
        statepoint_filename: str,
        fusion_power: float = None):
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

        if tally.name.endswith('heating'):

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

        if tally.name.endswith('flux'):

            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"].sum()
            tally_std_dev = data_frame['std. dev.'].sum()
            results[tally.name]['Flux per source particle'] = {
                'result': tally_result,
                'std. dev.': tally_std_dev,
            }

        if tally.name.endswith('spectra'):
            data_frame = tally.get_pandas_dataframe()
            tally_result = data_frame["mean"]
            tally_std_dev = data_frame['std. dev.']
            results[tally.name]['Flux per source particle'] = {
                'energy': openmc.mgxs.GROUP_STRUCTURES['CCFE-709'].tolist(),
                'result': tally_result.tolist(),
                'std. dev.': tally_std_dev.tolist(),
            }

        if tally.name.startswith('tritium_production_on_2D_mesh'):

            _save_2d_mesh_tally_as_png(
                score='(n,Xt)',
                tally=tally,
                filename='tritium_production_on_2D_mesh' + tally.name[-3:]
            )

        if tally.name.startswith('flux_on_2D_mesh'):

            _save_2d_mesh_tally_as_png(
                score='flux',
                tally=tally,
                filename='flux_on_2D_mesh' + tally.name[-3:]
            )

        if tally.name.startswith('heating_on_2D_mesh'):

            _save_2d_mesh_tally_as_png(
                score='heating',
                tally=tally,
                filename='heating_on_2D_mesh' + tally.name[-3:]
            )

        if '_on_3D_mesh' in tally.name:
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
                outfile=tally.name + '.vtk'
            )

    return results


def write_3d_mesh_tally_to_vtk(
        xs,
        ys,
        zs,
        tally_label: str,
        tally_data,
        error_data,
        outfile):
    try:
        import vtk
    except (ImportError, ModuleNotFoundError):
        msg = "Conversion to VTK requested," \
            "but the Python VTK module is not installed."
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
