import os

import cadquery as cq
import numpy as np
from cadquery.vis import show
from matplotlib.path import Path
from PIL import Image

import paramak
from paramak.workplanes.toroidal_field_coil_princeton_d import find_points

original_radial_build=[
    (paramak.LayerType.GAP, 40),
    # (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 10),
]
original_elongation=4
original_triangularity=0.55
original_rotation_angle=180
original_n_tf_coils = 8
original_coil_height_factor = 1
original_divertor_thickness = 55

def blanket_outer_surface(radial_build, major_radius, minor_radius, elongation, triangularity, num_points=360):
    """R and Z points on the outer surface of the blanket, found by offsetting
    the plasma surface along its normal by the total blanket thickness."""
    plasma_index = [layer[0] for layer in radial_build].index(paramak.LayerType.PLASMA)
    outboard_thickness = sum(layer[1] for layer in radial_build[plasma_index + 1 :])
    number_of_outboard_layers = len(radial_build) - plasma_index - 1
    inboard_thickness = sum(layer[1] for layer in radial_build[plasma_index - number_of_outboard_layers : plasma_index])

    theta = np.linspace(0, 2 * np.pi, num_points)
    R = major_radius + minor_radius * np.cos(theta + triangularity * np.sin(theta))
    Z = elongation * minor_radius * np.sin(theta)
    dR = np.gradient(R, theta)
    dZ = np.gradient(Z, theta)
    norm = np.hypot(dR, dZ)
    # the thickness varies from the outboard value at the outboard midplane
    # to the inboard value at the top, inboard midplane and bottom
    thickness = np.interp(
        np.degrees(theta), [0, 90, 180, 270, 360],
        [outboard_thickness, inboard_thickness, inboard_thickness, inboard_thickness, outboard_thickness],
    )
    return R + thickness * dZ / norm, Z - thickness * dR / norm


def tf_coil_outer_radius(blanket_points, r1, thickness, start_r2, clearance=20, step=10):
    """Finds the smallest Princeton-D outer radius (r2) at or above start_r2
    whose inner profile encloses the blanket with some clearance. This avoids
    the coils overlapping the blanket, for example with negative triangularity."""
    R, Z = blanket_points
    theta = np.linspace(0, 2 * np.pi, 36, endpoint=False)
    # points around each blanket point so the clearance is kept in every direction
    test_points = np.column_stack(
        [
            (R[:, None] + clearance * np.cos(theta)).ravel(),
            (Z[:, None] + clearance * np.sin(theta)).ravel(),
        ]
    )
    test_points = test_points[test_points[:, 0] > r1 + thickness]
    r2 = start_r2
    while True:
        _, _, inner_points, _ = find_points(r1, r2, thickness, vertical_displacement=0)
        if Path(inner_points).contains_points(test_points).all():
            return r2
        r2 += step


# Function to create a reactor with modified radial build
def create_reactor(
    radial_build=original_radial_build,
    elongation = original_elongation,
    triangularity = original_triangularity,
    n_tf_coils = original_n_tf_coils,
    coil_height_factor = original_coil_height_factor,
    divertor_thickness=original_divertor_thickness,
    n_modules=None,
    segment_blanket=False,
):
    
    reactor_diameter = sum([layer[1] for layer in radial_build])
    minor_radius = radial_build[6][1]/2
    major_radius = sum([layer[1] for layer in radial_build][:6])+minor_radius

    theta = 3 * np.pi / 2
    divertor_radius = major_radius + minor_radius * np.cos(theta + triangularity * np.sin(theta))
    outer_blanket_thickness = sum([layer[1] for layer in radial_build[2:6]])
    pf_radial_position = divertor_radius + outer_blanket_thickness + 40
    reactor_height = 0.5*elongation * radial_build[6][1] + outer_blanket_thickness

    # makes a rectangle that overlaps the lower blanket under the plasma
    # the intersection of this and the layers will form the lower divertor
    points = [(divertor_radius-divertor_thickness, -2000), (divertor_radius-divertor_thickness, 2000), (divertor_radius+divertor_thickness, 0), (divertor_radius+divertor_thickness, -700)]
    divertor = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)


    tf_r2 = tf_coil_outer_radius(
        blanket_outer_surface(radial_build, major_radius, minor_radius, elongation, triangularity),
        r1=10,
        thickness=40,
        start_r2=reactor_diameter + 30,
    )
    tf_coils = paramak.toroidal_field_coil_princeton_d(
        r2=tf_r2,
        r1=10,
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
            (pf_radial_position, reactor_height),
            # outboard coils sit outside the tf coil outer leg
            (tf_r2+40+15+50/2, 150*coil_height_factor),
            (tf_r2+40+15+50/2, -150*coil_height_factor),
            (pf_radial_position, -reactor_height)
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

    # optionally splits the first wall (layer_2) into tiles, and optionally
    # the blanket (layer_3) into modules that line up with the first wall tiles
    poloidal_build = None
    module_colors = {}
    plasma_color = (1., 0.7, 0.8, 0.6)
    if n_modules is not None:
        module_gap = 15
        arc_lengths = paramak.poloidal_arc_lengths(radial_build, elongation=elongation, triangularity=triangularity)
        module_arc_length = (arc_lengths[1] - n_modules * module_gap) / n_modules
        poloidal_build = paramak.aligned_poloidal_build(
            radial_build,
            segments=[("module", module_arc_length), ("gap", module_gap)] * n_modules,
            layers=[1, 2] if segment_blanket else [1],
            elongation=elongation,
            triangularity=triangularity,
        )
        # alternating colors so neighbouring segments can be told apart
        layer_colors = {"layer_2": [(0.75, 0.95, 0.75), (0.2, 0.5, 0.2)], "layer_3": [(0.1, 0.1, 0.9), (0.5, 0.75, 1.0)]}
        for layer_name, colors in layer_colors.items():
            for i in range(n_modules):
                name = f"{layer_name}_module" if n_modules == 1 else f"{layer_name}_module_{i + 1}"
                module_colors[name] = colors[i % 2]
        # a more transparent plasma so the segments behind it can be seen
        plasma_color = (1., 0.7, 0.8, 0.3)

    return paramak.tokamak_from_plasma(
        radial_build=radial_build,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=180,
        poloidal_build=poloidal_build,
        colors={
            **module_colors,
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": plasma_color,
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
            "toroidal_field_coil_1": (0.6, 0.3, 0.4),
            "poloidal_field_coil_2": (0.4, 0.9, 0.4),
            "poloidal_field_coil_case_3": (0.9, 0.4, 0.4),
            "poloidal_field_coil_4": (0.4, 0.9, 0.4),
            "poloidal_field_coil_case_5": (0.9, 0.4, 0.4),
            "poloidal_field_coil_6": (0.4, 0.9, 0.4),
            "poloidal_field_coil_case_7": (0.9, 0.4, 0.4),
            "poloidal_field_coil_8": (0.4, 0.9, 0.4),
            "poloidal_field_coil_case_9": (0.9, 0.4, 0.4),
            "extra_intersect_shapes_1": (0.1, 0.1, 0.4), # divertor lower
        },
        extra_cut_shapes=coils,
        extra_intersect_shapes=[divertor]
    )

# Function to export reactor to a PNG with a transparent background
def export_reactor_to_png(reactor, file_path):
    reactor.add(
        cq.Workplane('XZ').text("Paramak", fontsize=200, distance=10
    ).translate((0, 0, -1215)), name="watermark", color=cq.Color(0.5, 0.5, 0.5))
    # renders on a black and a white background, the difference between the
    # two gives the transparency of each pixel (including anti aliased edges
    # and the partly transparent plasma)
    renders = []
    for bgcolor in [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]:
        show(reactor, screenshot=file_path, interact=False, width=640, height=512, zoom=1.25,
             bgcolor=bgcolor, gradient=False, trihedron=False)
        renders.append(np.asarray(Image.open(file_path).convert("RGB"), dtype=float))
    on_black, on_white = renders
    alpha = np.clip(1 - (on_white - on_black).mean(axis=2) / 255, 0, 1)
    rgb = on_black / np.maximum(alpha, 1e-6)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(file_path)
    print(f'written {file_path}')


# Generate reactors with varying radial build values
frame = 0
factors = [1.0, 1.25, 1.5, 1.75, 2.0, 1.75, 1.5, 1.25, 1.0]
for i in range(len(original_radial_build)):
    layer_type, original_value = original_radial_build[i]
    for factor in factors:
        modified_radial_build = original_radial_build.copy()
        modified_radial_build[i] = (layer_type, original_value * factor)
        reactor = create_reactor(modified_radial_build, original_elongation, original_triangularity, original_n_tf_coils, original_coil_height_factor)
        export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
        frame += 1

for modified_n_tf_coils in [original_n_tf_coils, original_n_tf_coils -1 , original_n_tf_coils -2, original_n_tf_coils-3, original_n_tf_coils-2, original_n_tf_coils-1,original_n_tf_coils]:
    reactor = create_reactor(n_tf_coils=modified_n_tf_coils)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

for modified_coil_height_factor in [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1, 1]:
    reactor = create_reactor(coil_height_factor=modified_coil_height_factor)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

for factor in factors:
    modified_divertor_thickness = original_divertor_thickness * factor
    reactor = create_reactor(divertor_thickness=modified_divertor_thickness)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

for factor in [1.0, 0.9, 0.8, 0.7, 0.8, 0.9, 1.0]:
    modified_elongation = original_elongation * factor
    reactor = create_reactor(elongation=modified_elongation)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

for modified_triangularity in [0.55, 0.3667, 0.1833, 0.0, -0.1833, -0.3667, -0.55, -0.3667, -0.1833, 0.0, 0.1833, 0.3667, 0.55]:
    reactor = create_reactor(triangularity=modified_triangularity)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

# first wall tiles only
for modified_n_modules in [None, 2, 4, 6, 8, 10, 12, 14, 16, 16, 16, 14, 12, 10, 8, 6, 4, 2, None]:
    reactor = create_reactor(n_modules=modified_n_modules)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

# first wall tiles and blanket modules with the same poloidal segments
for modified_n_modules in [None, 2, 3, 4, 5, 6, 7, 8, 8, 8, 7, 6, 5, 4, 3, 2, None]:
    reactor = create_reactor(n_modules=modified_n_modules, segment_blanket=True)
    export_reactor_to_png(reactor, f'tokamak_frame_{frame:03d}.png')
    frame += 1

# animated webp keeps the transparent background, so the animation works on light and dark pages
os.system('ffmpeg -framerate 10 -i tokamak_frame_%03d.png -c:v libwebp_anim -lossless 0 -q:v 80 -loop 0 tokamak_animation.webp')
