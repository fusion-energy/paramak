import math
import operator

import cadquery as cq

import paramak


class SubmersionTokamak(paramak.Reactor):
    """Creates geometry for a simple submersion reactor including a
    plasma, cylindical center column shielding, square toroidal field
    coils. There is an inboard breeder blanket on this ball reactor.
    :param inner_bore_radial_thickness: the radial thickness of
     the inner bore (cm)
    :type inner_bore_radial_thickness: float
    :inboard_tf_leg_radial_thickness: the radial thickness of the
     inner leg of the toroidal field coils (cm)
    :type inboard_tf_leg_radial_thickness: float
    :center_column_shield_radial_thickness: the radial thickness
     of the center column shield (cm)
    :type center_column_shield_radial_thickness: float
    :inboard_blanket_radial_thickness: the radial thickness of the first wall (cm)
    :type inboard_blanket_radial_thickness: float
    :firstwall_radial_thickness: the radial thickness of the first wall (cm)
    :type firstwall_radial_thickness: float
    :inner_plasma_gap_radial_thickness: the radial thickness of the
     inboard gap between the plasma and the center column shield (cm)
    :type inner_plasma_gap_radial_thickness: float
    :plasma_radial_thickness: the radial thickness of the plasma (cm),
     this is double the minor radius
    :type plasma_radial_thickness: float
    :divertor_radial_thickness: the radial thickness of the divertors (cm)
    :type divertor_radial_thickness: float
    :support_radial_thickness: the radial thickness of the upper and lower supports (cm)
    :type support_radial_thickness: float
    :outer_plasma_gap_radial_thickness: the radial thickness of the
     outboard gap between the plasma and the firstwall (cm)
    :type outer_plasma_gap_radial_thickness: float
    :outboard_blanket_radial_thickness: the radial thickness of the blanket (cm)
    :type outboard_blanket_radial_thickness: float
    :blanket_rear_wall_radial_thickness: the radial thickness of the rear wall
     of the blanket (cm)
    :type blanket_rear_wall_radial_thickness: float
    :param high_point: the (x,z) coordinates value of the top of the plasma (cm)
    :type high_point: tuple of 2 floats
    :number_of_tf_coils: the number of tf coils
    :type number_of_tf_coils: int
    :rotation_angle: the angle of the sector that is desired
    :type rotation_angle: int
    :outboard_tf_coil_radial_thickness: the radial thickness of the toroidal field
     coil (optional)
    :type outboard_tf_coil_radial_thickness: float
    :tf_coil_to_rear_blanket_radial_gap: the radial distance between the rear of
     the blanket and the toroidal field coil (optional)
    :type tf_coil_to_rear_blanket_radial_gap: float
    :tf_coil_poloidal_thickness: the poloidal thickness of the toroidal field
     coil (optional)
    :type tf_coil_poloidal_thickness: float
    :pf_coil_vertical_thicknesses: the vertical thickness of each poloidal
     field coil (optional)
    :type pf_coil_vertical_thicknesses: list of floats
    :pf_coil_radial_thicknesses: the radial thickness of each poloidal field
     coil (optional)
    :type pf_coil_radial_thicknesses: list of floats
    :pf_coil_to_tf_coil_radial_gap: the radial distance between the rear of
     the poloidal field coil and the toroidal field coil (optional)
    :type pf_coil_to_tf_coil_radial_gap: float
    :return: a Reactor object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        inboard_blanket_radial_thickness,
        firstwall_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        divertor_radial_thickness,
        support_radial_thickness,
        outer_plasma_gap_radial_thickness,
        outboard_blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        plasma_high_point,
        number_of_tf_coils=16,
        rotation_angle=360,
        outboard_tf_coil_radial_thickness=None,
        tf_coil_to_rear_blanket_radial_gap=None,
        tf_coil_poloidal_thickness=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = (
            center_column_shield_radial_thickness
        )
        self.inboard_blanket_radial_thickness = inboard_blanket_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.outboard_blanket_radial_thickness = outboard_blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap
        self.outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness
        self.tf_coil_poloidal_thickness = tf_coil_poloidal_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.support_radial_thickness = support_radial_thickness
        self.plasma_high_point = plasma_high_point
        self.tf_coil_to_rear_blanket_radial_gap = tf_coil_to_rear_blanket_radial_gap
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        # these are set later by the plasma when it is created
        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

        self.create_components()

    def create_components(self):

        # this is the radial build sequence, where one componet stops and
        # another starts
        inner_bore_start_radius = 0
        inner_bore_end_radius = (
            inner_bore_start_radius + self.inner_bore_radial_thickness
        )

        inboard_tf_coils_start_radius = inner_bore_end_radius
        inboard_tf_coils_end_radius = (
            inboard_tf_coils_start_radius +
            self.inboard_tf_leg_radial_thickness)

        center_column_shield_start_radius = inboard_tf_coils_end_radius
        center_column_shield_end_radius = (
            center_column_shield_start_radius
            + self.center_column_shield_radial_thickness
        )

        inboard_blanket_start_radius = center_column_shield_end_radius
        inboard_blanket_end_radius = (
            inboard_blanket_start_radius +
            self.inboard_blanket_radial_thickness)

        inboard_firstwall_start_radius = inboard_blanket_end_radius
        inboard_firstwall_end_radius = (
            inboard_firstwall_start_radius + self.firstwall_radial_thickness
        )

        inner_plasma_gap_start_radius = inboard_firstwall_end_radius
        inner_plasma_gap_end_radius = (
            inner_plasma_gap_start_radius +
            self.inner_plasma_gap_radial_thickness)

        plasma_start_radius = inner_plasma_gap_end_radius
        plasma_end_radius = plasma_start_radius + self.plasma_radial_thickness

        outer_plasma_gap_start_radius = plasma_end_radius
        outer_plasma_gap_end_radius = (
            outer_plasma_gap_start_radius +
            self.outer_plasma_gap_radial_thickness)

        outboard_firstwall_start_radius = outer_plasma_gap_end_radius
        outboard_firstwall_end_radius = (
            outboard_firstwall_start_radius + self.firstwall_radial_thickness
        )

        outboard_blanket_start_radius = outboard_firstwall_end_radius
        outboard_blanket_end_radius = (
            outboard_blanket_start_radius +
            self.outboard_blanket_radial_thickness)

        blanket_rear_wall_start_radius = outboard_blanket_end_radius
        blanket_rear_wall_end_radius = (
            blanket_rear_wall_start_radius +
            self.blanket_rear_wall_radial_thickness)

        tf_info_provided = False
        if (
            self.outboard_tf_coil_radial_thickness is not None
            and self.tf_coil_to_rear_blanket_radial_gap is not None
            and self.tf_coil_poloidal_thickness is not None
        ):
            tf_info_provided = True
            outboard_tf_coil_start_radius = (
                blanket_rear_wall_end_radius +
                self.tf_coil_to_rear_blanket_radial_gap)
            outboard_tf_coil_end_radius = (
                outboard_tf_coil_start_radius +
                self.outboard_tf_coil_radial_thickness)

        pf_info_provided = False
        if (
            self.pf_coil_vertical_thicknesses is not None
            and self.pf_coil_radial_thicknesses is not None
            and self.pf_coil_to_tf_coil_radial_gap is not None
        ):
            pf_info_provided = True

        divertor_start_radius = (
            self.plasma_high_point[0] - 0.5 * self.divertor_radial_thickness
        )
        divertor_end_radius = (
            self.plasma_high_point[0] + 0.5 * self.divertor_radial_thickness
        )

        support_start_radius = (
            self.plasma_high_point[0] - 0.5 * self.support_radial_thickness
        )
        support_end_radius = (
            self.plasma_high_point[0] + 0.5 * self.support_radial_thickness
        )

        # this is the vertical build sequence, componets build on each other in
        # a similar manner to the radial build
        plasma_start_height = 0
        plasma_end_height = plasma_start_height + self.plasma_high_point[1]

        plasma_to_divertor_gap_start_height = plasma_end_height
        plasma_to_divertor_gap_end_height = (
            plasma_to_divertor_gap_start_height +
            self.outer_plasma_gap_radial_thickness)

        # the firstwall is cut by the divertor but uses the same control points
        firstwall_start_height = plasma_to_divertor_gap_end_height
        firstwall_end_height = firstwall_start_height + self.firstwall_radial_thickness

        blanket_start_height = firstwall_end_height
        blanket_end_height = (
            blanket_start_height + self.outboard_blanket_radial_thickness
        )

        blanket_rear_wall_start_height = blanket_end_height
        blanket_rear_wall_end_height = (
            blanket_rear_wall_start_height +
            self.blanket_rear_wall_radial_thickness)

        if tf_info_provided and pf_info_provided:
            number_of_pf_coils = len(self.pf_coil_vertical_thicknesses)

            y_position_step = (2 * blanket_rear_wall_end_height) / (
                number_of_pf_coils + 1
            )

            pf_coils_y_values = []
            pf_coils_x_values = []
            # adds in coils with equal spacing strategy, should be updated to
            # allow user positions
            for i in range(number_of_pf_coils):
                y_value = (
                    blanket_rear_wall_end_height
                    + self.pf_coil_to_tf_coil_radial_gap
                    - y_position_step * (i + 1)
                )
                x_value = (
                    outboard_tf_coil_end_radius
                    + self.pf_coil_to_tf_coil_radial_gap
                    + 0.5 * self.pf_coil_radial_thicknesses[i]
                )
                pf_coils_y_values.append(y_value)
                pf_coils_x_values.append(x_value)

            pf_coil_start_radius = (
                outboard_tf_coil_end_radius +
                self.pf_coil_to_tf_coil_radial_gap)
            pf_coil_end_radius = pf_coil_start_radius + max(
                self.pf_coil_radial_thicknesses
            )

        # raises an error if the plasma high point is not above part of the
        # plasma
        if self.plasma_high_point[0] < plasma_start_radius:
            raise ValueError(
                "The first value in plasma high_point is too small, it should be larger than",
                plasma_start_radius,
            )
        if self.plasma_high_point[0] > plasma_end_radius:
            raise ValueError(
                "The first value in plasma high_point is too large, it should be smaller than",
                plasma_end_radius,
            )

        if self.rotation_angle < 360:
            max_high = 3 * blanket_rear_wall_end_height
            max_width = 3 * blanket_rear_wall_end_radius
            cutting_slice = paramak.RotateStraightShape(
                points=[
                    (0, max_high),
                    (max_width, max_high),
                    (max_width, -max_high),
                    (0, -max_high),
                ],
                rotation_angle=360 - self.rotation_angle,
                azimuth_placement_angle=360 - self.rotation_angle,
            )
        else:
            cutting_slice = None

        shapes_or_components = []

        # shapes_or_components.append(inboard_tf_coils)
        inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=blanket_rear_wall_end_height * 2,
            inner_radius=inboard_tf_coils_start_radius,
            outer_radius=inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="inboard_tf_coils.stp",
            stl_filename="inboard_tf_coils.stl",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
        )
        shapes_or_components.append(inboard_tf_coils)

        center_column_shield = paramak.CenterColumnShieldCylinder(
            height=blanket_rear_wall_end_height * 2,
            inner_radius=center_column_shield_start_radius,
            outer_radius=center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="center_column_shield.stp",
            stl_filename="center_column_shield.stl",
            name="center_column_shield",
            material_tag="center_column_shield_mat",
        )
        shapes_or_components.append(center_column_shield)

        plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=plasma_end_radius,
            inner_equatorial_x_point=plasma_start_radius,
            high_point=self.plasma_high_point,
            rotation_angle=self.rotation_angle,
        )

        self.major_radius = plasma.major_radius
        self.minor_radius = plasma.minor_radius
        self.elongation = plasma.elongation
        self.triangularity = plasma.triangularity

        shapes_or_components.append(plasma)

        # this is used to cut the inboard blanket and then fused / unioned with
        # the firstwall
        inboard_firstwall = paramak.BlanketFP(
            plasma=plasma,
            offset_from_plasma=self.inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
        )

        inboard_blanket = paramak.CenterColumnShieldCylinder(
            height=blanket_end_height * 2,
            inner_radius=inboard_blanket_start_radius,
            outer_radius=max([item[0] for item in inboard_firstwall.points]),
            rotation_angle=self.rotation_angle,
            cut=inboard_firstwall,
        )

        # this takes a single solid from a compound of solids by finding the
        # solid nearest to a point
        inboard_blanket.solid = inboard_blanket.solid.solids(
            cq.selectors.NearestToPointSelector((0, 0, 0))
        )

        firstwall = paramak.BlanketFP(
            plasma=plasma,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="outboard_firstwall.stp",
            stl_filename="outboard_firstwall.stl",
            name="outboard_firstwall",
            material_tag="firstwall_mat",
            union=inboard_firstwall,
        )

        divertor = paramak.CenterColumnShieldCylinder(
            height=blanket_rear_wall_end_height * 2,
            inner_radius=divertor_start_radius,
            outer_radius=divertor_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            intersect=firstwall,
        )
        shapes_or_components.append(divertor)

        # the divertor is cut away then the firstwall can be added to the
        # reactor using CQ operations
        firstwall.solid = firstwall.solid.cut(divertor.solid)
        shapes_or_components.append(firstwall)

        # this is the outboard fused / unioned with the inboard blanket
        blanket = paramak.BlanketFP(
            plasma=plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness
            + self.firstwall_radial_thickness,
            thickness=self.outboard_blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            name="blanket",
            material_tag="blanket_mat",
            union=inboard_blanket,
        )

        supports = paramak.CenterColumnShieldCylinder(
            height=blanket_rear_wall_end_height * 2,
            inner_radius=support_start_radius,
            outer_radius=support_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="supports.stp",
            stl_filename="supports.stl",
            name="supports",
            material_tag="supports_mat",
            intersect=blanket,
        )
        shapes_or_components.append(supports)

        # cutting the supports away from the blanket
        blanket.solid = blanket.solid.cut(supports.solid)
        shapes_or_components.append(blanket)

        # shapes_or_components.append(outboard_rear_blanket_wall)

        outboard_rear_blanket_wall_upper = paramak.RotateStraightShape(
            points=[
                (center_column_shield_end_radius, blanket_rear_wall_start_height),
                (center_column_shield_end_radius, blanket_rear_wall_end_height),
                (
                    max([item[0] for item in inboard_firstwall.points]),
                    blanket_rear_wall_end_height,
                ),
                (
                    max([item[0] for item in inboard_firstwall.points]),
                    blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        outboard_rear_blanket_wall_lower = paramak.RotateStraightShape(
            points=[
                (center_column_shield_end_radius, -blanket_rear_wall_start_height),
                (center_column_shield_end_radius, -blanket_rear_wall_end_height),
                (
                    max([item[0] for item in inboard_firstwall.points]),
                    -blanket_rear_wall_end_height,
                ),
                (
                    max([item[0] for item in inboard_firstwall.points]),
                    -blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        outboard_rear_blanket_wall = paramak.BlanketFP(
            plasma=plasma,
            start_angle=90,
            stop_angle=-
            90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness +
            self.firstwall_radial_thickness +
            self.outboard_blanket_radial_thickness,
            thickness=self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="outboard_rear_blanket_wall.stp",
            stl_filename="outboard_rear_blanket_wall.stl",
            name="outboard_rear_blanket_wall",
            material_tag="rear_blanket_wall_mat",
            union=[
                outboard_rear_blanket_wall_upper,
                outboard_rear_blanket_wall_lower],
        )

        shapes_or_components.append(outboard_rear_blanket_wall)

        if tf_info_provided:
            tf_coil = paramak.ToroidalFieldCoilRectangle(
                inner_upper_point=(
                    inboard_tf_coils_start_radius,
                    blanket_rear_wall_end_height,
                ),
                inner_lower_point=(
                    inboard_tf_coils_start_radius,
                    -blanket_rear_wall_end_height,
                ),
                inner_mid_point=(outboard_tf_coil_start_radius, 0),
                thickness=self.outboard_tf_coil_radial_thickness,
                number_of_coils=self.number_of_tf_coils,
                distance=self.tf_coil_poloidal_thickness,
                stp_filename="outboard_tf_coil.stp",
                stl_filename="outboard_tf_coil.stl",
                cut=cutting_slice,
            )
            shapes_or_components.append(tf_coil)

            if pf_info_provided:

                for i, (rt, vt, y_value, x_value) in enumerate(
                    zip(
                        self.pf_coil_radial_thicknesses,
                        self.pf_coil_vertical_thicknesses,
                        pf_coils_y_values,
                        pf_coils_x_values,
                    )
                ):

                    pf_coil = paramak.PoloidalFieldCoil(
                        width=rt,
                        height=vt,
                        center_point=(x_value, y_value),
                        rotation_angle=self.rotation_angle,
                        stp_filename="pf_coil_" + str(i) + ".stp",
                        stl_filename="pf_coil_" + str(i) + ".stl",
                        name="pf_coil",
                        material_tag="pf_coil_mat",
                    )
                    shapes_or_components.append(pf_coil)

        self.shapes_and_components = shapes_or_components
