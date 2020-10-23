
"""
This script makes a blanket and then segments it in a similar
manner to the EU DEMO segmentation for remote maintenance.
"""

import math
import numpy as np
import paramak


def make_demo_blanket(
        number_of_sections=8,
        gap_size=15,
        central_block_width=200):

    number_of_segments = 8
    gap_size = 15.
    central_block_width = 200

    large_dimention = 10000  # used to make large cutting slices
    offset = (360 / number_of_segments) / 2

    # a plasma shape is made and used by the BlanketFP, which builds around
    # the plasma
    plasma = paramak.Plasma(
        elongation=1.59,
        triangularity=0.33,
        major_radius=910,
        minor_radius=290)
    plasma.solid

    # makes a block which is used later to make the to parallel gaps segments
    parallel_outboard_gaps_inner = paramak.ExtrudeStraightShape(
        points=[(large_dimention, large_dimention),
                (large_dimention, -large_dimention),
                (0, -large_dimention),
                (0, large_dimention),
                ],
        distance=central_block_width,
        azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False)
    )

    # makes a larger block which has the smaller block cut away and the result
    # is two parallel gaps segments
    parallel_outboard_gaps_outer = paramak.ExtrudeStraightShape(
        points=[(large_dimention, large_dimention),
                (large_dimention, -large_dimention),
                (0, -large_dimention),
                (0, large_dimention),
                ],
        distance=central_block_width + (gap_size * 2),
        azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False),
        cut=parallel_outboard_gaps_inner
    )

    # this makes a gap that seperates the inboard and outboard blanket
    inboard_to_outboard_gaps = paramak.ExtrudeStraightShape(
        points=[(plasma.high_point[0] - (0.5 * gap_size), plasma.high_point[1]),
                (plasma.high_point[0] - (0.5 * gap_size), plasma.high_point[1] + 1000),
                (plasma.high_point[0] + (0.5 * gap_size), plasma.high_point[1] + 1000),
                (plasma.high_point[0] + (0.5 * gap_size), plasma.high_point[1]),
                ],
        distance=math.tan(math.radians(360 / (2 * number_of_segments))) * plasma.high_point[0] * 2,
        azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False)
    )

    # this makes the regular gaps (non parallel) gaps on the outboard blanket
    outboard_gaps = paramak.ExtrudeStraightShape(
        points=[(large_dimention, large_dimention),
                (large_dimention, -large_dimention),
                (0, -large_dimention),
                (0, large_dimention),
                ],
        distance=gap_size,
        azimuth_placement_angle=np.linspace(0 + offset, 360 + offset, number_of_segments, endpoint=False)
    )

    # makes the outboard blanket with cuts for all the segmentation
    outboard_blanket = paramak.BlanketFP(
        plasma=plasma,
        thickness=100,
        stop_angle=90,
        start_angle=-60,
        offset_from_plasma=30,
        rotation_angle=360,
        cut=[
            outboard_gaps,
            parallel_outboard_gaps_outer,
            inboard_to_outboard_gaps])

    # this makes the regular gaps on the outboard blanket
    inboard_gaps = paramak.ExtrudeStraightShape(
        points=[(large_dimention, large_dimention),
                (large_dimention, -large_dimention),
                (0, -large_dimention),
                (0, large_dimention),
                ],
        distance=gap_size,
        azimuth_placement_angle=np.linspace(0, 360, number_of_segments * 2, endpoint=False)
    )

    # makes the inboard blanket with cuts for all the segmentation
    inboard_blanket = paramak.BlanketFP(
        plasma=plasma,
        thickness=100,
        stop_angle=90,
        start_angle=260,
        offset_from_plasma=30,
        rotation_angle=360,
        cut=[inboard_gaps, inboard_to_outboard_gaps],
        union=outboard_blanket
    )

    # saves the blanket as an stp file
    inboard_blanket.export_stp('blanket.stp')


if __name__ == "__main__":
    make_demo_blanket()
