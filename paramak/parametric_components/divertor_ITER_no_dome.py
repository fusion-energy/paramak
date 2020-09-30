from paramak import RotateMixedShape, extend, rotate, distance_between_two_points, ITERtypeDivertor
import math
import numpy as np


class ITERtypeDivertorNoDome(ITERtypeDivertor):
    """Creates a ITER-like divertor with inner and outer vertical targets

    Args:
        anchors ((float, float), (float, float)): xy coordinates of points at
            the top of vertical targets.
            Defaults to ((450, -300), (561, -367)).
        coverages (float, float): coverages (anticlockwise) in degrees of the
            circular parts of vertical targets. Defaults to (90, 180).
        radii (float, float): radii (cm) of circular parts of the vertical
            targets. Defaults to (50, 25).
        lengths (float, float): leg length (cm) of the vertical targets.
            Defaults to (78, 87).
        tilts ((float, float), optional): Tilt angles (anticlockwise) in
            degrees for the vertical targets. Defaults to (-27, 0).
        Others: see paramak.RotateMixedShape() arguments.

    Keyword Args:
        Others: see paramak.RotateMixedShape() and paramak.ITERtypeDivertor()
            attributes.

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid
        of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        anchors=((450, -300), (561, -367)),
        coverages=(90, 180),
        radii=(50, 25),
        lengths=(78, 87),
        tilts=(-27, 0),
        rotation_angle=360,
        workplane="XZ",
        points=None,
        stp_filename=None,
        azimuth_placement_angle=0,
        solid=None,
        color=(0.5, 0.5, 0.5),
        name=None,
        material_tag=None,
        cut=None,
    ):

        super().__init__(
            anchors=anchors,
            coverages=coverages,
            radii=radii,
            lengths=lengths,
            dome=False,
            dome_height=None,
            dome_length=None,
            dome_thickness=None,
            dome_pos=None,
            tilts=tilts,
            rotation_angle=rotation_angle,
            workplane=workplane,
            points=points,
            stp_filename=stp_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            solid=solid,
            color=color,
            name=name,
            material_tag=material_tag,
            cut=cut,
        )
