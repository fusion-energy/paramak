import os
import paramak
import numpy as np
import cadquery as cq
from cadquery.vis import show

# Original radial build values
original_radial_build = [
    (paramak.LayerType.GAP, 55),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.SOLID, 60),
    (paramak.LayerType.SOLID, 10),
]
original_elongation = 2
original_triangularity = 0.55
original_n_tf_coils = 8
original_coil_height_factor = 1
original_divertor_thickness = 50

# Function to create a reactor with modified radial build
def create_reactor(
    radial_build=original_radial_build,
    elongation = original_elongation,
    triangularity = original_triangularity,
    n_tf_coils = original_n_tf_coils,
    coil_height_factor = original_coil_height_factor,
    divertor_thickness=original_divertor_thickness
):

    reactor_diameter = sum([layer[1] for layer in radial_build])
    minor_radius = radial_build[4][1]/2
    major_radius = sum([layer[1] for layer in radial_build][:4])+minor_radius

    theta = 3 * np.pi / 2
    divertor_radius = major_radius + minor_radius * np.cos(theta + triangularity * np.sin(theta))

    reactor_height = elongation * radial_build[4][1] * 0.5 + sum([layer[1] for layer in radial_build[5:]])

    # makes a rectangle that overlaps the lower blanket under the plasma
    # the intersection of this and the layers will form the lower divertor
    points = [(divertor_radius-divertor_thickness, -2000), (divertor_radius-divertor_thickness, 0), (divertor_radius+divertor_thickness, 0), (divertor_radius+divertor_thickness, -2000)]
    divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)

    tf_coils = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point=(10, reactor_height+5),
        vertical_mid_point=(reactor_diameter+5,0),
        thickness = 40,
        distance = 50 ,
        rotation_angle = 180.0,
        name = "toroidal_field_coil",
        with_inner_leg = True,
        azimuthal_placement_angles=np.linspace(0, 180, n_tf_coils)
    )

    coils = [tf_coils]
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10],
        [20, 50, 50, 20],
        [20, 50, 50, 20],
        [
            (reactor_diameter+5+50+10+20/2, 300*coil_height_factor),
            (reactor_diameter+5+50+15+50/2, 100*coil_height_factor),
            (reactor_diameter+5+50+15+50/2, -100*coil_height_factor),
            (reactor_diameter+5+50+10+20/2, -300*coil_height_factor)
        ]
    ):
        coils.append(
            paramak.poloidal_field_coil(
                height=height, width=width,
                center_point=center_point,
                rotation_angle=180
            )
        )
        coils.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=180,
                center_point=center_point        
            )
        )

    return paramak.spherical_tokamak_from_plasma(
        radial_build=radial_build,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=180,
        colors={
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": (1., 0.7, 0.8, 0.6),
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
            "add_extra_cut_shape_1": (0.6, 0.3, 0.4), # tf coils
            "add_extra_cut_shape_2": (0.4, 0.9, 0.4), # pf coil
            "add_extra_cut_shape_3": (0.9, 0.4, 0.4), # pf coil case
            "add_extra_cut_shape_4": (0.4, 0.9, 0.4), # pf coil
            "add_extra_cut_shape_5": (0.9, 0.4, 0.4), # pf coil case
            "add_extra_cut_shape_6": (0.4, 0.9, 0.4), # pf coil
            "add_extra_cut_shape_7": (0.9, 0.4, 0.4), # pf coil case
            "add_extra_cut_shape_8": (0.4, 0.9, 0.4), # pf coil
            "add_extra_cut_shape_9": (0.9, 0.4, 0.4), # pf coil case
            "extra_intersect_shapes": (0.1, 0.1, 0.4), # divertor lower
            
        },
        extra_cut_shapes=coils,
        extra_intersect_shapes=[divertor_lower]
    )

# Function to export reactor to PNG
def export_reactor_to_png(reactor, file_path):
    reactor.add(
        cq.Workplane('XZ').text("Paramak", fontsize=200, distance=10
    ).translate((0, 0, -615)), name="watermark")
    show(reactor, screenshot=file_path, interact=False, width=640, height=512, zoom=1.4, bgcolor=(1.0, 1.0, 1.0))
    print(f'written {file_path}')

# Generate reactors with varying radial build values
frame = 0
factors = [1.0, 1.25, 1.5, 1.75, 2.0, 1.75, 1.5, 1.25, 1.0]
for i in range(len(original_radial_build)):
    layer_type, original_value = original_radial_build[i]
    for factor in factors:
        modified_radial_build = original_radial_build.copy()
        modified_radial_build[i] = (layer_type, original_value * factor)
        reactor = create_reactor(modified_radial_build)
        export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
        frame += 1

for modified_n_tf_coils in [original_n_tf_coils, original_n_tf_coils -1 , original_n_tf_coils -2, original_n_tf_coils-3, original_n_tf_coils-2, original_n_tf_coils-1,original_n_tf_coils]:
    reactor = create_reactor(n_tf_coils=modified_n_tf_coils)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1

for modified_coil_height_factor in [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1, 1]:
    reactor = create_reactor(coil_height_factor=modified_coil_height_factor)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1

for factor in factors:
    modified_divertor_thickness = original_divertor_thickness * factor
    reactor = create_reactor(divertor_thickness=modified_divertor_thickness)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1

for factor in factors:
    modified_elongation = original_elongation * factor
    reactor = create_reactor(elongation=modified_elongation)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1

for modified_triangularity in [0.55, 0.3667, 0.1833, 0.0, -0.1833, -0.3667, -0.55, -0.3667, -0.1833, 0.0, 0.1833, 0.3667, 0.55]:
    reactor = create_reactor(triangularity=modified_triangularity)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1


os.system('ffmpeg -r 10 -i spherical_tokamak_frame_%3d.png -c:v libx264 -r 30 -pix_fmt yuv420p spherical_tokamak_animation.mp4')
