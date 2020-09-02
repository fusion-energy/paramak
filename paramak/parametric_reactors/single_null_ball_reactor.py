import math
import operator

import cadquery as cq

import paramak


class SingleNullBallReactor(paramak.BallReactor):
    """Creates geometry for a single ball reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    Arguments:
        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (cm)
        inboard_tf_leg_radial_thickness (float): the radial thickness of the
            inner leg of the toroidal field coils (cm)
        center_column_shield_radial_thickness (float): the radial thickness of
            the center column shield (cm)
        divertor_radial_thickness (float): the radial thickness of the divertor
            (cm), this fills the gap between the center column shield and blanket
        inner_plasma_gap_radial_thickness (float): the radial thickness of the
            inboard gap between the plasma and the center column shield (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
        outer_plasma_gap_radial_thickness (float): the radial thickness of the
            outboard gap between the plasma and firstwall (cm)
        firstwall_radial_thickness (float): the radial thickness of the first
            wall (cm)
        blanket_radial_thickness (float): the radial thickness of the blanket (cm)
        blanket_rear_wall_radial_thickness (float): the radial thickness of the
            rear wall of the blanket (cm)
        elongation (float): the elongation of the plasma
        triangularity (float): the triangularity of the plasma
        number_of_tf_coils (int): the number of tf coils
        pf_coil_to_rear_blanket_radial_gap (float): the radial distance between
            the rear blanket and the closest poloidal field coil (optional)
        pf_coil_radial_thicknesses (list of floats): the radial thickness of each
            poloidal field coil (optional)
        pf_coil_vertical_thicknesses (list of floats): the vertical thickness of
            each poloidal field coil (optional)
        pf_coil_to_tf_coil_radial_gap (float): the radial distance between the
            rear of the poloidal field coil and the toroidal field coil (optional)
        outboard_tf_coil_radial_thickness (float): the radial thickness of the
            toroidal field coil (optional)
        outboard_tf_coil_poloidal_thickness (float): the poloidal thickness of the toroidal
            field coil (optional)
        divertor_position (str): the position of the divertor, "upper" or "lower
        rotation_angle (float): the angle of the sector that is desired

    Returns:
        a paramak shape object: a Reactor object that has generic functionality
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
        pf_coil_to_rear_blanket_radial_gap=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        outboard_tf_coil_radial_thickness=None,
        outboard_tf_coil_poloidal_thickness=None,
        divertor_position="upper",
        rotation_angle=360,
    ):

        super().__init__(
            inner_bore_radial_thickness=inner_bore_radial_thickness,
            inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
            center_column_shield_radial_thickness=center_column_shield_radial_thickness,
            divertor_radial_thickness=divertor_radial_thickness,
            inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
            plasma_radial_thickness=plasma_radial_thickness,
            outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
            firstwall_radial_thickness=firstwall_radial_thickness,
            blanket_radial_thickness=blanket_radial_thickness,
            blanket_rear_wall_radial_thickness=blanket_rear_wall_radial_thickness,
            elongation=elongation,
            triangularity=triangularity,
            number_of_tf_coils=number_of_tf_coils,
            pf_coil_to_rear_blanket_radial_gap=pf_coil_to_rear_blanket_radial_gap,
            pf_coil_radial_thicknesses=pf_coil_radial_thicknesses,
            pf_coil_vertical_thicknesses=pf_coil_vertical_thicknesses,
            pf_coil_to_tf_coil_radial_gap=pf_coil_vertical_thicknesses,
            outboard_tf_coil_radial_thickness=outer_plasma_gap_radial_thickness,
            outboard_tf_coil_poloidal_thickness=outboard_tf_coil_poloidal_thickness,
            rotation_angle=rotation_angle)

        self.divertor_position = divertor_position

        shapes_or_components = []

        self.make_plasma(shapes_or_components)
        self.make_radial_build(shapes_or_components)
        self.make_vertical_build(shapes_or_components)
        self.make_inboard_tf_coils(shapes_or_components)
        self.make_center_column_shield(shapes_or_components)
        self.make_blanket_and_firstwall(shapes_or_components)
        self.make_divertor_single_null(shapes_or_components)
        self.make_component_cuts(shapes_or_components)

        self.shapes_and_components = shapes_or_components

    @property
    def divertor_position(self):
        return self._divertor_position

    @divertor_position.setter
    def divertor_position(self, value):
        acceptable_values = ["upper", "lower"]
        if value in acceptable_values:
            self._divertor_position = value
        else:
            raise ValueError("divertor position must be 'upper' or 'lower'")

    def make_divertor_single_null(self, shapes_or_components):

        # used as an intersect when making the divertor
        self._blanket_fw_rear_wall_envelope = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._firstwall_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._firstwall_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._firstwall_start_height),
            thickness=self.firstwall_radial_thickness
            + self.blanket_radial_thickness
            + self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            union=[
                self._extra_blanket_upper,
                self._extra_firstwall_upper,
                self._extra_blanket_rear_wall_upper,
                self._extra_blanket_lower,
                self._extra_firstwall_lower,
                self._extra_blanket_rear_wall_lower,
            ],
            stp_filename="test.stp",
        )

        if self.divertor_position == "upper":
            divertor_height = self._blanket_rear_wall_end_height
        elif self.divertor_position == "lower":
            divertor_height = -self._blanket_rear_wall_end_height

        self._divertor = paramak.RotateStraightShape(
            points=[
                (self._divertor_start_radius, 0),
                (self._divertor_end_radius, 0),
                (self._divertor_end_radius, divertor_height),
                (self._divertor_start_radius, divertor_height)
            ],
            intersect=self._blanket_fw_rear_wall_envelope,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            rotation_angle=self.rotation_angle
        )
        shapes_or_components.append(self._divertor)
