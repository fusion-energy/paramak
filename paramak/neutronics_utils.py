

def define_moab_core_and_tags():

    try:
        from pymoab import core, types
    except ImportError as err:
        raise err('PyMoab not found, Reactor.export_h5m method not available')

    # create pymoab instance
    mb = core.Core()

    tags = dict()

    SENSE_TAG_NAME = "GEOM_SENSE_2"
    SENSE_TAG_SIZE = 2
    tags['surf_sense'] = mb.tag_get_handle(
        SENSE_TAG_NAME,
        SENSE_TAG_SIZE,
        types.MB_TYPE_HANDLE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)

    tags['category'] = mb.tag_get_handle(
        types.CATEGORY_TAG_NAME,
        types.CATEGORY_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)
    tags['name'] = mb.tag_get_handle(
        types.NAME_TAG_NAME,
        types.NAME_TAG_SIZE,
        types.MB_TYPE_OPAQUE,
        types.MB_TAG_SPARSE,
        create_if_missing=True)
    tags['geom_dimension'] = mb.tag_get_handle(
        types.GEOM_DIMENSION_TAG_NAME,
        1,
        types.MB_TYPE_INTEGER,
        types.MB_TAG_DENSE,
        create_if_missing=True)

    # Global ID is a default tag, just need the name to retrieve
    tags['global_id'] = mb.tag_get_handle(types.GLOBAL_ID_TAG_NAME)

    return mb, tags


def add_stl_to_moab_core(mb, surface_id, volume_id, material_name, tags):

    surface_set = mb.create_meshset()
    volume_set = mb.create_meshset()

    # recent versions of MOAB handle this automatically
    # but best to go ahead and do it manually
    mb.tag_set_data(tags['global_id'], volume_set, volume_id)

    mb.tag_set_data(tags['global_id'], surface_set, surface_id)

    # set geom IDs
    mb.tag_set_data(tags['geom_dimension'], volume_set, 3)
    mb.tag_set_data(tags['geom_dimension'], surface_set, 2)

    # set category tag values
    mb.tag_set_data(tags['category'], volume_set, "Volume")
    mb.tag_set_data(tags['category'], surface_set, "Surface")

    # establish parent-child relationship
    mb.add_parent_child(volume_set, surface_set)

    # set surface sense
    sense_data = [volume_set, np.uint64(0)]
    mb.tag_set_data(tags['surf_sense'], surface_set, sense_data)

    # load the stl triangles/vertices into the surface set
    mb.load_file(stl_filename, surface_set)

    group_set = mb.create_meshset()
    mb.tag_set_data(tags['category'], group_set, "Group")
    print("mat:{}".format(material_name))
    mb.tag_set_data(
        tags['name'],
        group_set,
        "mat:{}".format(material_name))
    mb.tag_set_data(tags['geom_dimension'], group_set, 4)

    # add the volume to this group set
    mb.add_entity(group_set, volume_set)

    return mb
