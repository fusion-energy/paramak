"""
This python script demonstrates the parametric creation of a shape similar to
a breeder blanket.
"""

import paramak


def main(filename="blanket_from_parameters.stp"):

    height = 700
    blanket_rear = 400
    blanket_front = 300
    blanket_mid_point = 350

    blanket = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (blanket_rear, height / 2.0, "straight"),
            (blanket_rear, -height / 2.0, "straight"),
            (blanket_front, -height / 2.0, "spline"),
            (blanket_mid_point, 0, "spline"),
            (blanket_front, height / 2.0, "straight"),
        ]
    )

    blanket.export_stp(filename=filename)


if __name__ == "__main__":
    main()
