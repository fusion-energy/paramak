# This examples creates a 3 by 3 grid of random reactor renders and saves
# them as a png image

import math
import random

# to run this example you will need all of the following packages installed
import matplotlib.pyplot as plt
import numpy as np
import paramak
import pyrender
import trimesh


def generate_random_reactor():
    all_reactors = [
        paramak.BallReactor(),
        paramak.CenterColumnStudyReactor(),
        paramak.EuDemoFrom2015PaperDiagram(),
        paramak.FlfSystemCodeReactor(),
        paramak.IterFrom2020PaperDiagram(),
        paramak.SegmentedBlanketBallReactor(),
        paramak.SingleNullBallReactor(),
        paramak.SingleNullSubmersionTokamak(),
        paramak.SparcFrom2020PaperDiagram(),
        paramak.SubmersionTokamak(),
    ]

    my_reactor = random.choice(all_reactors)

    print(my_reactor)

    input_variables = my_reactor.input_variable_names
    my_reactor.rotation_angle = 180

    for input_var in [
        "graveyard_size",
        "graveyard_offset",
        "largest_shapes",
        "elongation",
        "triangularity",
        "rotation_angle",
    ]:
        try:
            input_variables.remove(input_var)
        except ValueError:
            pass

    print(my_reactor.__dict__, "\n\n")

    for input_arg in my_reactor.input_variables:
        if input_arg in my_reactor.__dict__:
            if isinstance(my_reactor.__dict__[input_arg], float):
                rand_scale = random.uniform(0.8, 1.2)
                setattr(my_reactor, input_arg, my_reactor.__dict__[input_arg] * rand_scale)

    return my_reactor


def create_reactor_renders(render_number, number_of_images_in_x, number_of_images_in_y, reactor):

    # saves the reactor geometry as separate stl files
    reactor.export_stl()

    # assigns colours to each stl file

    scene = pyrender.Scene()

    # for each stl file and color combination
    for entry in reactor.shapes_and_components:
        trimesh_obj = trimesh.load(entry.name + ".stl")
        trimesh_obj.visual.vertex_colors = entry.color

        render_mesh = pyrender.Mesh.from_trimesh(trimesh_obj, smooth=False)
        scene.add(render_mesh)

    camera = pyrender.camera.PerspectiveCamera(yfov=math.radians(90.0))  # aspectRatio=2.0 could be added here

    # sets the position of the camera using a matrix
    cam = 2**-0.5
    camera_pose = np.array([[1, 0, 0, 0], [0, cam, -cam, -650], [0, cam, cam, 650], [0, 0, 0, 1]])

    # adds a camera and a point light source at the same location
    scene.add(camera, pose=camera_pose)
    light = pyrender.PointLight(color=np.ones(3), intensity=300000.0)
    scene.add(light, pose=camera_pose)

    # renders the scene
    my_render = pyrender.OffscreenRenderer(1000, 1000)
    color, depth = my_render.render(scene)

    # adds the render to the plot as a subplot in the correct location
    plt.subplot(number_of_images_in_y, number_of_images_in_x, render_number + 1)
    plt.axis("off")
    plt.imshow(color)
    return reactor.reactor_hash_value


# creates a blank figure for populating with subplots
plt.figure()

# loops through adding a random reactor render to the figure with each iteration
for i in range(4 * 3):
    reactor_hash_value = create_reactor_renders(
        render_number=i,
        number_of_images_in_x=4,
        number_of_images_in_y=3,
        reactor=generate_random_reactor(),
    )

# saves the plot
plt.savefig("render_random_reactors.png", dpi=200)
