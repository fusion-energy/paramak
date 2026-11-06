"""Makes the reactors from papers animation on the front page of the
documentation. The SPARC, ITER and EU DEMO reactors are shown one after the
other, each built with a rotation_angle that sweeps from 1 to 360 degrees and
back again.

This writes an mp4 on a white background and a webm with a transparent
background (so the animation also works on dark pages), in the same format as
the tokamak and spherical tokamak animations. The frames are built and
rendered in parallel processes. Requires Pillow, VTK (installed with
CadQuery) and ffmpeg.
"""

import os
import shutil
from concurrent.futures import ProcessPoolExecutor

import cadquery as cq
import numpy as np
from cadquery.occ_impl.assembly import toVTKAssy
from PIL import Image
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkWindowToImageFilter
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer  # noqa: F401 loads the OpenGL backend

import paramak

REACTORS = {
    "sparc": paramak.sparc_from_2020_paper,
    "iter": paramak.iter_from_2020_paper,
    "eu_demo": paramak.eu_demo_from_2015_paper,
}
ANGLES = [1, 5] + list(range(10, 361, 10))
PAUSE_FRAMES = 10  # number of frames to hold the fully built and the thinnest reactors
ZOOM = 1.2


def add_watermark(reactor, z):
    reactor.add(
        cq.Workplane("XZ").text("Paramak", fontsize=reactor.major_radius * 0.6, distance=10).translate((0, 0, z)),
        name="watermark",
        color=cq.Color(0.4, 0.4, 0.4),
    )


def camera_settings(label):
    """The watermark height and the bounds of the complete 360 degree reactor
    with its watermark, used to keep the camera still while the rotation angle
    changes."""
    reactor = REACTORS[label](rotation_angle=360)
    bb = reactor.toCompound().BoundingBox()
    # low enough to stay visible below the near side of the complete reactor
    watermark_z = bb.zmin - bb.xmax * 0.9
    add_watermark(reactor, watermark_z)
    bb = reactor.toCompound().BoundingBox()
    return watermark_z, (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)


# Rendering is done with VTK directly (using the cadquery assembly to VTK
# conversion) to control the anti aliasing, lighting and camera framing
def render_png(reactor, file_path, bgcolor, bounds):
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
    renderer.ResetCamera(bounds)
    camera.Zoom(ZOOM)
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


def frame_paths(label, angle):
    return f"{label}_frame_angle_{angle:03d}.png", f"{label}_alpha_frame_angle_{angle:03d}.png"


def build_and_render(job):
    """Saves a frame on a white background (used for the mp4) and a frame with
    a transparent background (used for the webm)."""
    label, angle, watermark_z, bounds = job
    reactor = REACTORS[label](rotation_angle=angle)
    add_watermark(reactor, watermark_z)
    file_path, alpha_file_path = frame_paths(label, angle)
    # the difference between renders on black and white backgrounds gives the
    # transparency of each pixel (including anti aliased edges and the partly
    # transparent plasma)
    render_png(reactor, alpha_file_path, (0.0, 0.0, 0.0), bounds)
    render_png(reactor, file_path, (1.0, 1.0, 1.0), bounds)
    on_black = np.asarray(Image.open(alpha_file_path).convert("RGB"), dtype=float)
    on_white = np.asarray(Image.open(file_path).convert("RGB"), dtype=float)
    alpha = np.clip(1 - (on_white - on_black).mean(axis=2) / 255, 0, 1)
    rgb = on_black / np.maximum(alpha, 1e-6)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(alpha_file_path)
    print(f"written {file_path} and {alpha_file_path}")


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) // 2)) as executor:
        settings = dict(zip(REACTORS, executor.map(camera_settings, REACTORS)))
        jobs = [(label, angle, *settings[label]) for label in REACTORS for angle in ANGLES]
        list(executor.map(build_and_render, jobs))

    # each reactor in turn builds up to 360 degrees, holds, then goes back down
    # to 1 degree and holds
    sequence = ANGLES + [ANGLES[-1]] * PAUSE_FRAMES + ANGLES[::-1] + [ANGLES[0]] * PAUSE_FRAMES
    frame = 0
    for label in REACTORS:
        for angle in sequence:
            file_path, alpha_file_path = frame_paths(label, angle)
            shutil.copy(file_path, f"frame_{frame:03d}.png")
            shutil.copy(alpha_file_path, f"alpha_frame_{frame:03d}.png")
            frame += 1

    # mp4 on a white background, and webm with a transparent background for
    # browsers that support it
    os.system("ffmpeg -y -r 10 -i frame_%03d.png -c:v libx264 -r 30 -pix_fmt yuv420p paper_reactors_animation.mp4")
    os.system(
        "ffmpeg -y -r 10 -i alpha_frame_%03d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 32 -r 30 "
        "paper_reactors_animation.webm"
    )
