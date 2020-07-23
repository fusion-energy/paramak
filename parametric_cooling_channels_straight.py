
import numpy as np 
import math

from paramak import ExtrudeCircleShape
from paramak.parametric_shapes import CenterColumnShieldCylinder


height = 300
coolant_channel_radius = 20
coolant_layers_offset = 15
shield_inner_radius = 200
shield_outer_radius = 350
channel_spacing_factor = 3.5

number_of_layers = math.floor(((shield_outer_radius - shield_inner_radius) - coolant_layers_offset) / ((coolant_channel_radius * 2) + coolant_layers_offset))

total_length_of_layers = (number_of_layers * (coolant_channel_radius * 2)) + ((number_of_layers - 1) * coolant_layers_offset)
remaining_length_of_shield = (shield_outer_radius - shield_inner_radius) - total_length_of_layers
first_layer_edge_position = shield_inner_radius + (remaining_length_of_shield / 2)
first_layer_center_position = first_layer_edge_position + coolant_channel_radius
last_layer_edge_position = shield_outer_radius - (remaining_length_of_shield / 2)
last_layer_center_position = last_layer_edge_position - coolant_channel_radius

layer_radii = np.linspace(first_layer_center_position, last_layer_center_position, number_of_layers)

coolant_layers = []

for layer_radius in layer_radii:

    circumference_of_coolant_layer = 2 * math.pi * layer_radius

    coolant_layer = ExtrudeCircleShape(
        points = [(layer_radius, 0)],
        radius = coolant_channel_radius,
        distance=height,
        azimuth_placement_angle=np.linspace(0, 360, math.floor(circumference_of_coolant_layer/(coolant_channel_radius * channel_spacing_factor))),
        workplane='YX')
    coolant_layers.append(coolant_layer)

shield = CenterColumnShieldCylinder(
    height=height,
    outer_radius=shield_outer_radius,
    inner_radius=shield_inner_radius,
    cut=coolant_layers
)

layer_export_number = 1
for layer in coolant_layers:
    layer.export_stp('layer' + str(layer_export_number) + '.stp')
    layer_export_number += 1

shield.export_stp('shield.stp')

