import warnings
import typing

from ..utils import create_wire_workplane_from_points
import mpmath
import numpy as np
import sympy as sp
from scipy.interpolate import interp1d


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

    # input()
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
    # create sympy objects and derivatives

    overlapping_shape = False
    theta_sp = sp.Symbol("theta")

    R_sp, Z_sp = distribution(
        major_radius,
        minor_radius,
        triangularity,
        elongation,
        vertical_displacement,
        theta_sp,
        pkg=sp,
    )
    R_derivative = sp.diff(R_sp, theta_sp)
    Z_derivative = sp.diff(Z_sp, theta_sp)
    points = []

    for theta in thetas:
        # get local value of derivatives
        val_R_derivative = float(R_derivative.subs("theta", theta))
        val_Z_derivative = float(Z_derivative.subs("theta", theta))

        # get normal vector components
        nx = val_Z_derivative
        ny = -val_R_derivative

        # normalise normal vector
        normal_vector_norm = (nx**2 + ny**2) ** 0.5
        nx /= normal_vector_norm
        ny /= normal_vector_norm

        # calculate outer points
        val_R_outer = (
            distribution(
                major_radius,
                minor_radius,
                triangularity,
                elongation,
                vertical_displacement,
                theta,
            )[0]
            + offset(theta) * nx
        )
        val_Z_outer = (
            distribution(
                major_radius,
                minor_radius,
                triangularity,
                elongation,
                vertical_displacement,
                theta,
            )[1]
            + offset(theta) * ny
        )
        if float(val_R_outer) > 0:
            points.append([float(val_R_outer), float(val_Z_outer), "spline"])
        else:
            overlapping_shape = True
    return points, overlapping_shape


def distribution(major_radius, minor_radius, triangularity, elongation, vertical_displacement, theta, pkg=np):
    """Plasma distribution theta in degrees

    Args:
        theta (float or np.array or sp.Symbol): the angle(s) in degrees.
        pkg (module, optional): Module to use in the funciton. If sp, as
            sympy object will be returned. If np, a np.array or a float
            will be returned. Defaults to np.

    Returns:
        (float, float) or (sympy.Add, sympy.Mul) or
            (numpy.array, numpy.array): The R and Z coordinates of the
            point with angle theta
    """
    if pkg == np:
        theta = np.radians(theta)
    else:
        theta = mpmath.radians(theta)
    R = major_radius + minor_radius * pkg.cos(theta + triangularity * pkg.sin(theta))
    Z = elongation * minor_radius * pkg.sin(theta) + vertical_displacement
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
    offset_from_plasma: typing.Union[float, typing.Iterable[float]] = 0.0,
    num_points: int = 50,
    name: str = "blanket_from_plasma",
    color: typing.Tuple[float, float, float, typing.Optional[float]] = (
        0.333,
        0.0,
        0.0,
    ),
    rotation_angle: float = 90.0,
    plane="XZ",
    origin=(0, 0, 0),
    obj=None,
    allow_overlapping_shape=False,
    connect_to_center=False,
):
    """A blanket volume created from plasma parameters. In might be nessecary
    to increase the num_points when making long but thin geometry with this
    component.

    Args:
        thickness (float or [float] or callable or [(float), (float)]):
            the thickness of the blanket (cm). If the thickness is a float then
            this produces a blanket of constant thickness. If the thickness is
            a tuple of floats, blanket thickness will vary linearly between the
            two values. If thickness is callable, then the blanket thickness
            will be a function of poloidal angle (in degrees). If thickness is
            a list of two lists (thicknesses and angles) then these will be
            used together with linear interpolation.
        start_angle: the angle in degrees to start the blanket, measured anti
            clockwise from 3 o'clock.
        stop_angle: the angle in degrees to stop the blanket, measured anti
            clockwise from 3 o'clock.
        plasma: If not None, the parameters of the plasma Object will be used.
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
        allow_overlapping_shape: allows parameters to create a shape that
            overlaps itself.
    """

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

    solid = wire.revolve(rotation_angle)
    solid.name = name
    solid.color = color
    return solid
