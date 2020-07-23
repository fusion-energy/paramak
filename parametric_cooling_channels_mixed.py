
import numpy as np
import math

from paramak import RotateMixedShape, SweepCircleShape, ExtrudeCircleShape

height = 1000
curvature_height = 750
coolant_channel_radius = 40
coolant_layers_offset_at_edge = 20
shield_inner_radius_at_edge = 100
shield_outer_radius_at_edge = 400
shield_mid_inner_offset = -60
shield_mid_outer_offset = -60
channel_spacing_factor = 2.5

number_of_layers = math.floor(((shield_outer_radius_at_edge - shield_inner_radius_at_edge) - coolant_layers_offset_at_edge) / ((coolant_channel_radius * 2) + coolant_layers_offset_at_edge))

# coolant pipes

# at shield edge

shield_edge_thickness = shield_outer_radius_at_edge - shield_inner_radius_at_edge
total_length_of_layers = (number_of_layers * (coolant_channel_radius * 2)) + ((number_of_layers - 1) * coolant_layers_offset_at_edge)
remaining_length_of_shield = (shield_outer_radius_at_edge - shield_inner_radius_at_edge) - total_length_of_layers
first_layer_edge_position = shield_inner_radius_at_edge + (remaining_length_of_shield / 2)
first_layer_center_position = first_layer_edge_position + coolant_channel_radius
last_layer_edge_position = shield_outer_radius_at_edge - (remaining_length_of_shield / 2)
last_layer_center_position = last_layer_edge_position - coolant_channel_radius

edge_layer_ratio = (first_layer_center_position - shield_inner_radius_at_edge) / shield_edge_thickness

edge_layer_radii = np.linspace(first_layer_center_position, last_layer_center_position, number_of_layers)

# at shield center

shield_mid_inner_radius = shield_inner_radius_at_edge + shield_mid_inner_offset
shield_mid_outer_radius = shield_outer_radius_at_edge + shield_mid_outer_offset
shield_mid_thickness = shield_mid_outer_radius - shield_mid_inner_radius

first_layer_distance = edge_layer_ratio * shield_mid_thickness
mid_first_layer_center_position = shield_mid_inner_radius + first_layer_distance
mid_last_layer_center_position = shield_mid_outer_radius - first_layer_distance

mid_layer_radii = np.linspace(mid_first_layer_center_position, mid_last_layer_center_position, number_of_layers)

# calculations for ends

remaining_height = height - curvature_height
height_at_each_end = remaining_height / 2
mid_point_of_top_straight = (curvature_height / 2) + (height_at_each_end / 2)
mid_point_of_bottom_straight = (-curvature_height / 2) - (height_at_each_end / 2)

coolant_parts = []

for edge_layer_radius, mid_layer_radius in zip(edge_layer_radii, mid_layer_radii):

    circumference_of_coolant_layer = 2 * math.pi * edge_layer_radius

    # THIS FUNCTION HAS NOW BEEN UPDATED ON THE NEW SWEEP BRANCH
    curved_coolant = SweepCircleShape(
        points = [(edge_layer_radius, 0)],
        radius = coolant_channel_radius,
        distance = curvature_height,
        mid_offset = mid_layer_radius - edge_layer_radius,
        azimuth_placement_angle = np.linspace(0, 360, math.floor(circumference_of_coolant_layer/(coolant_channel_radius * channel_spacing_factor))),
        # spline_workplane = "XZ", # workplane can be specified. At the moment, translation only works correctly in default workplanes
        # face_workplane = "XY"  # workplane can be specified. At the moment, translation only works correctly in default workplanes
    )
    coolant_parts.append(curved_coolant)

    # For some reason, it is difficult to get the correct orientation of coolant pipes when combining SweepCircleShape
    # and ExtrudeCircleShape
    # a quick-fix could be to use SweepCircleShape again but with 0 offset but this doesn't demonstrate the paramak as good

    # top_straight_coolant = ExtrudeCircleShape(
    #     points = [(edge_layer_radius, mid_point_of_top_straight)],
    #     radius = coolant_channel_radius,
    #     distance = height_at_each_end,
    #     azimuth_placement_angle = np.linspace(0, 360, math.floor(circumference_of_coolant_layer/(coolant_channel_radius * channel_spacing_factor))),
    #     workplane = 'YX'
    # )
    # coolant_parts.append(top_straight_coolant)

    # bottom_straight_coolant = ExtrudeCircleShape(
    #     points = [(edge_layer_radius, mid_point_of_bottom_straight)],
    #     radius = coolant_channel_radius,
    #     distance = height_at_each_end,
    #     azimuth_placement_angle = np.linspace(0, 360, math.floor(circumference_of_coolant_layer/(coolant_channel_radius * channel_spacing_factor))),
    #     workplane = 'YX'
    # )
    # coolant_parts.append(bottom_straight_coolant)
    
    # ideally, we would fuse each of these shapes and add the combined shape to the coolant layers list

coolant_part_export_number = 1
for part in coolant_parts:
    part.export_stp('part' + str(coolant_part_export_number) + '.stp')
    coolant_part_export_number += 1


