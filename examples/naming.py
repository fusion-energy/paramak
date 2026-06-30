import paramak
import cadquery as cq

# Create lower divertor shape
points = [(300, -700), (300, 0), (400, 0), (400, -700)]
divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)
divertor_lower.name = "divertor"  # We can directly assign the name for any cadquery shape, which will be used in extra_intersect_shapes().

'''
For extra_cut_shapes,
these shapes already has a default name, but we can also pass a custom name to the shape, which will be used in extra_cut_shapes().
If we have multiple tf coil or pf coil or any other shape, we need to pass the base name of the shape to extra_cut_shapes().
for example:
    if we define name = "toroidal_coil" for toroidal_field_coil_rectangle(),
    and we have 2 separate tf coils, then the names of the shapes will be autometically defined as "toroidal_coil_1" and "toroidal_coil_2".
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
we need to define names only for the radial_build.
If we don't define names for any layer then the default name will be assigned as "layer_1", "layer_2", "layer_3" and so on.
We can also define names for some layers and the rest of the layers will be assigned default names.
Now, if we define a SOLID layer only in one side of the plasma, then this solid does not revolve around the plasma.
Suppose we have a radial build like this:
    "7-SOLID-inner-layer, plasma, 5-SOLID-outer-layer"
    here, there are 2 extra layers on the inner side of plasma. So, the first 2 layers('2'+5, plasma, 5) of inner-layer won't revolve around the plasma,
    but the remaining 5 SOLID layer will revolve around the plasma.
    In the example below, "CS Coil" and "TF Coil" layer won't revolve around the plasma.
We can define names for the revolved layers on both inner and outer layers, but the inner and outer layers will create one single solid, 
so there will be only one name for the solid. If we define names for the both layers, then the name of the inner layer will be used for the solid. 
If we don't define any name for the inner layer, then the name of the outer layer will be used for the solid.
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

    Here, we have defined names for all the inner build layers.
    The balnket layer will be assigned the name "Blanket-1".
    But suppose if we don't define any name for the inner blanket layer like (paramak.LayerType.SOLID, 60), 
    then the name of the blanket layer will be assigned as "Blanket-2" as we have defined the outer layer name, and
    the rest of the layers will be assigned given names.
    Again suppose if we don't define any name for first wall layer on both inner and outer side, then the name of the first wall layer will be assigned as "layer_4", 
    which is the default name for the first wall layer.
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
We can get all the names of the shapes in the reactor using my_reactor.names() function.
If we have shapes which contains multiple soilds, then we need to use the my_reactor.split_solids() function to get all the names sequentially.
Like there can be 8 separate TF coils. It is recommended to use my_reactor.split_solids() function to get all the names of the shapes in the reactor.
If we want to convert the reactor to a DAGMC mesh using cad_to_dagmc(), then we should not use my_reactor.split_solids() function.
After getting the names, we should remove or comment the my_reactor.split_solids() function, as it will create multiple solids for each shape, which is not recommended 
and then rerun the script to generate the final mesh.
'''
my_reactor = my_reactor.split_solids()
print(my_reactor.names())

# We can save the reactor with names in a step file, which can be used for CAD visualization.
my_reactor.save("tokamak_names.step")
print("Saved as tokamak_names.step")

'''
Now we can define the material tags for the mesh using the names of the shapes.
'''