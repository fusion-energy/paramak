#!/usr/env/python3
import json
import os

# This script automatically produces DAGMC compatable geometry. A manifest
# file is required that specfies a the stp filenames and the materials names to
# assign. The name of the manifest file is manifest.json by default but can be
# specified using aprepro arguments. Other optional aprepro arguments are
# faceting_tolerance and merge_tolerance which default to 1e-1 and 1e-4 by
# default

# To using this script with Cubit it can be run in batch mode
# c -batch -nographics make_faceteted_neutronics_model.py

# With the Cubit GUI
# coreform_cubit make_faceteted_neutronics_model.py

# With additional arguments to overwrite the defaults
# coreform_cubit -batch -nographics make_faceteted_neutronics_model.py "faceting_tolerance='1e-4'" "merge_tolerance='1e-4'"

# An example manifest file would contain a list of dictionaries with entries
# having stp_filename and material_tag keywords. Here is an example manifest
# file with just two entries.

# coreform_cubit -batch -nographics make_faceteted_neutronics_model.py

# [
#     {
#         "material_tag": "copper",
#         "stp_filename": "inboard_tf_coils.stp"
#     },
#     {
#         "material_tag": "tungsten_carbide",
#         "stp_filename": "center_column_shield.stp"
#     }
# ]

# The specific name of dictionary key to use for material group names defaults
# to material_tag but can be specified by the user, in this example another
# dictionary key is used (called material_id) which could contain integers and
# therefore make the manifest.json file can contain strings for use with OpenMC
# and integer values to make Cubit group names are compatable with MCNP and
# Shift.

# coreform_cubit -batch -nographics make_faceteted_neutronics_model.py "material_key_name='material_id'"

# [
#     {
#         "material_id": "1",
#         "material_tag": "copper",
#         "stp_filename": "inboard_tf_coils.stp"
#     },
#     {
#         "material_id": "2",
#         "material_tag": "tungsten_carbide",
#         "stp_filename": "center_column_shield.stp"
#     }
# ]

# You can also change the default dictionary key used for the geometry file.
# By default the code looks for "stp_filename" however the dictionary key can
# be changed using the geometry_key_name argument. For example you could have
# a key name for sat files.

# coreform_cubit -batch -nographics make_faceteted_neutronics_model.py "geometry_key_name='sat_filename'"

# entries can also contain a "surface_reflectivity" key to indicate reflecting
# surfaces. This will then be used to automatically tag the surfaces.

#     {
#         "material_tag": "m3",
#         "stp_filename": "large_cake_slice.stp",
#         "surface_reflectivity": true
#     }

# The tag name to use as the reflective boundary identifier can also be
# specified using the surface_reflectivity_name argument. Defaults to
# "reflective" Shift uses "spec.reflect" and MCNP code uses "boundary:Reflecting"

def find_number_of_volumes_in_each_step_file(input_locations, basefolder):
    body_ids = ""
    volumes_in_each_step_file = []
    # all_groups=cubit.parse_cubit_list("group","all")
    # starting_group_id = len(all_groups)
    for entry in input_locations:
        # starting_group_id = starting_group_id +1
        current_vols = cubit.parse_cubit_list("volume", "all")
        print(os.path.join(basefolder, entry[geometry_key_name]))
        if entry[geometry_key_name].endswith(".sat"):
            import_type = "acis"
        if entry[geometry_key_name].endswith(
                ".stp") or entry[geometry_key_name].endswith(".step"):
            import_type = "step"
        short_file_name = os.path.split(entry[geometry_key_name])[-1]
        # print('short_file_name',short_file_name)
        # cubit.cmd('import '+import_type+' "' + entry['stp_filename'] + '" separate_bodies no_surfaces no_curves no_vertices group "'+str(short_file_name)+'"')
        cubit.cmd(
            "import "
            + import_type
            + ' "'
            + os.path.join(basefolder, entry[geometry_key_name])
            + '" separate_bodies no_surfaces no_curves no_vertices '
        )
        all_vols = cubit.parse_cubit_list("volume", "all")
        new_vols = set(current_vols).symmetric_difference(set(all_vols))
        new_vols = map(str, new_vols)
        print("new_vols", new_vols, type(new_vols))
        current_bodies = cubit.parse_cubit_list("body", "all")
        print("current_bodies", current_bodies)
        # volumes_in_group = cubit.cmd('volume in group '+str(starting_group_id))
        # print('volumes_in_group',volumes_in_group,type(volumes_in_group))
        if len(new_vols) > 1:
            cubit.cmd(
                "unite vol " +
                " ".join(new_vols) +
                " with vol " +
                " ".join(new_vols))
        all_vols = cubit.parse_cubit_list("volume", "all")
        new_vols_after_unite = set(
            current_vols).symmetric_difference(set(all_vols))
        new_vols_after_unite = map(str, new_vols_after_unite)
        # cubit.cmd('group '+str(starting_group_id)+' copy rotate 45 about z repeat 7')
        entry["volumes"] = new_vols_after_unite
        cubit.cmd(
            'group "' +
            short_file_name +
            '" add volume ' +
            " ".join(
                entry["volumes"]))
        # cubit.cmd('volume in group '+str(starting_group_id)+' copy rotate 45 about z repeat 7')
        if 'surface_reflectivity' in entry.keys():
            entry['surface_reflectivity'] = find_all_surfaces_of_reflecting_wedge(new_vols_after_unite)
            print("entry['surface_reflectivity']", entry['surface_reflectivity'])
    cubit.cmd("separate body all")
    return input_locations


def find_all_surfaces_of_reflecting_wedge(new_vols):
    surfaces_in_volume = cubit.parse_cubit_list("surface", " in volume "+' '.join(new_vols))
    surface_info_dict = {}
    for surface_id in surfaces_in_volume:
        surface = cubit.surface(surface_id)
        #area = surface.area()
        vertex_in_surface = cubit.parse_cubit_list("vertex", " in surface " + str(surface_id))
        if surface.is_planar() == True and len(vertex_in_surface) == 4:
            surface_info_dict[surface_id] = {'reflector': True}
        else:
            surface_info_dict[surface_id] = {'reflector': False}
    print('surface_info_dict', surface_info_dict)
    return surface_info_dict


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode("utf-8")
    else:
        return input


def find_reflecting_surfaces_of_reflecting_wedge(geometry_details, surface_reflectivity_name):
    print('running find_reflecting_surfaces_of_reflecting_wedge')
    wedge_volume = None
    for entry in geometry_details:
        print(entry)
        print(entry.keys())
        if 'surface_reflectivity' in entry.keys():
            print('found surface_reflectivity')
            surface_info_dict = entry['surface_reflectivity']
            wedge_volume = ' '.join(entry['volumes'])
            print('wedge_volume', wedge_volume)
            surfaces_in_wedge_volume = cubit.parse_cubit_list("surface", " in volume "+str(wedge_volume))
            print('surfaces_in_wedge_volume', surfaces_in_wedge_volume)
            for surface_id in surface_info_dict.keys():
                if surface_info_dict[surface_id]['reflector'] == True:
                    print(surface_id, 'surface originally reflecting but does it still exist')
                    if surface_id not in surfaces_in_wedge_volume:
                        del surface_info_dict[surface_id]
            for surface_id in surfaces_in_wedge_volume:
                if surface_id not in surface_info_dict.keys():
                    surface_info_dict[surface_id] = {'reflector': True}
                    cubit.cmd('group "' + surface_reflectivity_name + '" add surf ' + str(surface_id))
                    cubit.cmd('surface ' + str(surface_id)+' visibility on')
            entry['surface_reflectivity'] = surface_info_dict
            return geometry_details, wedge_volume
    return geometry_details, wedge_volume


def tag_geometry_with_mats(geometry_details):
    for entry in geometry_details:
        if material_key_name in entry.keys():
            cubit.cmd(
                'group "mat:'
                + str(entry[material_key_name])
                + '" add volume '
                + " ".join(entry["volumes"])
            )
        else:
            print('material_key_name', material_key_name, 'not found for', entry)


def imprint_and_merge_geometry():
    cubit.cmd("imprint body all")
    print('using merge_tolerance of ', merge_tolerance)
    cubit.cmd("merge tolerance " + merge_tolerance)  # optional as there is a default
    cubit.cmd("merge vol all group_results")
    cubit.cmd("graphics tol angle 3")


def scale_geometry(geometry_details):
    for entry in geometry_details:
        if 'scale' in entry.keys():
            cubit.cmd('volume ' + ' '.join(entry['volumes']) + ' scale ' + str(entry['scale']))


def save_output_files(h5m_filename, trelis_filename, cubit_filename, geometry_details_filename):
    """This saves the output files"""
    cubit.cmd("set attribute on")
    # use a faceting_tolerance 1.0e-4 or smaller for accurate simulations
    print('using faceting_tolerance of ', faceting_tolerance)
    cubit.cmd('export dagmc "'+h5m_filename+'" faceting_tolerance '+ faceting_tolerance)
    # os.system('mbconvert -1 '+h5m_filename+' dagmc_not_watertight_edges.h5m')
    if cubit_filename is not None:
        cubit.cmd('save as "'+cubit_filename+'" overwrite')
    if trelis_filename is not None:
        cubit.cmd('save as "'+trelis_filename+'" overwrite')
    if geometry_details_filename is not None:
        with open(geometry_details_filename, "w") as outfile:
            json.dump(geometry_details, outfile, indent=4)

aprepro_vars = cubit.get_aprepro_vars()

print("Found the following aprepro variables:")
print(aprepro_vars)
for var_name in aprepro_vars:
    val = cubit.get_aprepro_value_as_string(var_name)
    print("{0} = {1}".format(var_name, val))

if "faceting_tolerance" in aprepro_vars:
    faceting_tolerance = str(cubit.get_aprepro_value_as_string("faceting_tolerance"))
else:
    faceting_tolerance = str(1.0e-1)

if "merge_tolerance" in aprepro_vars:
    merge_tolerance = str(cubit.get_aprepro_value_as_string("merge_tolerance"))
else:
    merge_tolerance = str(1e-4)

if "material_key_name" in aprepro_vars:
    material_key_name = str(cubit.get_aprepro_value_as_string("material_key_name"))
else:
    material_key_name = "material_tag"

if "geometry_key_name" in aprepro_vars:
    geometry_key_name = str(cubit.get_aprepro_value_as_string("geometry_key_name"))
else:
    geometry_key_name = "stp_filename"

if "h5m_filename" in aprepro_vars:
    h5m_filename = str(cubit.get_aprepro_value_as_string("h5m_filename"))
else:
    h5m_filename = "dagmc_not_watertight.h5m"

if "manifest_filename" in aprepro_vars:
    manifest_filename = str(cubit.get_aprepro_value_as_string("manifest_filename"))
else:
    manifest_filename = "manifest.json"

if "trelis_filename" in aprepro_vars:
    trelis_filename = str(cubit.get_aprepro_value_as_string("trelis_filename"))
else:
    trelis_filename = None

if "cubit_filename" in aprepro_vars:
    cubit_filename = str(cubit.get_aprepro_value_as_string("cubit_filename"))
else:
    cubit_filename = None

if "geometry_details_filename" in aprepro_vars:
    geometry_details_filename = str(cubit.get_aprepro_value_as_string("geometry_details_filename"))
else:
    geometry_details_filename = None

if "surface_reflectivity_name" in aprepro_vars:
    surface_reflectivity_name = str(cubit.get_aprepro_value_as_string("surface_reflectivity_name"))
else:
    surface_reflectivity_name = 'reflective'


with open(manifest_filename) as f:
    geometry_details = byteify(json.load(f))

geometry_details = find_number_of_volumes_in_each_step_file( \
    geometry_details, os.path.abspath("."))

scale_geometry(geometry_details)

tag_geometry_with_mats(geometry_details)

imprint_and_merge_geometry()

find_reflecting_surfaces_of_reflecting_wedge(geometry_details, surface_reflectivity_name)

save_output_files(h5m_filename, trelis_filename, cubit_filename, geometry_details_filename)
