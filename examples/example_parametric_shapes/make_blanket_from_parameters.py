"""
This python script demonstrates the parametric creation of a breeder blanket
"""

import paramak

def main():

    height = 700
    blanket_rear = 400
    blanket_front = 300
    blanket_mid_point = 350

    blanket = paramak.RotateMixedShape(
        points=[
            (blanket_rear, height / 2.0, "straight"),
            (blanket_rear, -height / 2.0, "straight"),
            (blanket_front, -height / 2.0, "spline"),
            (blanket_mid_point, 0, "spline"),
            (blanket_front, height / 2.0, "straight"),
        ]
    )

    blanket.rotation_angle = 180
    blanket.export_stp("blanket_from_parameters.stp")

if __name__ == "__main__":
    main()