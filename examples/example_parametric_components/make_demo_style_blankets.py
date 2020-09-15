import math
import numpy as np
import paramak

number_of_segments = 8
large_dimention=10000
gap_size = 10.
central_block_width = 200

offset = (360 / number_of_segments)/ 2
plasma = paramak.Plasma(
    elongation = 1.59,
    triangularity=0.33,
    major_radius=910,
    minor_radius=290)
plasma.solid

parallel_outboard_gaps_inner = paramak.ExtrudeStraightShape(
    points=[(large_dimention,large_dimention),
            (large_dimention,-large_dimention),
            (0,-large_dimention),
            (0,large_dimention),
    ],
    distance=central_block_width,
    azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False)
)

parallel_outboard_gaps_outer = paramak.ExtrudeStraightShape(
    points=[(large_dimention,large_dimention),
            (large_dimention,-large_dimention),
            (0,-large_dimention),
            (0,large_dimention),
    ],
    distance=central_block_width+(gap_size*2),
    azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False),
    cut=parallel_outboard_gaps_inner
)

inboard_to_outboard_gaps = paramak.ExtrudeStraightShape(
    points=[(plasma.high_point[0]-(0.5*gap_size),plasma.high_point[1]),
            (plasma.high_point[0]-(0.5*gap_size),plasma.high_point[1]+1000),
            (plasma.high_point[0]+(0.5*gap_size),plasma.high_point[1]+1000),
            (plasma.high_point[0]+(0.5*gap_size),plasma.high_point[1]),
    ],
    distance=math.tan(math.radians(360/(2*number_of_segments)))*plasma.high_point[0]*2,
    azimuth_placement_angle=np.linspace(0, 360, number_of_segments, endpoint=False)
)

outboard_gaps = paramak.ExtrudeStraightShape(
    points=[(large_dimention,large_dimention),
            (large_dimention,-large_dimention),
            (0,-large_dimention),
            (0,large_dimention),
    ],
    distance=gap_size,
    azimuth_placement_angle=np.linspace(0+offset, 360+offset, number_of_segments, endpoint=False)
)

outboard_blanket = paramak.BlanketFP(
    plasma=plasma,
    thickness=100,
    stop_angle=90,
    start_angle=-60,
    offset_from_plasma=30,
    rotation_angle=360,
    cut = [outboard_gaps, parallel_outboard_gaps_outer, inboard_to_outboard_gaps]
)

inboard_gaps = paramak.ExtrudeStraightShape(
    points=[(large_dimention,large_dimention),
            (large_dimention,-large_dimention),
            (0,-large_dimention),
            (0,large_dimention),
    ],
    distance=gap_size,
    azimuth_placement_angle=np.linspace(0, 360, number_of_segments*2, endpoint=False)
)

inboard_blanket = paramak.BlanketFP(
    plasma=plasma,
    thickness=100,
    stop_angle=90,
    start_angle=260,
    offset_from_plasma=30,
    rotation_angle=360,
    cut = [inboard_gaps, inboard_to_outboard_gaps],
    union = outboard_blanket
)

inboard_blanket.export_stp('blanket.stp')
