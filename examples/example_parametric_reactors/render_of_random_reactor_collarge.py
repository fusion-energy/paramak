# This examples creates a 3 by 3 grid of random reactor renders and saves
# them as a png image

import math

# to run this example you will need all of the following packages installed
import matplotlib.pyplot as plt
import numpy as np
import paramak
import pyrender
import trimesh


def create_reactor_renders(
    render_number,
    inner_blanket_radius,
    blanket_thickness,
    blanket_height,
    lower_blanket_thickness,
    upper_blanket_thickness,
    blanket_vv_gap,
    number_of_images_in_x,
    number_of_images_in_y,
):

    # creates a reactor from the input arguments
    my_reactor = paramak.FlfSystemCodeReactor(
        rotation_angle=180,
        inner_blanket_radius=inner_blanket_radius,
        blanket_thickness=blanket_thickness,
        blanket_height=blanket_height,
        lower_blanket_thickness=lower_blanket_thickness,
        upper_blanket_thickness=upper_blanket_thickness,
        blanket_vv_gap=blanket_vv_gap,
        upper_vv_thickness=10,
        vv_thickness=10,
        lower_vv_thickness=10,
    )

    # saves the reactor geometry as separate stl files
    my_reactor.export_stl()

    # assigns colours to each stl file
    stl_files_with_colors = {
        "blanket.stl": (255, 255, 0),
        "vacuum_vessel.stl": (128, 128, 128),
        "upper_blanket.stl": (255, 255, 0),
        "lower_blanket.stl": (255, 255, 0),
        "lower_vacuum_vessel.stl": (128, 128, 128),
        "upper_vacuum_vessel.stl": (128, 128, 128),
    }

    scene = pyrender.Scene()

    # for each stl file and color combination
    for key, value in stl_files_with_colors.items():
        trimesh_obj = trimesh.load(key)
        trimesh_obj.visual.vertex_colors = value
        trimesh_obj.visual

        render_mesh = pyrender.Mesh.from_trimesh(trimesh_obj, smooth=False)
        scene.add(render_mesh)

    camera = pyrender.camera.PerspectiveCamera(yfov=math.radians(90.0))  # aspectRatio=2.0 could be added here

    # sets the position of the camera using a matrix
    cam = 2**-0.5
    camera_pose = np.array([[1, 0, 0, 0], [0, cam, -cam, -350], [0, cam, cam, 350], [0, 0, 0, 1]])

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


# creates a blank figure for populating with subplots
plt.figure()

# loops through adding a random reactor render to the figure with each iteration
for i in range(4 * 3):
    create_reactor_renders(
        render_number=i,
        number_of_images_in_x=4,
        number_of_images_in_y=3,
        inner_blanket_radius=np.random.uniform(low=50, high=90),
        blanket_thickness=np.random.uniform(low=50, high=140),
        blanket_height=np.random.uniform(low=400, high=550),
        lower_blanket_thickness=np.random.uniform(low=20, high=70),
        upper_blanket_thickness=np.random.uniform(low=20, high=70),
        blanket_vv_gap=np.random.uniform(low=10, high=90),
    )

# saves the plot
plt.savefig("render.png", dpi=200)
