import os
import shutil

import cadquery as cq
import numpy as np
from cadquery.occ_impl.assembly import toVTKAssy
from PIL import Image
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkWindowToImageFilter
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer  # noqa: F401 loads the OpenGL backend

import paramak

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
    divertor_thickness=original_divertor_thickness,
    n_modules=None,
    segment_blanket=False,
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

    # optionally splits the first wall (layer_3) into tiles, and optionally the
    # blanket (layer_4) into modules with the same segments so they line up
    poloidal_build = None
    module_colors = {}
    plasma_color = (1., 0.7, 0.8, 0.6)
    if n_modules is not None:
        module_gap = 15  # gap between neighbouring segments
        arc_length = paramak.spherical_poloidal_arc_length(
            radial_build, elongation=elongation, triangularity=triangularity
        )
        module_length = (arc_length - n_modules * module_gap) / n_modules
        modules = [("module", module_length), ("gap", module_gap)] * n_modules
        poloidal_build = [None, modules, modules if segment_blanket else None, None]
        # alternating colors so neighbouring segments can be told apart
        layer_colors = {"layer_3": [(0.1, 0.1, 0.9), (0.5, 0.75, 1.0)], "layer_4": [(0.4, 0.4, 0.8), (0.75, 0.75, 0.95)]}
        for layer_name, colors in layer_colors.items():
            for i in range(n_modules):
                name = f"{layer_name}_module" if n_modules == 1 else f"{layer_name}_module_{i + 1}"
                module_colors[name] = colors[i % 2]
        # a more transparent plasma so the segments behind it can be seen
        plasma_color = (1., 0.7, 0.8, 0.3)

    return paramak.spherical_tokamak_from_plasma(
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
        extra_intersect_shapes=[divertor_lower]
    )

ZOOM = 1.2
WATERMARK_Z = -615


# Rendering is done with VTK directly (using the cadquery assembly to VTK
# conversion) to control the anti aliasing, lighting and camera framing
def render_png(reactor, file_path, bgcolor, zoom):
    renderer = vtkRenderer()
    for actor in toVTKAssy(reactor, edges=True, linewidth=1, tolerance=1e-3):
        actor.GetProperty().SetAmbient(0.1)
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(100)
        renderer.AddActor(actor)
    renderer.SetBackground(*bgcolor)
    renderer.SetUseFXAA(True)
    window = vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(640, 512)
    window.AddRenderer(renderer)
    camera = renderer.GetActiveCamera()
    camera.Roll(-35)
    camera.Elevation(-60)
    renderer.ResetCamera()  # fits the reactor in the view after rotating
    camera.Zoom(zoom)
    renderer.ResetCameraClippingRange()
    window.Render()
    grab = vtkWindowToImageFilter()
    grab.SetInput(window)
    grab.ReadFrontBufferOff()
    grab.Update()
    writer = vtkPNGWriter()
    writer.SetFileName(file_path)
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()


# Saves a frame on a white background (used for the mp4) and a frame with a
# transparent background (used for the webm, so the animation also works on
# dark pages)
def export_reactor_to_png(reactor, file_path, alpha_file_path):
    # the watermark goes below the reactor, lower than usual if the reactor is tall
    watermark_z = min(WATERMARK_Z, reactor.toCompound().BoundingBox().zmin - 250)
    reactor.add(
        cq.Workplane('XZ').text("Paramak", fontsize=200, distance=10
    ).translate((0, 0, watermark_z)), name="watermark", color=cq.Color(0.4, 0.4, 0.4))
    # the difference between renders on black and white backgrounds gives the
    # transparency of each pixel (including anti aliased edges and the partly
    # transparent plasma), the view is zoomed out if the reactor touches the edge
    zoom = ZOOM
    while True:
        render_png(reactor, alpha_file_path, (0.0, 0.0, 0.0), zoom)
        render_png(reactor, file_path, (1.0, 1.0, 1.0), zoom)
        on_black = np.asarray(Image.open(alpha_file_path).convert("RGB"), dtype=float)
        on_white = np.asarray(Image.open(file_path).convert("RGB"), dtype=float)
        alpha = np.clip(1 - (on_white - on_black).mean(axis=2) / 255, 0, 1)
        border = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
        if border.max() < 0.05 or zoom < 0.8:
            break
        zoom *= 0.95
    rgb = on_black / np.maximum(alpha, 1e-6)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(alpha_file_path)
    print(f'written {file_path} and {alpha_file_path}')


# Generate reactors with varying radial build values
frame = 0
factors = [1.0, 1.25, 1.5, 1.75, 2.0, 1.75, 1.5, 1.25, 1.0]
for i in range(len(original_radial_build)):
    layer_type, original_value = original_radial_build[i]
    for factor in factors:
        modified_radial_build = original_radial_build.copy()
        modified_radial_build[i] = (layer_type, original_value * factor)
        reactor = create_reactor(modified_radial_build)
        export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
        frame += 1

for modified_n_tf_coils in [original_n_tf_coils, original_n_tf_coils -1 , original_n_tf_coils -2, original_n_tf_coils-3, original_n_tf_coils-2, original_n_tf_coils-1,original_n_tf_coils]:
    reactor = create_reactor(n_tf_coils=modified_n_tf_coils)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    frame += 1

for modified_coil_height_factor in [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1, 1]:
    reactor = create_reactor(coil_height_factor=modified_coil_height_factor)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    frame += 1

for factor in factors:
    modified_divertor_thickness = original_divertor_thickness * factor
    reactor = create_reactor(divertor_thickness=modified_divertor_thickness)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    frame += 1

for factor in factors:
    modified_elongation = original_elongation * factor
    reactor = create_reactor(elongation=modified_elongation)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    frame += 1

for modified_triangularity in [0.55, 0.3667, 0.1833, 0.0, -0.1833, -0.3667, -0.55, -0.3667, -0.1833, 0.0, 0.1833, 0.3667, 0.55]:
    reactor = create_reactor(triangularity=modified_triangularity)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    frame += 1

# the segmentation frames are each shown for three frames so these sequences play more slowly
segmentation_frame_repeats = 3

# first wall tiles only
for modified_n_modules in [None, 2, 4, 6, 8, 10, 12, 14, 16, 16, 16, 14, 12, 10, 8, 6, 4, 2, None]:
    reactor = create_reactor(n_modules=modified_n_modules)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    for repeat in range(1, segmentation_frame_repeats):
        shutil.copy(f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_frame_{frame + repeat:03d}.png')
        shutil.copy(f'spherical_tokamak_alpha_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame + repeat:03d}.png')
    frame += segmentation_frame_repeats

# first wall tiles and blanket modules with the same poloidal segments
for modified_n_modules in [None, 2, 3, 4, 5, 6, 7, 8, 8, 8, 7, 6, 5, 4, 3, 2, None]:
    reactor = create_reactor(n_modules=modified_n_modules, segment_blanket=True)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame:03d}.png')
    for repeat in range(1, segmentation_frame_repeats):
        shutil.copy(f'spherical_tokamak_frame_{frame:03d}.png', f'spherical_tokamak_frame_{frame + repeat:03d}.png')
        shutil.copy(f'spherical_tokamak_alpha_frame_{frame:03d}.png', f'spherical_tokamak_alpha_frame_{frame + repeat:03d}.png')
    frame += segmentation_frame_repeats

# mp4 on a white background, and webm with a transparent background for
# browsers that support it
os.system('ffmpeg -y -r 10 -i spherical_tokamak_frame_%03d.png -c:v libx264 -r 30 -pix_fmt yuv420p spherical_tokamak_animation.mp4')
os.system('ffmpeg -y -r 10 -i spherical_tokamak_alpha_frame_%03d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 32 -r 30 spherical_tokamak_animation.webm')
