""" This example creates a rendering of a reactor"""


import os
import numpy as np
import paramak
import pyrender
import math
from PIL import Image
import trimesh


def make_render(rgb_colours, shapes, filename='render.png'):
    """renders a collection of shapes"""

    scene = pyrender.Scene(ambient_light=np.array([0.1, 0.1, 0.1, 1.0]))

    for rgb_colour, entry in zip(rgb_colours, shapes):
        entry.export_stl("temp.stl", tolerance=0.001)

        tm = trimesh.load("temp.stl")

        tm.visual.vertex_colors = rgb_colour

        render_mesh = pyrender.Mesh.from_trimesh(tm)
        scene.add(render_mesh)

    os.system('rm temp.stl')

    # sets the field of view (fov) and the aspect ratio of the image
    camera = pyrender.camera.PerspectiveCamera(
        yfov=math.radians(90.0), aspectRatio=2.0
    )

    # sets the position of the camera using a matrix, to zoom out increase 700
    c = 2 ** -0.5
    camera_pose = np.array(
        [[1, 0, 0, 0], [0, c, -c, -700], [0, c, c, 700], [0, 0, 0, 1]]
    )
    scene.add(camera, pose=camera_pose)

    # adds some basic lighting to the scene
    light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.0)
    scene.add(light, pose=camera_pose)

    # Render the scene
    renderer = pyrender.OffscreenRenderer(1000, 500)
    colours, depth = renderer.render(scene)

    image = Image.fromarray(colours, "RGB")

    image.save(filename, "PNG")


if __name__ == "__main__":
    # make a reactor
    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=1,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=3,
        blanket_radial_thickness=100,
        blanket_rear_wall_radial_thickness=3,
        elongation=2.75,
        triangularity=0.5,
        number_of_tf_coils=16,
        rotation_angle=180,
    )
    # render the reactor shape objects
    make_render([(255, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255),
                 (255, 255, 0), (0, 255, 255), (192, 192, 192)],
                my_reactor.shapes_and_components)
