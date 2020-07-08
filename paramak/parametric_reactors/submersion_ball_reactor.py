from paramak import Reactor
import paramak

class SubmersionBallReactor(Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils and
    a submersion blanket.

    :param major_radius: 
    :type height: float

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        major_radius,
        minor_radius,
        offset_from_plasma,
        blanket_thickness,
        firstwall_thickness,
        center_column_shield_inner_radius,
        center_column_shield_outer_radius,
        number_of_tf_coils,
        casing_thickness,
        rotation_angle = 180
    ):

        super().__init__()

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.offset_from_plasma = offset_from_plasma
        self.blanket_thickness = blanket_thickness
        self.firstwall_thickness = firstwall_thickness
        self.rotation_angle = rotation_angle
        self.center_column_shield_inner_radius = center_column_shield_inner_radius
        self.center_column_shield_outer_radius = center_column_shield_outer_radius
        self.number_of_tf_coils = number_of_tf_coils
        self.casing_thickness = casing_thickness

        self.create_components()


    def create_components(self):

        plasma = paramak.Plasma(major_radius=self.major_radius,
                                minor_radius=self.minor_radius,
                                rotation_angle=self.rotation_angle)
        plasma.create_solid()

        self.add_shape_or_component(plasma)

        outboard_firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(plasma.minor_radius + 
                             plasma.major_radius + 
                             self.offset_from_plasma,
                             0),
            inner_upper_point=(plasma.x_point,
                               plasma.z_point+self.offset_from_plasma),
            inner_lower_point=(plasma.x_point,
                               -(plasma.z_point+self.offset_from_plasma)),
            thickness=self.firstwall_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='outboard_firstwall.stp'
        )

        self.add_shape_or_component(outboard_firstwall)

        inboard_firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(
                             plasma.major_radius - 
                             (plasma.minor_radius + 
                             self.offset_from_plasma),
                             0),
            inner_upper_point=(plasma.x_point,
                               plasma.z_point+self.offset_from_plasma),
            inner_lower_point=(plasma.x_point,
                               -(plasma.z_point+self.offset_from_plasma)),
            thickness=-self.firstwall_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='inboard_firstwall.stp'
        )

        self.add_shape_or_component(inboard_firstwall)

        # The height of this center column is calculated using CadQuery commands
        center_column_shield = paramak.CenterColumnShieldCylinder(
            height=2*(plasma.z_point + self.offset_from_plasma),
            inner_radius=self.center_column_shield_inner_radius,
            outer_radius=self.center_column_shield_outer_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="center_column_shield.stp",
            material_tag="center_column_material",
        )
        self.add_shape_or_component(center_column_shield)

        inboard_tf_coils = paramak.InnerTfCoilsCircular(
            height=2*(plasma.z_point + self.offset_from_plasma),
            outer_radius = self.center_column_shield_inner_radius,
            inner_radius = 30,
            number_of_coils = self.number_of_tf_coils,
            gap_size=5,
            stp_filename="inboard_tf_coils.stp",
            material_tag="inboard_tf_coils_material",
        )

        self.add_shape_or_component(inboard_tf_coils)

        submersion_blanket = paramak.RotateMixedShape(
            points=[
                (self.center_column_shield_outer_radius, plasma.z_point + self.offset_from_plasma, 'spline'),
                (plasma.x_point, plasma.z_point+self.blanket_thickness, 'spline'),
                (self.major_radius+self.minor_radius+self.offset_from_plasma+self.firstwall_thickness+self.blanket_thickness, 0, 'spline'),
                (plasma.x_point,-( plasma.z_point+self.blanket_thickness), 'spline'),
                (self.center_column_shield_outer_radius, -(plasma.z_point + self.offset_from_plasma), 'straight'),
            ],
            stp_filename = 'blanket.stp',
            material_tag='blanket_material',
            rotation_angle=self.rotation_angle,
            cut=[plasma, inboard_firstwall, outboard_firstwall]
        )

        # this takes the first solid from the compound
        submersion_blanket.solid = submersion_blanket.solid.solids().first()

        self.add_shape_or_component(submersion_blanket)

        blanket_casing = paramak.RotateMixedShape(
            points=[
                (self.center_column_shield_outer_radius, plasma.z_point + self.offset_from_plasma + self.casing_thickness, 'spline'),
                (plasma.x_point, plasma.z_point+self.blanket_thickness + self.casing_thickness, 'spline'),
                (self.major_radius+self.minor_radius+self.offset_from_plasma+self.firstwall_thickness+self.blanket_thickness +  + self.casing_thickness, 0, 'spline'),
                (plasma.x_point,-( plasma.z_point+self.blanket_thickness+ + self.casing_thickness), 'spline'),
                (self.center_column_shield_outer_radius, -(plasma.z_point + self.offset_from_plasma+ + self.casing_thickness), 'straight'),
            ],
            stp_filename = 'blanket_casing.stp',
            material_tag='blanket_casing_material',
            rotation_angle=self.rotation_angle,
            cut=[plasma, inboard_firstwall, outboard_firstwall, submersion_blanket]
        )

        # this takes the first solid from the compound
        blanket_casing.solid = blanket_casing.solid.solids().first()

        self.add_shape_or_component(blanket_casing)