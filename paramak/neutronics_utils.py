
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
        raise err('PyMoab not found, export_h5m method not available')

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
        surface_id,
        volume_id,
        material_name,
        tags,
        stl_filename):
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
