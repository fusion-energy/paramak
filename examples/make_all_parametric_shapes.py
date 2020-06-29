
rot_angle = 180

from paramak.parametric_shapes import BlanketConstantThickness

shape = BlanketConstantThickness(
            major_radius = 800,
            minor_radius = 400,
            triangularity = 1.2,
            elongation = 0.9,
            thickness = 100,
            stop_angle = 30,
            start_angle = 330,
            offset_from_plasma = 20,
            rotation_angle = rot_angle,
)

shape.export_stp('blanket_constant_thickness.stp')


# from paramak.parametric_shapes import DivertorBlock

# shape = DivertorBlock(
#             major_radius = 800,
#             minor_radius = 400,
#             triangularity = 1.2,
#             elongation = 0.9,
#             thickness = 50,
#             stop_angle = 120,
#             start_x_value = 50,
#             offset_from_plasma = 20,
#             rotation_angle = rot_angle
#         )

# shape.export_stp('divertor_block.stp')


from paramak.parametric_shapes import CenterColumnShieldCylinder

shape = CenterColumnShieldCylinder(
            inner_radius = 50,
            outer_radius = 100,
            height = 600,
            rotation_angle = rot_angle
)

shape.export_stp('center_column_shield_cylinder.stp')


from paramak.parametric_shapes import CenterColumnShieldHyperbola

shape = CenterColumnShieldHyperbola(
            inner_radius = 50,
            mid_radius = 90,
            outer_radius = 150,
            height = 600,
            rotation_angle = rot_angle
)

shape.export_stp('center_column_shield_hyperbola.stp')


from paramak.parametric_shapes import CenterColumnShieldFlatTopHyperbola

shape = CenterColumnShieldFlatTopHyperbola(
            inner_radius = 40,
            mid_radius = 90,
            outer_radius = 150,
            height = 800,
            arc_height = 500,
            rotation_angle = rot_angle
)

shape.export_stp('center_column_shield_flat_top_hyperbola.stp')


from paramak.parametric_shapes import CenterColumnShieldPlasmaHyperbola

shape = CenterColumnShieldPlasmaHyperbola(
            height = 1000,
            inner_radius = 150,
            mid_offset = 50,
            edge_offset = 50,
            rotation_angle = rot_angle
)

shape.export_stp('center_column_shield_plasma_hyperbola.stp')


from paramak.parametric_shapes import PoloidalFieldCoil

shape = PoloidalFieldCoil(
            height = 50,
            width = 50,
            center_point = (400, 700),
            rotation_angle = rot_angle
)

shape.export_stp('poloidal_field_coil.stp')


from paramak.parametric_shapes import PoloidalFieldCoilCase

shape = PoloidalFieldCoilCase(
            coil_height = 50,
            coil_width = 50,
            center_point = (400, 700),
            casing_thickness = 30,
            rotation_angle = rot_angle
)

shape.export_stp('poloidal_field_coil_case.stp')


from paramak.parametric_shapes import InnerTfCoilsCircular

shape = InnerTfCoilsCircular(
                             inner_radius = 40,
                             outer_radius = 180,
                             number_of_coils = 10,
                             gap_size = 10,
                             height = 600
                            )

shape.export_stp('inner_tf_coils_circular.stp')

from paramak.parametric_shapes import InnerTfCoilsFlat

shape = InnerTfCoilsFlat(
                         height=600,
                         inner_radius=40,
                         outer_radius=180,
                         number_of_coils=10,
                         gap_size=10
                        )

shape.export_stp('inner_tf_coils_flat.stp')
