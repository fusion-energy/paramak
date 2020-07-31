
import math
import operator

import cadquery as cq

import paramak


class SubmersionRector(paramak.Reactor):
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
        inboard_blanket_radial_thickness,
        inboard_firstwall_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outboard_plasma_gap_radial_thickness,
        outboard_firstwall_radial_thickness,
        outboard_blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        pf_coil_to_rear_blanket_radial_gap,
        pf_coil_radial_thicknesses,
        pf_coil_to_tf_coil_radial_gap,
        tf_coil_radial_thickness,
        divertor_radial_thickness,
        tf_coil_poloidal_thickness,
        plasma_vertical_thickness,
        plasma_gap_vertical_thickness,
        divertor_vertical_thickness,
        blanket_vertical_thickness,
        blanket_rear_wall_vertical_thickness,
        tf_coil_to_rear_blanket_vertical_gap,
        tf_coil_vertical_thickness,
        pf_coil_vertical_thicknesses,
        number_of_tf_coils,
        rotation_angle = 360,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = center_column_shield_radial_thickness
        self.inboard_blanket_radial_thickness = inboard_blanket_radial_thickness
        self.inboard_firstwall_radial_thickness = inboard_firstwall_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outboard_plasma_gap_radial_thickness = outboard_plasma_gap_radial_thickness
        self.outboard_firstwall_radial_thickness = outboard_firstwall_radial_thickness
        self.outboard_blanket_radial_thickness = outboard_blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_to_rear_blanket_radial_gap = pf_coil_to_rear_blanket_radial_gap
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap
        self.tf_coil_radial_thickness = tf_coil_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.tf_coil_poloidal_thickness = tf_coil_poloidal_thickness
        self.plasma_vertical_thickness = plasma_vertical_thickness
        self.plasma_gap_vertical_thickness = plasma_gap_vertical_thickness
        self.divertor_vertical_thickness = divertor_vertical_thickness
        self.blanket_vertical_thickness = blanket_vertical_thickness
        self.blanket_rear_wall_vertical_thickness = blanket_rear_wall_vertical_thickness
        self.tf_coil_to_rear_blanket_vertical_gap = tf_coil_to_rear_blanket_vertical_gap
        self.tf_coil_vertical_thickness = tf_coil_vertical_thickness
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        self.create_components()

        # these are set later by the plasma
        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

    def create_components(self):

        shapes_or_components = []

        plasma = paramak.Plas
                                rotation_angle=self.rotation_angle)
    #     plasma.create_solid()

        shapes_or_components.append(plasma)
