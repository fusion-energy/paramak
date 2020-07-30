
import math
import operator

import cadquery as cq

import paramak


class BallReactor(paramak.Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils.
    There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    :param inner_bore_radial_thickness: the radial thickness of 
     the inner bore (cm)
    :type inner_bore_radial_thickness: float
    :inboard_tf_leg_radial_thickness: the radial thickness of the
     inner leg of the toroidal field coils (cm)
    :type inboard_tf_leg_radial_thickness: float
    :center_column_shield_radial_thickness: the radial thickness
     of the center column shield (cm)
    :type center_column_shield_radial_thickness: float
    :divertor_radial_thickness: the radial thickness of the divertor
     (cm), this fills the gap between the center column shield and blanket
    :type divertor_radial_thickness: float
    :inner_plasma_gap_radial_thickness: the radial thickness of the
     inboard gap between the plasma and the center column shield (cm)
    :type inner_plasma_gap_radial_thickness: float
    :plasma_radial_thickness: the radial thickness of the plasma (cm),
     this is double the minor radius
    :type plasma_radial_thickness: float
    :outer_plasma_gap_radial_thickness: the radial thickness of the
     outboard gap between the plasma and the firstwall (cm)
    :type outer_plasma_gap_radial_thickness: float
    :firstwall_radial_thickness: the radial thickness of the first wall (cm)
    :type firstwall_radial_thickness: float
    :blanket_radial_thickness: the radial thickness of the blanket (cm)
    :type blanket_radial_thickness: float
    :blanket_rear_wall_radial_thickness: the radial thickness of the rear wall
     of the blanket (cm)
    :type blanket_rear_wall_radial_thickness: float
    :elongation: the elongation of the plasma
    :type elongation: float
    :triangularity: the triangularity of the plasma
    :type triangularity: float
    :number_of_tf_coils: the number of tf coils
    :type number_of_tf_coils: int
    :pf_coil_to_rear_blanket_radial_gap: the radial distance between the rear
     blanket and the closest poloidal field coil (optional)
    :type pf_coil_to_rear_blanket_radial_gap: float
    :pf_coil_radial_thicknesses: the radial thickness of each poloidal field
     coil (optional)
    :type pf_coil_radial_thicknesses: list of floats
    :pf_coil_vertical_thicknesses: the vertical thickness of each poloidal
     field coil (optional)
    :type pf_coil_vertical_thicknesses: list of floats
    :pf_coil_to_tf_coil_radial_gap: the radial distance between the rear of
     the poloidal field coil and the toroidal field coil (optional)
    :type pf_coil_to_tf_coil_radial_gap: float
    :tf_coil_radial_thickness: the radial thickness of the toroidal field
     coil (optional)
    :type tf_coil_radial_thickness: float
    :tf_coil_poloidal_thickness: the poloidal thickness of the toroidal field
     coil (optional)
    :type tf_coil_poloidal_thickness: float
    :rotation_angle: the angle of the sector that is desired
    :type rotation_angle: int

    :return: a Reactor object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        elongation,
        triangularity,
        number_of_tf_coils,
        pf_coil_to_rear_blanket_radial_gap = None,
        pf_coil_radial_thicknesses = None,
        pf_coil_vertical_thicknesses = None,
        pf_coil_to_tf_coil_radial_gap = None,
        tf_coil_radial_thickness = None,
        tf_coil_poloidal_thickness = None,
        rotation_angle = 360,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = center_column_shield_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.blanket_radial_thickness = blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_to_rear_blanket_radial_gap = pf_coil_to_rear_blanket_radial_gap
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap
        self.tf_coil_radial_thickness = tf_coil_radial_thickness
        self.tf_coil_poloidal_thickness = tf_coil_poloidal_thickness

        # sets major raduis and minor radius from equatorial_points to allow a radial build
        # this helps avoid the plasma overlapping the center column and such things
        inner_equatorial_point = inner_bore_radial_thickness + inboard_tf_leg_radial_thickness + center_column_shield_radial_thickness + inner_plasma_gap_radial_thickness
        outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness
        self.major_radius = (inner_equatorial_point + plasma_radial_thickness + inner_equatorial_point) /2
        self.minor_radius = ((outer_equatorial_point + inner_equatorial_point) /2 )-inner_equatorial_point

        self.elongation = elongation
        self.triangularity = triangularity

        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        self.create_components()


    def create_components(self):

        shapes_or_components = []

        plasma = paramak.Plasma(major_radius=self.major_radius,
                                minor_radius=self.minor_radius,
                                elongation=self.elongation,
                                triangularity=self.triangularity,
                                rotation_angle=self.rotation_angle)
        plasma.create_solid()

        shapes_or_components.append(plasma)


        # this is the radial build sequence, where one componet stops and another starts
        inner_bore_start_radius = 0
        inner_bore_end_radius = inner_bore_start_radius + self.inner_bore_radial_thickness

        inboard_tf_coils_start_radius = inner_bore_end_radius
        inboard_tf_coils_end_radius = inboard_tf_coils_start_radius + self.inboard_tf_leg_radial_thickness

        center_column_shield_start_radius = inboard_tf_coils_end_radius
        center_column_shield_end_radius = center_column_shield_start_radius + self.center_column_shield_radial_thickness

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
        blanket_read_wall_end_radius = blanket_read_wall_start_radius + self.blanket_rear_wall_radial_thickness 

        #this is the vertical build sequence, componets build on each other in a similar manner to the radial build

        divertor_start_height = plasma.high_point[1]+ self.outer_plasma_gap_radial_thickness
        # make it the same hight as fw, blanket, rw
        divertor_end_height = divertor_start_height + self.firstwall_radial_thickness + self.blanket_radial_thickness + self.blanket_rear_wall_radial_thickness

        firstwall_start_height = divertor_start_height
        firstwall_end_height = firstwall_start_height + self.firstwall_radial_thickness

        blanket_start_height = firstwall_end_height
        blanket_end_height = blanket_start_height + self.blanket_radial_thickness

        blanket_rear_wall_start_height = blanket_end_height
        blanket_rear_wall_end_height = blanket_rear_wall_start_height + self.blanket_rear_wall_radial_thickness

        tf_coil_height = blanket_rear_wall_end_height
        center_column_shield_height = blanket_rear_wall_end_height * 2

        if self.pf_coil_vertical_thicknesses!=None and self.pf_coil_radial_thicknesses !=None and self.pf_coil_to_rear_blanket_radial_gap !=None:
            number_of_pf_coils = len(self.pf_coil_vertical_thicknesses)

            y_position_step = (2*(blanket_rear_wall_end_height + self.pf_coil_to_rear_blanket_radial_gap))/(number_of_pf_coils+1)

            pf_coils_y_values = []
            pf_coils_x_values = []
            # adds in coils with equal spacing strategy, should be updated to allow user positions
            for i in range(number_of_pf_coils):
                y_value =blanket_rear_wall_end_height + self.pf_coil_to_rear_blanket_radial_gap - y_position_step*(i+1)
                x_value = blanket_read_wall_end_radius + self.pf_coil_to_rear_blanket_radial_gap + \
                          0.5*self.pf_coil_radial_thicknesses[i]
                pf_coils_y_values.append(y_value)
                pf_coils_x_values.append(x_value)

            pf_coil_start_radius = blanket_read_wall_end_radius + self.pf_coil_to_rear_blanket_radial_gap
            pf_coil_end_radius = pf_coil_start_radius + max(self.pf_coil_radial_thicknesses)
        
        if self.pf_coil_to_tf_coil_radial_gap !=None and self.tf_coil_radial_thickness !=None:
            tf_coil_start_radius = pf_coil_end_radius + self.pf_coil_to_rear_blanket_radial_gap 
            tf_coil_end_radius = tf_coil_start_radius + self.tf_coil_radial_thickness


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

        # shapes_or_components.append(inboard_tf_coils)
        inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=tf_coil_height * 2,
            inner_radius=inboard_tf_coils_start_radius,
            outer_radius=inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="inboard_tf_coils.stp",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
        )
        shapes_or_components.append(inboard_tf_coils)

        center_column_shield = paramak.CenterColumnShieldCylinder(
            height=center_column_shield_height,
            inner_radius=center_column_shield_start_radius,
            outer_radius=center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="center_column_shield.stp",
            name="center_column_shield",
            material_tag="center_column_shield_mat",
        )
        shapes_or_components.append(center_column_shield)

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
                name='extra_blanket_upper',
                material_tag='blanket_mat')
            shapes_or_components.append(extra_blanket_upper)

            extra_firstwall_upper = paramak.RotateStraightShape(points=[
                (divertor_end_radius, firstwall_start_height),
                (divertor_end_radius, firstwall_end_height),
                (plasma.high_point[0], firstwall_end_height),
                (plasma.high_point[0], firstwall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_firstwall_upper.stp',
                name='extra_firstwall_upper',
                material_tag='firstwall_mat')
            shapes_or_components.append(extra_firstwall_upper)

            extra_blanket_rear_wall_upper = paramak.RotateStraightShape(points=[
                (divertor_end_radius, blanket_rear_wall_start_height),
                (divertor_end_radius, blanket_rear_wall_end_height),
                (plasma.high_point[0], blanket_rear_wall_end_height),
                (plasma.high_point[0], blanket_rear_wall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_rear_wall_upper.stp',
                name='extra_blanket_rear_wall_upper',
                material_tag='blanket_rear_wall_mat')
            shapes_or_components.append(extra_blanket_rear_wall_upper)

            extra_blanket_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -blanket_start_height),
                (divertor_end_radius, -blanket_end_height),
                (plasma.high_point[0], -blanket_end_height),
                (plasma.high_point[0], -blanket_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_lower.stp',
                name='extra_blanket_lower',
                material_tag='blanket_mat')
            shapes_or_components.append(extra_blanket_lower)

            extra_firstwall_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -firstwall_start_height),
                (divertor_end_radius, -firstwall_end_height),
                (plasma.high_point[0], -firstwall_end_height),
                (plasma.high_point[0], -firstwall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_firstwall_lower.stp',
                name='extra_firstwall_lower',
                material_tag='firstwall_mat')
            shapes_or_components.append(extra_firstwall_lower)

            extra_blanket_rear_wall_lower = paramak.RotateStraightShape(points=[
                (divertor_end_radius, -blanket_rear_wall_start_height),
                (divertor_end_radius, -blanket_rear_wall_end_height),
                (plasma.high_point[0], -blanket_rear_wall_end_height),
                (plasma.high_point[0], -blanket_rear_wall_start_height),
                ],
                rotation_angle=self.rotation_angle,
                stp_filename='extra_blanket_rear_wall_lower.stp',
                name='extra_blanket_rear_wall_lower',
                material_tag='blanket_rear_wall_mat')
            shapes_or_components.append(extra_blanket_rear_wall_lower)

            divertor_upper_part = paramak.RotateStraightShape(points=[
                (divertor_start_radius, divertor_end_height),
                (divertor_start_radius, divertor_start_height),
                (divertor_end_radius, divertor_start_height),
                (divertor_end_radius, divertor_end_height),
                ],
                stp_filename='divertor_upper.stp',
                name='divertor_upper',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_upper_part)

            # negative signs used as this is in the negative side of the Z axis 
            divertor_lower_part = paramak.RotateStraightShape(points=[
                (divertor_start_radius, -divertor_end_height),
                (divertor_start_radius, -divertor_start_height),
                (divertor_end_radius, -divertor_start_height),
                (divertor_end_radius, -divertor_end_height),
                ],
                stp_filename='divertor_lower.stp',
                name='divertor_lower',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_lower_part)

        # curve divertor arround if it is larger than the horitonal space provided
        elif self.divertor_radial_thickness > space_for_divertor:

            length_of_curved_section = self.divertor_radial_thickness - space_for_divertor

            center_point, radius = paramak.utils.find_center_point_of_circle(point1=(firstwall_start_radius, 0),
                                                      point2=(plasma.high_point[0], firstwall_start_height),
                                                      point3=(plasma.low_point[0], -firstwall_start_height))

            circumference = 2.*math.pi*radius

            rotation_angle = (length_of_curved_section * 2 * math.pi) / circumference

            new_point_x1, new_point_y1 = paramak.utils.rotate(center_point, (plasma.high_point[0], firstwall_start_height), -rotation_angle/2.)
            new_point_x2, new_point_y2 = paramak.utils.rotate(center_point, (plasma.high_point[0], firstwall_start_height), -rotation_angle)
            new_point_x3, new_point_y3 = paramak.utils.rotate(center_point, (plasma.high_point[0], blanket_rear_wall_end_height), -rotation_angle)
            new_point_x4, new_point_y4 = paramak.utils.rotate(center_point, (plasma.high_point[0], blanket_rear_wall_end_height), -rotation_angle/2.)

            divertor_upper_part = paramak.RotateMixedShape(points=[
                (divertor_start_radius, divertor_end_height, 'straight'),
                (divertor_start_radius, divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, divertor_start_height, 'circle'),
                (new_point_x1, new_point_y1, 'circle'),
                (new_point_x2, new_point_y2, 'straight'),
                (new_point_x3, new_point_y3, 'circle'),
                (new_point_x4, new_point_y4, 'circle'),
                (divertor_start_radius+space_for_divertor, divertor_end_height, 'straight'),
                ],
                stp_filename='divertor_upper.stp',
                name='divertor_upper',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_upper_part)

            # negative signs used as this is in the negative side of the Z axis 
            divertor_lower_part = paramak.RotateMixedShape(points=[
                (divertor_start_radius, -divertor_end_height, 'straight'),
                (divertor_start_radius, -divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, -divertor_start_height, 'circle'),
                (new_point_x1, -new_point_y1, 'circle'),
                (new_point_x2, -new_point_y2, 'straight'),
                (new_point_x3, -new_point_y3, 'circle'),
                (new_point_x4, -new_point_y4, 'circle'),
                (divertor_start_radius+space_for_divertor, -divertor_end_height, 'straight'),
                ],
                stp_filename='divertor_lower.stp',
                name='divertor_lower',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_lower_part)

        elif self.divertor_radial_thickness == space_for_divertor:

            divertor_upper_part = paramak.RotateMixedShape(points=[
                (divertor_start_radius, divertor_end_height, 'straight'),
                (divertor_start_radius, divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, divertor_end_height, 'straight'),
                ],
                stp_filename='divertor_upper.stp',
                name='divertor_upper',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_upper_part)

            # negative signs used as this is in the negative side of the Z axis 
            divertor_lower_part = paramak.RotateMixedShape(points=[
                (divertor_start_radius, -divertor_end_height, 'straight'),
                (divertor_start_radius, -divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, -divertor_start_height, 'straight'),
                (divertor_start_radius+space_for_divertor, -divertor_end_height, 'straight'),
                ],
                stp_filename='divertor_lower.stp',
                name='divertor_lower',
                rotation_angle=self.rotation_angle,
                material_tag='divertor_mat'
                )
            shapes_or_components.append(divertor_lower_part)

        firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(firstwall_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], firstwall_start_height),
            inner_lower_point=(plasma.low_point[0], -firstwall_start_height),
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='firstwall.stp',
            name='firstwall',
            material_tag='firstwall_mat',
            cut=[divertor_lower_part, divertor_upper_part]
        )
        shapes_or_components.append(firstwall)

        blanket = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(blanket_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], blanket_start_height),
            inner_lower_point=(plasma.low_point[0], -blanket_start_height),
            thickness=self.blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='blanket.stp',
            name='blanket',
            material_tag='blanket_mat',
            cut=[divertor_lower_part, divertor_upper_part]
        )
        shapes_or_components.append(blanket)

        blanket_rear_casing = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(blanket_read_wall_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], blanket_rear_wall_start_height),
            inner_lower_point=(plasma.low_point[0], -blanket_rear_wall_start_height),
            thickness=self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='blanket_rear_wall.stp',
            name='blanket_rear_wall',
            material_tag='blanket_rear_wall_mat',
            cut=[divertor_lower_part, divertor_upper_part]
        )
        shapes_or_components.append(blanket_rear_casing)

        if self.pf_coil_vertical_thicknesses!=None and self.pf_coil_radial_thicknesses !=None and self.pf_coil_to_rear_blanket_radial_gap !=None:
            
            for i, (rt, vt, y_value, x_value) in enumerate(zip(self.pf_coil_radial_thicknesses,
                                                             self.pf_coil_vertical_thicknesses,
                                                             pf_coils_y_values,
                                                             pf_coils_x_values,
                                                            )
                                                        ):


                pf_coil = paramak.PoloidalFieldCoil(width=rt, 
                                                    height=vt,
                                                    center_point=(x_value,y_value),
                                                    rotation_angle=self.rotation_angle,
                                                    stp_filename='pf_coil_'+str(i)+'.stp',
                                                    name='pf_coil',
                                                    material_tag='pf_coil_mat')
                shapes_or_components.append(pf_coil)
        
            if self.pf_coil_to_tf_coil_radial_gap !=None and self.tf_coil_radial_thickness !=None:
                tf_coil = paramak.ToroidalFieldCoilRectangle(inner_upper_point=(inboard_tf_coils_start_radius, tf_coil_height),
                                                inner_lower_point=(inboard_tf_coils_start_radius, -tf_coil_height),
                                                inner_mid_point=(tf_coil_start_radius, 0),
                                                thickness= self.tf_coil_radial_thickness,
                                                number_of_coils=self.number_of_tf_coils,
                                                distance=self.tf_coil_poloidal_thickness,
                                                cut=cutting_slice)

                shapes_or_components.append(tf_coil)
        
        self.shapes_and_components = shapes_or_components