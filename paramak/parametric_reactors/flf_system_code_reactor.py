from typing import List, Optional

import paramak


class FlfSystemCodeReactor(paramak.Reactor):
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
            blanket and the inner edge of the vaccum vessel (cm).
        upper_vv_thickness: The thickness (z axis direction) of the
            upper section of vaccum vessel (cm).
        vv_thickness: The radial thickness of the vaccum vessel (cm)
        lower_vv_thickness: The thickness (z axis direction) of the
            lower section of vaccum vessel (cm).
        rotation_angle: The angle of the sector simulated. Set to 360 for
            simulations and less when creating models for visualization.
    """

    def __init__(
        self,
        inner_blanket_radius: Optional[float] = 100.0,
        blanket_thickness: Optional[float] = 70.0,
        blanket_height: Optional[float] = 500.0,
        lower_blanket_thickness: Optional[float] = 50.0,
        upper_blanket_thickness: Optional[float] = 40.0,
        blanket_vv_gap: Optional[float] = 20.0,
        upper_vv_thickness: Optional[float] = 10.0,
        vv_thickness: Optional[float] = 10.0,
        lower_vv_thickness: Optional[float] = 10.0,
        rotation_angle: Optional[float] = 180.0,
    ):

        super().__init__([])

        self.rotation_angle = rotation_angle
        self.inner_blanket_radius = inner_blanket_radius
        self.blanket_thickness = blanket_thickness
        self.blanket_height = blanket_height
        self.lower_blanket_thickness = lower_blanket_thickness
        self.upper_blanket_thickness = upper_blanket_thickness
        self.blanket_vv_gap = blanket_vv_gap
        self.upper_vv_thickness = upper_vv_thickness
        self.vv_thickness = vv_thickness
        self.lower_vv_thickness = lower_vv_thickness

        # adds self.input_variable_names from the Reactor class
        self.input_variable_names: List[str] = self.input_variable_names + [
            "inner_blanket_radius",
            "blanket_thickness",
            "blanket_height",
            "lower_blanket_thickness",
            "upper_blanket_thickness",
            "blanket_vv_gap",
            "upper_vv_thickness",
            "vv_thickness",
            "lower_vv_thickness",
            "rotation_angle",
        ]

    def create_solids(self):
        """Creates a list of paramak.Shape for components and saves it in
        self.shapes_and_components
        """
        inner_wall = self.inner_blanket_radius + self.blanket_thickness + self.blanket_vv_gap
        lower_vv = paramak.RotateStraightShape(
            points=[
                (inner_wall, 0),
                (
                    inner_wall,
                    self.lower_vv_thickness,
                ),
                (
                    0,
                    self.lower_vv_thickness,
                ),
                (0, 0),
            ],
            rotation_angle=self.rotation_angle,
            color=(0.5, 0.5, 0.5),
            name="lower_vessel",
        )

        lower_blanket = paramak.RotateStraightShape(
            points=[
                (inner_wall, self.lower_vv_thickness),
                (inner_wall, self.lower_vv_thickness + self.lower_blanket_thickness),
                (0, self.lower_vv_thickness + self.lower_blanket_thickness),
                (0, self.lower_vv_thickness),
            ],
            rotation_angle=self.rotation_angle,
            color=(0.0, 1.0, 0.498),
            name="lower_blanket",
        )

        blanket = paramak.CenterColumnShieldCylinder(
            height=self.blanket_height,
            center_height=self.lower_vv_thickness + self.lower_blanket_thickness + 0.5 * self.blanket_height,
            inner_radius=self.inner_blanket_radius,
            outer_radius=self.blanket_thickness + self.inner_blanket_radius,
            rotation_angle=self.rotation_angle,
            cut=lower_blanket,
            color=(0.0, 1.0, 0.498),
            name="blanket",
        )

        upper_vv = paramak.RotateStraightShape(
            points=[
                (inner_wall, self.lower_vv_thickness + self.lower_blanket_thickness + self.blanket_height),
                (
                    inner_wall,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness,
                ),
                (
                    0,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness,
                ),
                (0, self.lower_vv_thickness + self.lower_blanket_thickness + self.blanket_height),
            ],
            rotation_angle=self.rotation_angle,
            color=(0.5, 0.5, 0.5),
            name="upper_vessel",
        )

        upper_blanket = paramak.RotateStraightShape(
            points=[
                (
                    inner_wall,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness,
                ),
                (
                    inner_wall,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness
                    + self.upper_blanket_thickness,
                ),
                (
                    0,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness
                    + self.upper_blanket_thickness,
                ),
                (
                    0,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness,
                ),
            ],
            rotation_angle=self.rotation_angle,
            color=(0.0, 1.0, 0.498),
            name="upper_blanket",
        )

        vac_ves = paramak.RotateStraightShape(
            points=[
                (inner_wall, 0),
                (
                    inner_wall,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness
                    + self.upper_blanket_thickness,
                ),
                (
                    inner_wall + self.vv_thickness,
                    self.lower_vv_thickness
                    + self.lower_blanket_thickness
                    + self.blanket_height
                    + self.upper_vv_thickness
                    + self.upper_blanket_thickness,
                ),
                (inner_wall + self.vv_thickness, 0),
            ],
            rotation_angle=self.rotation_angle,
            color=(0.5, 0.5, 0.5),
            name="vessel",
        )

        self.shapes_and_components = [
            blanket,
            vac_ves,
            upper_blanket,
            lower_blanket,
            lower_vv,
            upper_vv,
        ]
