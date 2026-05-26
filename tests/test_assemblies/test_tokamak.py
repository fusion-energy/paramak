import paramak
import pytest


def test_colors():
    "passing in the colors dictionary should not raise an error"

    paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
        colors={
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": (1., 0.7, 0.8, 0.6),
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
        }
    )


def test_tokamak_no_inner_layers_error():
    radial_build = [
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.PLASMA, 100),
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 20),
    ]
    vertical_build = [
        (paramak.LayerType.GAP, 20),
        (paramak.LayerType.PLASMA, 200),
        (paramak.LayerType.GAP, 20),
    ]

    with pytest.raises(ValueError, match="No inner SOLID layers found before the plasma"):
        paramak.tokamak(
            radial_build=radial_build,
            vertical_build=vertical_build,
            rotation_angle=180,
        )