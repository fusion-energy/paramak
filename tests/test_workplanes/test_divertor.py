import pytest

from paramak.workplanes.divertor import divertor


def make_divertor(start_angle):
    return divertor(
        poloidal_start_angle=start_angle,
        poloidal_extent_angle=30,
        divertor_layer_names=["test_divertor"],
        divertor_layer_thicknesses=[50],
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        elongation=2,
        plasma_facing_offset=lambda theta: 60,
        rotation_angle=180,
    )[0]


def test_poloidal_start_angle_changes_divertor_position():
    top_divertor = make_divertor(90).val()
    bottom_divertor = make_divertor(270).val()

    assert top_divertor.isValid()
    assert bottom_divertor.isValid()
    assert top_divertor.BoundingBox().zmin > 0
    assert bottom_divertor.BoundingBox().zmax < 0


def test_divertor_supports_multiple_named_layers():
    layers = divertor(
        poloidal_start_angle=85,
        poloidal_extent_angle=30,
        divertor_layer_names=["armor", "heatsink", "shield"],
        divertor_layer_thicknesses=[0.2, 10, 50],
        major_radius=450,
        minor_radius=150,
        triangularity=0.55,
        elongation=2,
        plasma_facing_offset=lambda theta: 60,
        rotation_angle=180,
    )

    assert [layer.name for layer in layers] == ["armor", "heatsink", "shield"]
    assert all(layer.val().isValid() and layer.val().Volume() > 0 for layer in layers)
    assert layers[0].val().Volume() < layers[1].val().Volume() < layers[2].val().Volume()


@pytest.mark.parametrize(
    "names,thicknesses",
    [([], []), (["armor"], []), ([""], [1])],
)
def test_divertor_rejects_invalid_layer_definitions(names, thicknesses):
    with pytest.raises(ValueError):
        divertor(
            poloidal_start_angle=85,
            poloidal_extent_angle=30,
            divertor_layer_names=names,
            divertor_layer_thicknesses=thicknesses,
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
            plasma_facing_offset=lambda theta: 60,
            rotation_angle=180,
        )
