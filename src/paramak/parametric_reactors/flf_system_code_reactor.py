import cadquery as cq
from paramak import RotateStraightShape, CenterColumnShieldCylinder


def FlfSystemCodeReactor(
    inner_blanket_radius: float = 100.0,
    blanket_thickness: float = 70.0,
    blanket_height: float = 500.0,
    lower_blanket_thickness: float = 50.0,
    upper_blanket_thickness: float = 40.0,
    blanket_vv_gap: float = 20.0,
    upper_vv_thickness: float = 10.0,
    vv_thickness: float = 10.0,
    lower_vv_thickness: float = 10.0,
    rotation_angle: float = 180.0,
):
    """Creates the 3D geometry for the a simplified FLF reactor model based
    on parameters. Model design was originally presented at University of
    York in 2019. Model shown at 50 mins 48 seconds in presentation
    https://www.youtube.com/watch?v=DtvcEkIb4D4

    Arguments:
        inner_blanket_radius: The radial distance between the center of the
            reactor on the start of the blanket (cm).
        blanket_thickness: The radial thickness of the blanket (cm).
        blanket_height: The height (z axis direction) of the blanket (cm).
        lower_blanket_thickness: The thickness (z axis direction) of the
            lower blanket pool (cm).
        upper_blanket_thickness: The thickness (z axis direction) of the
            upper blanket pool (cm).
        blanket_vv_gap: The radial distance between the outer edge of the
            blanket and the inner edge of the vacuum vessel (cm).
        upper_vv_thickness: The thickness (z axis direction) of the
            upper section of vacuum vessel (cm).
        vv_thickness: The radial thickness of the vacuum vessel (cm)
        lower_vv_thickness: The thickness (z axis direction) of the
            lower section of vacuum vessel (cm).
        rotation_angle: The angle of the sector simulated. Set to 360 for
            simulations and less when creating models for visualization.
    """

    inner_wall = inner_blanket_radius + blanket_thickness + blanket_vv_gap
    lower_vac_vessel = RotateStraightShape(
        points=[
            (inner_wall, 0),
            (
                inner_wall,
                lower_vv_thickness,
            ),
            (
                0,
                lower_vv_thickness,
            ),
            (0, 0),
        ],
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name="lower_vessel",
    )

    lower_blanket = RotateStraightShape(
        points=[
            (inner_wall, lower_vv_thickness),
            (inner_wall, lower_vv_thickness + lower_blanket_thickness),
            (0, lower_vv_thickness + lower_blanket_thickness),
            (0, lower_vv_thickness),
        ],
        rotation_angle=rotation_angle,
        color=(0.0, 1.0, 0.498),
        name="lower_blanket",
    )

    blanket = CenterColumnShieldCylinder(
        height=blanket_height,
        center_height=lower_vv_thickness + lower_blanket_thickness + 0.5 * blanket_height,
        inner_radius=inner_blanket_radius,
        outer_radius=blanket_thickness + inner_blanket_radius,
        rotation_angle=rotation_angle,
        cut=lower_blanket,
        color=(0.0, 1.0, 0.498),
        name="blanket",
    )

    upper_vac_vessel = RotateStraightShape(
        points=[
            (inner_wall, lower_vv_thickness + lower_blanket_thickness + blanket_height),
            (
                inner_wall,
                lower_vv_thickness + lower_blanket_thickness + blanket_height + upper_vv_thickness,
            ),
            (
                0,
                lower_vv_thickness + lower_blanket_thickness + blanket_height + upper_vv_thickness,
            ),
            (0, lower_vv_thickness + lower_blanket_thickness + blanket_height),
        ],
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name="upper_vessel",
    )

    upper_blanket = RotateStraightShape(
        points=[
            (
                inner_wall,
                lower_vv_thickness + lower_blanket_thickness + blanket_height + upper_vv_thickness,
            ),
            (
                inner_wall,
                lower_vv_thickness
                + lower_blanket_thickness
                + blanket_height
                + upper_vv_thickness
                + upper_blanket_thickness,
            ),
            (
                0,
                lower_vv_thickness
                + lower_blanket_thickness
                + blanket_height
                + upper_vv_thickness
                + upper_blanket_thickness,
            ),
            (
                0,
                lower_vv_thickness + lower_blanket_thickness + blanket_height + upper_vv_thickness,
            ),
        ],
        rotation_angle=rotation_angle,
        color=(0.0, 1.0, 0.498),
        name="upper_blanket",
    )

    vac_vessel = RotateStraightShape(
        points=[
            (inner_wall, 0),
            (
                inner_wall,
                lower_vv_thickness
                + lower_blanket_thickness
                + blanket_height
                + upper_vv_thickness
                + upper_blanket_thickness,
            ),
            (
                inner_wall + vv_thickness,
                lower_vv_thickness
                + lower_blanket_thickness
                + blanket_height
                + upper_vv_thickness
                + upper_blanket_thickness,
            ),
            (inner_wall + vv_thickness, 0),
        ],
        rotation_angle=rotation_angle,
        color=(0.5, 0.5, 0.5),
        name="vessel",
    )

    colors=[(0.5, 0.5, 0.5)]

    assembly = (
        cq.Assembly(name='FlfSystemCodeReactor')
        .add(blanket.solid,name='blanket', color=cq.Color(*colors[0]))
        .add(vac_vessel.solid,name='vac_vessel')   
        .add(upper_blanket.solid,name='upper_blanket')
        .add(lower_blanket.solid,name='lower_blanket')
        .add(lower_vac_vessel.solid,name='lower_vac_vessel')
        .add(upper_vac_vessel.solid,name='upper_vac_vessel')
    )

    return assembly
