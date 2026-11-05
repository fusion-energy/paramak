import pytest

import paramak

L = paramak.LayerType


def test_tokamak_without_extra_inboard_layers():
    "every inboard solid is paired with an outboard one, so there are no centre column cylinders"

    reactor = paramak.tokamak_from_plasma(
        radial_build=[(L.GAP, 100), (L.SOLID, 20), (L.GAP, 10), (L.PLASMA, 200), (L.GAP, 10), (L.SOLID, 20)],
        rotation_angle=90,
    )
    assert reactor.names() == ["layer_1", "plasma"]


def test_tokamak_without_extra_inboard_layers_and_intersect_shape():
    divertor = paramak.poloidal_field_coil(height=100, width=100, center_point=(250, -200), rotation_angle=90)
    reactor = paramak.tokamak_from_plasma(
        radial_build=[(L.GAP, 100), (L.SOLID, 20), (L.GAP, 10), (L.PLASMA, 200), (L.GAP, 10), (L.SOLID, 20)],
        rotation_angle=90,
        extra_intersect_shapes=[divertor],
    )
    assert "poloidal_field_coil_1" in reactor.names()


@pytest.mark.parametrize(
    "radial_build",
    [
        [(L.GAP, 50), (L.PLASMA, 300), (L.GAP, 10), (L.SOLID, 20)],
        [(L.GAP, 10), (L.GAP, 50), (L.PLASMA, 300), (L.GAP, 10), (L.SOLID, 20)],
    ],
)
def test_spherical_tokamak_needs_a_centre_column(radial_build):
    with pytest.raises(ValueError, match="needs at least one LayerType.SOLID before"):
        paramak.spherical_tokamak_from_plasma(radial_build=radial_build, rotation_angle=90)
