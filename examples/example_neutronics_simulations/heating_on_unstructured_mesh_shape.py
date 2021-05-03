
import paramak


rotated_spline = paramak.RotateSplineShape(
    rotation_angle=180,
    method='trelis',
    points=[
        (500, 0),
        (500, -20),
        (400, -300),
        (300, -300),
        (400, 0),
        (300, 300),
        (400, 300),
        (500, 20),
    ],
    tet_mesh=
)

rotated_spline.export_h5m(
    # merge_tolerance,
    # faceting_tolerance=,
)