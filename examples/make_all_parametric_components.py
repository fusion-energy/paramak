
import paramak

rot_angle = 180

shape = paramak.Plasma(
    # default parameters
    rotation_angle = rot_angle
)
shape.export_stp('plasma_shape.stp')


shape = paramak.BlanketConstantThicknessFP(
    plasma=shape,
    thickness = 70,
    start_angle = 30,
    stop_angle = 330,
    offset_from_plasma = 20,
    rotation_angle = rot_angle
)
shape.export_stp('blanket_constant_thickness.stp')


shape = paramak.CenterColumnShieldCylinder(
    inner_radius = 80,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_cylinder.stp')


shape = paramak.CenterColumnShieldHyperbola(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_hyperbola.stp')


shape = paramak.CenterColumnShieldCircular(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_circular.stp')


shape = paramak.CenterColumnShieldFlatTopHyperbola(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    arc_height = 220,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_flat_top_hyperbola.stp')


shape = paramak.CenterColumnShieldFlatTopCircular(
    inner_radius = 50,
    mid_radius = 75,
    outer_radius = 100,
    arc_height = 220,
    height = 300,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_flat_top_Circular.stp')


shape = paramak.CenterColumnShieldPlasmaHyperbola(
    inner_radius = 150,
    mid_offset = 50,
    edge_offset = 40,
    height = 800,
    rotation_angle = rot_angle
)
shape.export_stp('center_column_shield_plasma_hyperbola.stp')


#

# shape = paramak.DivertorBlock(
#     major_radius = 800,
#     minor_radius = 400,
#     triangularity = 1.2,
#     elongation = 0.9,
#     thickness = 50,
#     offset_from_plasma = 20,
#     start
# )



shape = paramak.InnerTfCoilsCircular(
    inner_radius = 25,
    outer_radius = 100,
    number_of_coils = 10,
    gap_size = 5,
    height = 300
)
shape.export_stp('inner_tf_coils_circular.stp')


shape = paramak.InnerTfCoilsFlat(
    inner_radius = 25,
    outer_radius = 100,
    number_of_coils = 10,
    gap_size = 5,
    height = 300
)
shape.export_stp('inner_tf_coils_flat.stp')


shape = paramak.PoloidalFieldCoil(
    center_point = (100, 100),
    height = 20,
    width = 20,
    rotation_angle = rot_angle
)
shape.export_stp('poloidal_field_coil.stp')


shape = paramak.PoloidalFieldCoilCaseFC(
    pf_coil=shape,
    casing_thickness = 10,
    rotation_angle = rot_angle
)
shape.export_stp('poloidal_field_coil_case_fc.stp')


shape = paramak.PoloidalFieldCoilCase(
    center_point = (100, 100),
    coil_height = 20,
    coil_width = 20,
    casing_thickness = 10,
    rotation_angle = rot_angle
)
shape.export_stp('poloidal_field_coil_case.stp')


shape = paramak.BlanketConstantThicknessArcV(
                         inner_lower_point=(300,-200),
                         inner_mid_point=(500,0),
                         inner_upper_point=(300,200),
                         thickness=100,
                         rotation_angle=rot_angle
                        )
shape.export_stp('blanket_arc_v.stp')

shape = paramak.BlanketConstantThicknessArcH(
                         inner_lower_point=(300,-200),
                         inner_mid_point=(400,0),
                         inner_upper_point=(300,200),
                         thickness=100,
                         rotation_angle=rot_angle
                        )
shape.export_stp('blanket_arc_h.stp')

shape = paramak.ToroidalFieldCoilRectangle(
            inner_upper_point=(100,700),
            inner_mid_point=(800,0),
            inner_lower_point=(100,-700),
            thickness=150,
            distance=6,
            number_of_coils=8)
shape.export_stp('tf_coil_rectangle.stp')
