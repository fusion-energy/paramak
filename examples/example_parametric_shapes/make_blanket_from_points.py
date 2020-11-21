"""
This python script demonstrates the creation of a breeder blanket from points
"""

from paramak


def main(filename="blanket_from_points.stp"):

    blanket = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (538, 305, "straight"),
            (538, -305, "straight"),
            (322, -305, "spline"),
            (470, 0, "spline"),
            (322, 305, "straight"),
        ]
    )

    blanket.export_stp(filename=filename)


if __name__ == "__main__":
    main()
