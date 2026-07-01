import paramak
import cadquery as cq

# Create lower divertor shape
points = [(300, -700), (300, 0), (400, 0), (400, -700)]
divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)
divertor_lower.name = "divertor"  # We can directly assign the name for any cadquery shape, which will be used in extra_intersect_shapes().

'''
For extra_cut_shapes,
these shapes already have a default name, but you can also provide a custom name, which will be used by extra_cut_shapes().
If there are multiple TF coils, PF coils, or any other shapes, you should pass the base name of the shape to extra_cut_shapes().
for example:
    if name="toroidal_coil" is specified for toroidal_field_coil_rectangle() and two separate TF coils are created,
    their names will automatically become toroidal_coil_1 and toroidal_coil_2.
'''

# Create toroidal field coils
tf = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point=(10, 520),
    vertical_mid_point=(860, 0),
    thickness=50,
    distance=40,
    rotation_angle=180,
    with_inner_leg=True,
    azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
    name="toroidal_coil"  # Default name "toroidal_field_coil"
)

extra_cut_shapes = [tf]

# creates pf coil
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(730, 370), (810, 235), (810, -235), (730, -370)]
):
    extra_cut_shapes.append(
        paramak.poloidal_field_coil(
            height=height, 
            width=width, 
            center_point=center_point, 
            rotation_angle=180, 
            name="poloidal_coil"  # Default name "poloidal_field_coil"
        )
    )
    extra_cut_shapes.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=180,
            center_point=center_point,
            name="poloidal_coil_case",  # Default name "poloidal_field_coil_case"
        )
    )

'''
For tokamak,
We need to define names only for the radial_build.
If no names are provided, default names will be assigned automatically as layer_1, layer_2, layer_3, and so on. 
We may also define names for only some layers; any unnamed layers will receive default names.
Now, if we define a SOLID layer only on one side of the plasma, then this solid does not revolve around the plasma.
Suppose we have a radial build like this:
    "7-SOLID-inner-layer, plasma, 5-SOLID-outer-layer"
    Here, there are 2 extra layers on the inner side of plasma. So, the first 2 layers('2'+5, plasma, 5) of inner-layer won't revolve around the plasma,
    but the remaining 5 SOLID layer will revolve around the plasma.
    In the example below, "CS Coil" and "TF Coil" layer won't revolve around the plasma.
Names can be defined for both the inner and outer portions of a revolved layer. However, the inner and outer portions are combined into a single solid, 
so only one name is assigned to the resulting solid. 
The naming rules are:
    1. If both the inner and outer layers have names, the name of the inner layer is used.
    2. If the inner layer is unnamed and the outer layer has a name, the outer layer's name is used.
    3. If neither layer has a name, the default layer name is used.
For example:
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30, "CS Coil"),         # layer_1
        (paramak.LayerType.SOLID, 50, "TF Coil"),         # layer_2
        (paramak.LayerType.SOLID, 100, "Vacuum Vessel"),  # layer_6
        (paramak.LayerType.SOLID, 60, "Blanket-1"),       # layer_5
        (paramak.LayerType.SOLID, 20, "First Wall"),      # layer_4
        (paramak.LayerType.SOLID, 10, "W Armor"),         # layer_3
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),                  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),                    # layer_3
        (paramak.LayerType.SOLID, 20),                    # layer_4
        (paramak.LayerType.SOLID, 60, "Blanket-2"),       # layer_5
        (paramak.LayerType.SOLID, 100),                   # layer_6
    ]

    In this example, names are defined for all inner-side layers. Therefore, the blanket solid is assigned the name "Blanket-1".
    If the inner blanket layer is left unnamed: (paramak.LayerType.SOLID, 60)
    then the blanket solid is assigned the name "Blanket-2" because the outer blanket layer has a defined name.
    Similarly, if no name is provided for the first wall layer on either the inner or outer side, 
    the resulting solid is assigned the default name "layer_4", which corresponds to the default name of that layer.
'''

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.SOLID, 50, "CS Coil"),
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 10, "Vacuum Vessel"),
        (paramak.LayerType.SOLID, 60, "Blanket"),
        (paramak.LayerType.SOLID, 60, "First Wall"),
        (paramak.LayerType.SOLID, 10, "W Armor"),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 650),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
    ],
    triangularity=0.55,
    rotation_angle=180,
    extra_cut_shapes=extra_cut_shapes,
    extra_intersect_shapes=[divertor_lower],
)

'''
We can obtain the names of all shapes in a reactor using the `my_reactor.names()` function.
Some shapes may contain multiple solids. In such cases, use the `my_reactor.split_solids()` function before calling `my_reactor.names()` to obtain the names of all solids individually and in sequence.
For example, a toroidal field coil set may consist of eight separate TF coils. In this case, it is recommended to use `my_reactor.split_solids()` to inspect the names of all resulting solids.
If we intend to convert the reactor geometry to a DAGMC mesh using `cad_to_dagmc()`, we should not keep `my_reactor.split_solids()` in the final workflow. 
The purpose of `split_solids()` is primarily to inspect and identify individual solid names.

A recommended workflow is:
    1. Call `my_reactor.split_solids()`.
    2. Use `my_reactor.names()` to inspect the generated solid names.
    3. Assign or verify the desired material tags and names.
    4. Remove or comment out the `my_reactor.split_solids()` call.
    5. Rerun the script and generate the final DAGMC mesh using `cad_to_dagmc()`.

This is recommended because `split_solids()` separates a shape into multiple individual solids. While this is useful for inspecting names, it is generally not desirable when generating the final DAGMC geometry.
'''
my_reactor = my_reactor.split_solids()
print(my_reactor.names())

# We can save the reactor with names in a step file, which can be used for CAD visualization.
my_reactor.save("tokamak_names.step")
print("Saved as tokamak_names.step")

'''
Now we can define the material tags for the mesh using the names of the shapes.
'''