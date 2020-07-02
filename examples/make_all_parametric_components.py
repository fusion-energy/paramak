
rot_angle = 180

from paramak.parametric_shapes import BlanketConstantThickness

shape = BlanketConstantThickness(
    major_radius = 800,
    minor_radius = 400,
    triangularity = 1.2,
    elongation = 0.9,
    thickness = 70,
    start_angle = 30,
    stop_angle = 330,
    offset_from_plasma = 20,
    rotation_angle = rot_angle
)
shape.export_stp('blanket_constant_thickness.stp')


from paramak.parametric_shapes import CenterColumnShieldCylinder

shape = CenterColumnShieldCylinder(
    inner_radius = 80,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_cylinder.stp')


from paramak.parametric_shapes import CenterColumnShieldHyperbola 

shape = CenterColumnShieldHyperbola(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_hyperbola.stp')


from paramak.parametric_shapes import CenterColumnShieldCircular

shape = CenterColumnShieldCircular(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_circular.stp')


from paramak.parametric_shapes import CenterColumnShieldFlatTopHyperbola

shape = CenterColumnShieldFlatTopHyperbola(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    arc_height = 220,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_flat_top_hyperbola.stp')


from paramak.parametric_shapes import CenterColumnShieldFlatTopCircular

shape = CenterColumnShieldFlatTopCircular(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    arc_height = 220,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_flat_top_Circular.stp')


from paramak.parametric_shapes import CenterColumnShieldPlasmaHyperbola

shape = CenterColumnShieldPlasmaHyperbola(
    inner_radius = 150,
    mid_offset = 50,
    edge_offset = 40,
    height = 800,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_plasma_hyperbola.stp')


# from paramak.parametric_shapes import DivertorBlock

# shape = DivertorBlock(
#     major_radius = 800,
#     minor_radius = 400,
#     triangularity = 1.2,
#     elongation = 0.9,
#     thickness = 50,
#     offset_from_plasma = 20,
#     start
# )


from paramak.parametric_shapes import InnerTfCoilsCircular

shape = InnerTfCoilsCircular(
    inner_radius = 25,
    outer_radius = 100,
    number_of_coils = 10,
    gap_size = 5,
    height = 300
)
shape.export_stp('inner_tf_coils_circular.stp')


from paramak.parametric_shapes import InnerTfCoilsFlat

shape = InnerTfCoilsFlat(
    inner_radius = 25,
    outer_radius = 100,
    number_of_coils = 10,
    gap_size = 5,
    height = 300
)
shape.export_stp('inner_tf_coils_flat.stp')


from paramak.parametric_shapes import PoloidalFieldCoil

shape = PoloidalFieldCoil(
    center_point = (100, 100),
    height = 20,
    width = 20,
    rotation_angle = rot_angle
)
shape.export_stp('poloidal_field_coil.stp')


from paramak.parametric_shapes import PoloidalFieldCoilCase

shape = PoloidalFieldCoilCase(
    center_point = (100, 100),
    coil_height = 20,
    coil_width = 20,
    casing_thickness = 10,
    rotation_angle = rot_angle
)
shape.export_stp('poloidal_field_coil_case.stp')


from paramak.parametric_shapes import PlasmaShape

shape = PlasmaShape(
    # default parameters
    rotation_angle = rot_angle
)
shape.export_stp('plasma_shape.stp')


from paramak.parametric_shapes import ConstantThicknessArcV

shape = ConstantThicknessArcV(                
                         inner_lower_point=(300,-200),
                         inner_mid_point=(500,0),
                         inner_upper_point=(300,200),
                         thickness=20,
                         rotation_angle=rot_angle
                        )
shape.export_stp('blanket_arc_v.stp')
