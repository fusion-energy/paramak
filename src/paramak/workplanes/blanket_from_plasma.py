from __future__ import annotations

import typing
import warnings

import numpy as np
from OCP.Standard import Standard_Failure
from OCP.StdFail import StdFail_NotDone
from scipy.interpolate import interp1d

from ..utils import (
    create_wire_workplane_from_points,
    rotate_to_rotation_start_angle,
    validate_positive,
    validate_positive_integer,
    validate_rotation_angle,
)


def make_callable(attribute, start_angle, stop_angle):
    """This function transforms an attribute (thickness or offset) into a
    callable function of theta
    """
    # if the attribute is a list, create a interpolated object of the
    # values
    if isinstance(attribute, (tuple, list)):
        if isinstance(attribute[0], (tuple, list)) and isinstance(attribute[1], (tuple, list)) and len(attribute) == 2:
            # attribute is a list of 2 lists
            if len(attribute[0]) != len(attribute[1]):
                raise ValueError(
                    "The length of angles list must equal \
                    the length of values list"
                )
            list_of_angles = np.array(attribute[0])
            offset_values = attribute[1]
        else:
            # no list of angles is given
            offset_values = attribute
            list_of_angles = np.linspace(start_angle, stop_angle, len(offset_values), endpoint=True)
        interpolated_values = interp1d(list_of_angles, offset_values)

    def fun(theta):
        if callable(attribute):
            return attribute(theta)
        elif isinstance(attribute, (tuple, list)):
            return interpolated_values(theta)
        else:
            return attribute

    return fun


def find_points(
    start_angle,
    stop_angle,
    offset_from_plasma,
    major_radius,
    minor_radius,
    triangularity,
    elongation,
    vertical_displacement,
    thickness,
    connect_to_center,
    num_points,
    allow_overlapping_shape,
    angles=None,
):
    # create array of angles theta
    if angles is None:
        thetas = np.linspace(
            start_angle,
            stop_angle,
            num=num_points,
            endpoint=True,
        )
    else:
        thetas = angles

    # create inner points
    inner_offset = make_callable(offset_from_plasma, start_angle, stop_angle)
    inner_points, overlapping_shape = create_offset_points(
        major_radius=major_radius,
        minor_radius=minor_radius,
        triangularity=triangularity,
        elongation=elongation,
        vertical_displacement=vertical_displacement,
        thetas=thetas,
        offset=inner_offset,
    )
    inner_points[-1][2] = "straight"

    # create outer points
    thickness = make_callable(thickness, start_angle, stop_angle)

    def outer_offset(theta):
        return inner_offset(theta) + thickness(theta)

    outer_points, overlapping_shape = create_offset_points(
        major_radius=major_radius,
        minor_radius=minor_radius,
        triangularity=triangularity,
        elongation=elongation,
        vertical_displacement=vertical_displacement,
        thetas=np.flip(thetas),
        offset=outer_offset,
    )

    outer_points[-1][2] = "straight"

    if connect_to_center:
        inner_points.append([0, inner_points[-1][1], "straight"])
        inner_points = [[0, inner_points[0][1], "straight"]] + inner_points
        outer_points.append([0, outer_points[-1][1], "straight"])
        outer_points = [[0, outer_points[0][1], "straight"]] + outer_points

    # assemble
    points = inner_points + outer_points
    if overlapping_shape and allow_overlapping_shape is False:
        msg = "blanket_from_plasma: Some points with negative R coordinate have " "been ignored."
        warnings.warn(msg, category=UserWarning)

    return points


def create_offset_points(
    major_radius: float,
    minor_radius: float,
    triangularity: float,
    elongation: float,
    vertical_displacement,
    thetas,
    offset,
):
    """generates a list of points following parametric equations with an
    offset

    Args:
        thetas (np.array): the angles in degrees.
        offset (callable): offset value (cm). offset=0 will follow the
            parametric equations.

    Returns:
        list: list of points [[R1, Z1, connection1], [R2, Z2, connection2],
        ...]
    """
    thetas = np.asarray(thetas, dtype=float)
    # offset may be a user function that only accepts a single angle
    offsets = np.array([offset(theta) for theta in thetas], dtype=float)
    R, Z = offset_curve_coordinates(
        major_radius, minor_radius, triangularity, elongation, vertical_displacement, thetas, offsets
    )
    points = [[float(r), float(z), "spline"] for r, z in zip(R, Z) if r > 0]
    overlapping_shape = len(points) < len(thetas)
    return points, overlapping_shape


def offset_curve_coordinates(
    major_radius: float,
    minor_radius: float,
    triangularity: float,
    elongation: float,
    vertical_displacement: float,
    thetas,
    offsets,
):
    """Returns the R and Z
    coordinates of the plasma surface offset along its outward normal.

    Args:
        thetas (np.array): the angles in degrees.
        offsets (float or np.array): the offset distance at each angle.

    Returns:
        (np.array, np.array): the R and Z coordinates.
    """
    R, Z = distribution(major_radius, minor_radius, triangularity, elongation, vertical_displacement, thetas)
    thetas = np.radians(np.asarray(thetas, dtype=float))
    # derivatives with respect to theta, the scale factor between degrees
    # and radians cancels when the normal is normalised
    R_derivative = -minor_radius * np.sin(thetas + triangularity * np.sin(thetas)) * (
        1 + triangularity * np.cos(thetas)
    )
    Z_derivative = elongation * minor_radius * np.cos(thetas)
    normal_vector_norm = np.hypot(Z_derivative, R_derivative)
    nx = Z_derivative / normal_vector_norm
    ny = -R_derivative / normal_vector_norm
    return R + offsets * nx, Z + offsets * ny


def poloidal_arc_length_table(
    major_radius: float,
    minor_radius: float,
    triangularity: float,
    elongation: float,
    offset,
    vertical_displacement: float = 0.0,
    num_points: int = 7201,
):
    """Computes the cumulative arc length around a full poloidal loop of the
    plasma surface offset by a distance that can vary with poloidal angle.

    The loop starts at the outboard midplane (theta = 0) and proceeds counter
    clockwise (upwards on the outboard side) to theta = 360.

    Args:
        offset (callable): the offset from the plasma surface as a function of
            poloidal angle in degrees. Must accept a np.array of angles.
        num_points: number of points used to discretise the loop.

    Returns:
        (np.array, np.array): the angles in degrees and the cumulative arc
        length at each angle. The last arc length value is the total.
    """
    thetas = np.linspace(0.0, 360.0, num_points)
    R, Z = offset_curve_coordinates(
        major_radius, minor_radius, triangularity, elongation, vertical_displacement, thetas, offset(thetas)
    )
    arc_lengths = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(R), np.diff(Z)))])
    return thetas, arc_lengths


def distribution(major_radius, minor_radius, triangularity, elongation, vertical_displacement, theta):
    """Plasma distribution theta in degrees

    Args:
        theta (float or np.array): the angle(s) in degrees.

    Returns:
        (float, float) or (numpy.array, numpy.array): The R and Z
            coordinates of the point with angle theta
    """
    theta = np.radians(theta)
    R = major_radius + minor_radius * np.cos(theta + triangularity * np.sin(theta))
    Z = elongation * minor_radius * np.sin(theta) + vertical_displacement
    return R, Z


def blanket_from_plasma(
    thickness,
    start_angle: float,
    stop_angle: float,
    minor_radius: float = 150.0,
    major_radius: float = 450.0,
    triangularity: float = 0.55,
    elongation: float = 2.0,
    vertical_displacement: float = 0.0,
    offset_from_plasma: float | typing.Iterable[float] = 0.0,
    num_points: int = 200,
    name: str = "blanket_from_plasma",
    color: tuple[float, float, float, float | None] = (
        0.333,
        0.0,
        0.0,
    ),
    rotation_angle: float = 90.0,
    rotation_start_angle: float = 0.0,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    allow_overlapping_shape=False,
    connect_to_center=False,
):
    """A blanket volume created from plasma parameters. It might be necessary
    to increase the num_points when making long but thin geometry with this
    component.

    Args:
        thickness (float or [float] or callable or [(float), (float)]):
            the thickness of the blanket (cm). If the thickness is a float then
            this produces a blanket of constant thickness. If the thickness is
            a tuple of floats, blanket thickness will vary linearly between the
            two values. If thickness is callable, then the blanket thickness
            will be a function of poloidal angle (in degrees). If thickness is
            a list of two lists (angles and thicknesses) then these will be
            used together with linear interpolation.
        start_angle: the angle in degrees to start the blanket, measured anti
            clockwise from 3 o'clock.
        stop_angle: the angle in degrees to stop the blanket, measured anti
            clockwise from 3 o'clock.
        minor_radius: the minor radius of the plasma (cm).
        major_radius: the major radius of the plasma (cm).
        triangularity: the triangularity of the plasma.
        elongation: the elongation of the plasma.
        vertical_displacement: the vertical_displacement of the plasma (cm).
        offset_from_plasma: the distance between the plasma and the blanket
            (cm). If float, constant offset. If list of floats, offset will
            vary linearly between the values. If callable, offset will be a
            function of poloidal angle (in degrees). If a list of two lists
            (angles and offsets) then these will be used together with linear
            interpolation.
        num_points: number of points that will describe the shape.
        allow_overlapping_shape: if False (the default) a warning is given
            when the offset makes some points of the profile reach past the
            Z axis (a negative R). Those points are always left out of the
            profile, setting this to True only stops the warning.
        rotation_start_angle: the angle in degrees the revolution starts from,
            measured around the revolve axis from the workplane. The shape covers
            rotation_start_angle to rotation_start_angle + rotation_angle. Must be
            between -360 and 360. Defaults to 0.
    """
    validate_positive_integer(num_points, "num_points")
    validate_rotation_angle(rotation_angle)
    validate_positive(major_radius, "major_radius")
    validate_positive(minor_radius, "minor_radius")
    validate_positive(elongation, "elongation")
    if not (-1.0 <= triangularity <= 1.0):
        raise ValueError(f"triangularity must be between -1 and 1, got {triangularity}.")

    points = find_points(
        thickness=thickness,
        start_angle=start_angle,
        stop_angle=stop_angle,
        minor_radius=minor_radius,
        major_radius=major_radius,
        triangularity=triangularity,
        elongation=elongation,
        vertical_displacement=vertical_displacement,
        offset_from_plasma=offset_from_plasma,
        num_points=num_points,
        allow_overlapping_shape=allow_overlapping_shape,
        connect_to_center=connect_to_center,
    )
    points.append(points[0])

    wire = create_wire_workplane_from_points(points=points, plane=plane, origin=origin, obj=obj)

    try:
        solid = wire.revolve(rotation_angle)
    except (Standard_Failure, StdFail_NotDone) as e:
        raise ValueError(
            "blanket_from_plasma: could not revolve the profile, "
            "the geometry is probably self-overlapping"
        ) from e
    solid = rotate_to_rotation_start_angle(solid, wire, rotation_start_angle)
    solid.name = name
    solid.color = color
    return solid
