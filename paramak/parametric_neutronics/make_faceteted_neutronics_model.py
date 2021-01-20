#!/usr/env/python3
import json
import os

# This script automatically produces DAGMC compatable geometry. A manifest
# file is required that specfies a the stp filenames and the materials names to
# assign. The name of the manifest file is manifest.json by default but can be
# specified using aprepro arguments. Other optional aprepro arguments are
# faceting_tolerance and merge_tolerance which default to 1e-1 and 1e-4 by
# default

# To using this script with Trelis it can be run in batch mode
# trelis -batch -nographics make_faceteted_neutronics_model.py

# With the Trelis GUI
# trelis make_faceteted_neutronics_model.py

# With additional arguments to overwrite the defaults
# trelis -batch -nographics make_faceteted_neutronics_model.py "faceting_tolerance='1e-4'" "merge_tolerance='1e-4'"

# An example manifest file would contain a list of dictionaries with entries
# having stp_filename and material keywords. Here is an example manifest file
# with just two entries.

# [
#     {
#         "material": "m1",
#         "stp_filename": "inboard_tf_coils.stp"
#     },
#     {
#         "material": "m2",
#         "stp_filename": "center_column_shield.stp"
#     }
# ]

# entries can also contain a "surface_reflectivity" key to indicate reflecting
# surfaces. This will then be used to automatically tag the surfaces.

#     {
#         "material": "m3",
#         "stp_filename": "large_cake_slice.stp",
#         "surface_reflectivity": true
#     }


def find_number_of_volumes_in_each_step_file(input_locations, basefolder):
    body_ids = ""
    volumes_in_each_step_file = []
    # all_groups=cubit.parse_cubit_list("group","all")
    # starting_group_id = len(all_groups)
    for entry in input_locations:
        # starting_group_id = starting_group_id +1
        current_vols = cubit.parse_cubit_list("volume", "all")
        print(os.path.join(basefolder, entry["stp_filename"]))
        if entry["stp_filename"].endswith(".sat"):
            import_type = "acis"
        if entry["stp_filename"].endswith(
                ".stp") or entry["stp_filename"].endswith(".step"):
            import_type = "step"
        short_file_name = os.path.split(entry["stp_filename"])[-1]
        # print('short_file_name',short_file_name)
        # cubit.cmd('import '+import_type+' "' + entry['stp_filename'] + '" separate_bodies no_surfaces no_curves no_vertices group "'+str(short_file_name)+'"')
        cubit.cmd(
            "import "
            + import_type
            + ' "'
            + os.path.join(basefolder, entry["stp_filename"])
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


def find_reflecting_surfaces_of_reflecting_wedge(geometry_details):
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
                    cubit.cmd('group "boundary:Reflecting" add surf ' + str(surface_id))
                    cubit.cmd('surface ' + str(surface_id)+' visibility on')
            entry['surface_reflectivity'] = surface_info_dict
            return geometry_details, wedge_volume
    return geometry_details, wedge_volume


def tag_geometry_with_mats(geometry_details):
    for entry in geometry_details:
        cubit.cmd(
            'group "mat:'
            + entry["material"]
            + '" add volume '
            + " ".join(entry["volumes"])
        )


def imprint_and_merge_geometry():
    cubit.cmd("imprint body all")
    print('using merge_tolerance of ', merge_tolerance)
    cubit.cmd("merge tolerance " + merge_tolerance)  # optional as there is a default
    cubit.cmd("merge vol all group_results")
    cubit.cmd("graphics tol angle 3")


def save_output_files():
    """This saves the output files"""
    cubit.cmd("set attribute on")
    # use a faceting_tolerance 1.0e-4 or smaller for accurate simulations
    print('using faceting_tolerance of ', faceting_tolerance)
    cubit.cmd('export dagmc "dagmc_not_watertight.h5m" faceting_tolerance '+ faceting_tolerance)
    # os.system('mbconvert -1 dagmc_not_watertight.h5m dagmc_not_watertight_edges.h5m')
    with open("geometry_details.json", "w") as outfile:
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

if "manifest" in aprepro_vars:
    manifest_filename = str(cubit.get_aprepro_value_as_string("manifest"))
else:
    manifest_filename = "manifest.json"

with open(manifest_filename) as f:
    geometry_details = byteify(json.load(f))


geometry_details = find_number_of_volumes_in_each_step_file( \
    geometry_details, os.path.abspath("."))

tag_geometry_with_mats(geometry_details)

imprint_and_merge_geometry()

find_reflecting_surfaces_of_reflecting_wedge(geometry_details)

save_output_files()
