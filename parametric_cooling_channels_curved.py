
import numpy as np
import math

from paramak import SweepCircleShape
from paramak.parametric_shapes import ShieldHyperbolaInnerOuterLinked

height = 1000
coolant_channel_radius = 20
coolant_layers_offset = 20
shield_edge_inner_radius = 150
shield_edge_outer_radius = 350
shield_mid_offset = -60
channel_spacing_factor = 2.5

number_of_layers = math.floor(((shield_edge_outer_radius - shield_edge_inner_radius) - coolant_layers_offset) / ((coolant_channel_radius * 2) + coolant_layers_offset))

total_length_of_layers = (number_of_layers * (coolant_channel_radius * 2)) + ((number_of_layers - 1) * coolant_layers_offset)
remaining_length_of_shield = (shield_edge_outer_radius - shield_edge_inner_radius) - total_length_of_layers
first_layer_edge_position = shield_edge_inner_radius + (remaining_length_of_shield / 2)
first_layer_center_position = first_layer_edge_position + coolant_channel_radius
last_layer_edge_position = shield_edge_outer_radius - (remaining_length_of_shield / 2)
last_layer_center_position = last_layer_edge_position - coolant_channel_radius

layer_radii = np.linspace(first_layer_center_position, last_layer_center_position, number_of_layers)

coolant_layers = []

for layer_radius in layer_radii:

    circumference_of_coolant_layer = 2 * math.pi * layer_radius

    # THIS FUNCTION HAS NOW BEEN UPDATED ON THE NEW SWEEP BRANCH
    coolant_layer = SweepCircleShape(
        points = [(layer_radius, 0)],   # bottom of channels at z=0
        radius = coolant_channel_radius,
        distance = height,
        mid_offset = shield_mid_offset,
        azimuth_placement_angle = np.linspace(0, 360, math.floor(circumference_of_coolant_layer/(coolant_channel_radius * channel_spacing_factor))),
        # spline_workplane = "XZ", # workplane can be specified. At the moment, translation only works correctly in default workplanes
        # face_workplane = "XY"  # workplane can be specified. At the moment, translation only works correctly in default workplanes
    )
    coolant_layers.append(coolant_layer)


# using RotateMixedShape for shield

# shield = RotateMixedShape(
#     points = [
#         (shield_edge_inner_radius, height, "straight"),
#         (shield_edge_outer_radius, height, "spline"),
#         (shield_edge_outer_radius + shield_mid_offset, height/2, "spline"),
#         (shield_edge_outer_radius, 0, "straight"),
#         (shield_edge_inner_radius, 0, "spline"),
#         (shield_edge_inner_radius + shield_mid_offset, height/2, "spline"),
#         (shield_edge_inner_radius, height)
#     ],
#     cut=coolant_layers
# )


# using parametric shape for shield

shield = ShieldHyperbolaInnerOuterLinked(
    height=height,
    edge_outer_radius=shield_edge_outer_radius,
    edge_inner_radius=shield_edge_inner_radius,
    mid_offset=shield_mid_offset,
    cut=coolant_layers
)

layer_export_number = 1
for layer in coolant_layers:
    layer.export_stp('layer' + str(layer_export_number) + '.stp')
    layer_export_number += 1

shield.export_stp('shield.stp')
