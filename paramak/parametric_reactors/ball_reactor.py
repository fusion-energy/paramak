
import operator

import cadquery as cq

import paramak


class BallReactor(paramak.Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils.
    There is not inboard breeder blanket on this ball reactor like
    most spherical reactors.

    :param inner_bore_radial_thickness:
    :type inner_bore_radial_thickness: float
    :inboard_tf_leg_radial_thickness:
    :type inboard_tf_leg_radial_thickness: float
    :center_column_radial_thickness:
    :type center_column_radial_thickness: float
    :divertor_radial_thickness:
    :type divertor_radial_thickness: float
    :inner_plasma_gap_radial_thickness:
    :type inner_plasma_gap_radial_thickness: float
    :plasma_radial_thickness:
    :type plasma_radial_thickness: float
    :outer_plasma_gap_radial_thickness:
    :type outer_plasma_gap_radial_thickness: float
    :firstwall_radial_thickness:
    :type firstwall_radial_thickness: float
    :blanket_radial_thickness:
    :type blanket_radial_thickness: float
    :blanket_rear_wall_thickness:
    :type blanket_rear_wall_thickness: float
    :elongation:
    :type elongation: float
    :triangularity:
    :type triangularity: float
    :number_of_tf_coils:
    :type number_of_tf_coils: int
    :rotation_angle:
    :type rotation_angle: int

    :return: a Reactor object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,
        blanket_rear_wall_thickness,
        elongation,
        triangularity,
        number_of_tf_coils,
        rotation_angle = 180
    ):

        super().__init__()

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_radial_thickness = center_column_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.blanket_radial_thickness = blanket_radial_thickness
        self.blanket_rear_wall_thickness = blanket_rear_wall_thickness


        # sets major raduis and minor radius from equatorial_points to allow a radial build
        # this helps avoid the plasma overlapping the center column and such things
        inner_equatorial_point = inner_bore_radial_thickness + inboard_tf_leg_radial_thickness + center_column_radial_thickness + inner_plasma_gap_radial_thickness
        outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness
        self.major_radius = (inner_equatorial_point + plasma_radial_thickness + inner_equatorial_point) /2
        self.minor_radius = ((outer_equatorial_point + inner_equatorial_point) /2 )-inner_equatorial_point

        self.elongation = elongation
        self.triangularity = triangularity

        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle


        self.create_components()


    def create_components(self):

        plasma = paramak.Plasma(major_radius=self.major_radius,
                                minor_radius=self.minor_radius,
                                elongation=self.elongation,
                                triangularity=self.triangularity,
                                rotation_angle=self.rotation_angle)
        plasma.create_solid()

        self.add_shape_or_component(plasma)


        # this is the radial build sequence, where one componet stops and another starts
        inner_bore_start_radius = 0
        inner_bore_end_radius = inner_bore_start_radius + self.inner_bore_radial_thickness

        inboard_tf_coils_start_radius = inner_bore_end_radius
        inboard_tf_coils_end_radius = inboard_tf_coils_start_radius + self.inboard_tf_leg_radial_thickness

        center_column_shield_start_radius = inboard_tf_coils_end_radius
        center_column_shield_end_radius = center_column_shield_start_radius + self.center_column_radial_thickness

        divertor_start_radius = center_column_shield_end_radius
        divertor_end_radius = center_column_shield_end_radius + self.divertor_radial_thickness

        firstwall_start_radius = center_column_shield_end_radius \
                                 + self.inner_plasma_gap_radial_thickness \
                                 + self.plasma_radial_thickness \
                                 + self.outer_plasma_gap_radial_thickness 
        firstwall_end_radius = firstwall_start_radius + self.firstwall_radial_thickness

        blanket_start_radius = firstwall_end_radius
        blanket_end_radius = blanket_start_radius + self.blanket_radial_thickness

        blanket_read_wall_start_radius = blanket_end_radius 
        blanket_read_wall_end_radius = blanket_read_wall_start_radius + self.blanket_rear_wall_thickness 

        #this is the vertical build sequence, componets build on each other in a similar manner to the radial build

        divertor_start_height = plasma.high_point[1]+ self.outer_plasma_gap_radial_thickness
        # make it the same hight as fw, blanket, rw
        divertor_end_height = divertor_start_height + self.firstwall_radial_thickness + self.blanket_radial_thickness + self.blanket_rear_wall_thickness

        firstwall_start_height = divertor_start_height
        firstwall_end_height = firstwall_start_height + self.firstwall_radial_thickness

        blanket_start_height = firstwall_end_height
        blanket_end_height = blanket_start_height + self.blanket_radial_thickness

        blanket_rear_wall_start_height = blanket_end_height
        blanket_rear_wall_end_height = blanket_rear_wall_start_height + self.blanket_rear_wall_thickness

        tf_coil_height = blanket_rear_wall_end_height * 2
        center_column_shield_height = blanket_rear_wall_end_height * 2

        if self.rotation_angle < 360:
            max_high = 3 * center_column_shield_height
            max_width = 3 * blanket_read_wall_end_radius
            cutting_slice = paramak.RotateStraightShape(points=[
                    (0,max_high),
                    (max_width, max_high),
                    (max_width, -max_high),
                    (0, -max_high),
                ],
                rotation_angle=360-self.rotation_angle,
                azimuth_placement_angle=360-self.rotation_angle
            )
        else:
            cutting_slice=None

        inboard_tf_coils = paramak.InnerTfCoilsCircular(
            height=tf_coil_height,
            inner_radius = inboard_tf_coils_start_radius,
            outer_radius = inboard_tf_coils_end_radius,
            number_of_coils = self.number_of_tf_coils,
            gap_size=10,
            stp_filename="inboard_tf_coils.stp",
            material_tag="inboard_tf_coils_material",
            cut=cutting_slice
        )

        self.add_shape_or_component(inboard_tf_coils)


        center_column_shield = paramak.CenterColumnShieldCylinder(
            height=center_column_shield_height,
            inner_radius=center_column_shield_start_radius,
            outer_radius=center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="center_column_shield.stp",
            material_tag="center_column_material",
        )
        self.add_shape_or_component(center_column_shield)


        divertor_upper_part = paramak.RotateStraightShape(points=[
            (divertor_start_radius, divertor_end_height),
            (divertor_start_radius, divertor_start_height),
            (divertor_end_radius, divertor_start_height),
            (divertor_end_radius, divertor_end_height),
            ],
            stp_filename='divertor_upper.stp',
            rotation_angle=self.rotation_angle,
            material_tag='divertor_material'
            )
        self.add_shape_or_component(divertor_upper_part)

        print(            (divertor_start_radius, -divertor_end_height),
            (divertor_start_radius, -divertor_start_height),
            (divertor_end_radius, -divertor_start_height),
            (divertor_end_radius, -divertor_end_height))

        # negative signs used as this is in the negative side of the Z axis 
        divertor_lower_part = paramak.RotateStraightShape(points=[
            (divertor_start_radius, -divertor_end_height),
            (divertor_start_radius, -divertor_start_height),
            (divertor_end_radius, -divertor_start_height),
            (divertor_end_radius, -divertor_end_height),
            ],
            stp_filename='divertor_lower.stp',
            rotation_angle=self.rotation_angle,
            material_tag='divertor_material'
            )
        self.add_shape_or_component(divertor_lower_part)

        space_for_divertor = plasma.high_point[0] - center_column_shield_end_radius

        #add blanket if the divertor doesn't take up all the space
        if space_for_divertor > self.divertor_radial_thickness:
            print('making extra blanket as there is space between the divertor and existing blanket')
            extra_blanket_upper = paramak.RotateStraightShape(points=[
                (divertor_end_radius, blanket_start_height),
                (divertor_end_radius, blanket_end_height),
                (plasma.high_point[0], blanket_end_height),
                (plasma.high_point[0], blanket_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_upper.stp',
                material_tag='blanket_material')
            self.add_shape_or_component(extra_blanket_upper)

            extra_firstwall_upper = paramak.RotateStraightShape(points=[
                (divertor_end_radius, firstwall_start_height),
                (divertor_end_radius, firstwall_end_height),
                (plasma.high_point[0], firstwall_end_height),
                (plasma.high_point[0], firstwall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_firstwall_upper.stp',
                material_tag='firstwall_material')
            self.add_shape_or_component(extra_firstwall_upper)

            extra_blanket_rear_wall_upper = paramak.RotateStraightShape(points=[
                (divertor_end_radius, blanket_rear_wall_start_height),
                (divertor_end_radius, blanket_rear_wall_end_height),
                (plasma.high_point[0], blanket_rear_wall_end_height),
                (plasma.high_point[0], blanket_rear_wall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_rear_wall_upper.stp',
                material_tag='blanket_rear_wall_material')
            self.add_shape_or_component(extra_blanket_rear_wall_upper)


            extra_blanket_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -blanket_start_height),
                (divertor_end_radius, -blanket_end_height),
                (plasma.high_point[0], -blanket_end_height),
                (plasma.high_point[0], -blanket_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_lower.stp',
                material_tag='blanket_material')
            self.add_shape_or_component(extra_blanket_lower)

            extra_firstwall_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -firstwall_start_height),
                (divertor_end_radius, -firstwall_end_height),
                (plasma.high_point[0], -firstwall_end_height),
                (plasma.high_point[0], -firstwall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_firstwall_lower.stp',
                material_tag='firstwall_material')
            self.add_shape_or_component(extra_firstwall_lower)

            extra_blanket_rear_wall_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -blanket_rear_wall_start_height),
                (divertor_end_radius, -blanket_rear_wall_end_height),
                (plasma.high_point[0], -blanket_rear_wall_end_height),
                (plasma.high_point[0], -blanket_rear_wall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_rear_wall_lower.stp',
                material_tag='blanket_rear_wall_material')
            self.add_shape_or_component(extra_blanket_rear_wall_lower)

        firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(firstwall_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], firstwall_start_height),
            inner_lower_point=(plasma.low_point[0], -firstwall_start_height),
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='firstwall.stp'
        )
        self.add_shape_or_component(firstwall)


        blanket = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(blanket_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], blanket_start_height),
            inner_lower_point=(plasma.low_point[0], -blanket_start_height),
            thickness=self.blanket_radial_thickness,
            rotation_angle=self.rotation_angle
        )
        self.add_shape_or_component(blanket)


        blanket_rear_casing = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(blanket_read_wall_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], blanket_rear_wall_start_height),
            inner_lower_point=(plasma.low_point[0], -blanket_rear_wall_start_height),
            thickness=self.blanket_rear_wall_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='blanket_rear_wall.stp'
        )
        self.add_shape_or_component(blanket_rear_casing)

