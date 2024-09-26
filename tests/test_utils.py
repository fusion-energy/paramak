import pytest

from paramak.utils import (
    ValidationError,
    get_gap_after_plasma,
    get_plasma_value,
    sum_after_gap_following_plasma,
    sum_up_to_plasma,
    validate_divertor_radial_build,
    validate_plasma_radial_build,
)


def test_validate_divertor_radial_build_valid():
    radial_build = [("gap", 10), ("lower_divertor", 20)]
    assert validate_divertor_radial_build(radial_build) is None


def test_validate_divertor_radial_build_invalid_length():
    radial_build = [("gap", 10)]
    with pytest.raises(ValidationError, match="should only contain two entries"):
        validate_divertor_radial_build(radial_build)


def test_validate_divertor_radial_build_invalid_tuple_length():
    radial_build = [("gap", 10, 5), ("lower_divertor", 20)]
    with pytest.raises(ValidationError, match="should only contain tuples of length 2"):
        validate_divertor_radial_build(radial_build)


def test_validate_divertor_radial_build_invalid_second_entry():
    radial_build = [("gap", 10), ("divertor", 20)]
    with pytest.raises(ValidationError, match='should be either "lower_divertor" or "upper_divertor"'):
        validate_divertor_radial_build(radial_build)


def test_validate_divertor_radial_build_invalid_first_entry():
    radial_build = [("layer", 10), ("lower_divertor", 20)]
    with pytest.raises(ValidationError, match='should be a "gap"'):
        validate_divertor_radial_build(radial_build)


def test_validate_divertor_radial_build_non_positive_thickness():
    radial_build = [("gap", -10), ("lower_divertor", 20)]
    with pytest.raises(ValidationError, match="should both be positive values"):
        validate_divertor_radial_build(radial_build)


def test_validate_divertor_radial_build_invalid_thickness_type():
    radial_build = [("gap", "10"), ("lower_divertor", 20)]
    with pytest.raises(ValidationError, match="should both be integers or floats"):
        validate_divertor_radial_build(radial_build)


def test_get_plasma_value():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert get_plasma_value(radial_build) == 50


def test_get_plasma_value_not_found():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValueError, match="'plasma' entry not found"):
        get_plasma_value(radial_build)


def test_valid_case():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    validate_plasma_radial_build(radial_build)  # Should not raise an error


def test_plasma_not_preceded_by_gap():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="'plasma' entry must be preceded and followed by a 'gap'"):
        validate_plasma_radial_build(radial_build)


def test_plasma_not_followed_by_gap():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            5,
        ),
        (
            "plasma",
            50,
        ),
        (
            "layer",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="'plasma' entry must be preceded and followed by a 'gap'"):
        validate_plasma_radial_build(radial_build)


def test_missing_plasma():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="'plasma' entry not found or found multiple times"):
        validate_plasma_radial_build(radial_build)


def test_multiple_plasma():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="Multiple 'plasma' entries found"):
        validate_plasma_radial_build(radial_build)


def test_first_entry_not_string():
    radial_build = [
        (
            10,
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="Invalid tuple structure at index 0"):
        validate_plasma_radial_build(radial_build)


def test_second_entry_not_number():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            "50",
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="Invalid tuple structure at index 1"):
        validate_plasma_radial_build(radial_build)


def test_invalid_string():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "invalid",
            5,
        ),  # Invalid string
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="Invalid string 'invalid' at index 2"):
        validate_plasma_radial_build(radial_build)


def test_plasma_first_entry():
    radial_build = [
        (
            "plasma",
            50,
        ),
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="'plasma' entry must have at least one entry before and after it"):
        validate_plasma_radial_build(radial_build)


def test_plasma_last_entry():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
        (
            "plasma",
            50,
        ),
    ]
    with pytest.raises(ValidationError, match="'plasma' entry must have at least one entry before and after it"):
        validate_plasma_radial_build(radial_build)


def test_non_positive_values():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            0,
        ),  # Non-positive value
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValidationError, match="Non-positive value '0' at index 2"):
        validate_plasma_radial_build(radial_build)


def test_sum_up_to_plasma_middle():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert sum_up_to_plasma(radial_build) == 115


def test_sum_up_to_plasma_first():
    radial_build = [
        (
            "plasma",
            50,
        ),
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert sum_up_to_plasma(radial_build) == 0


def test_sum_up_to_plasma_last():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
        (
            "plasma",
            50,
        ),
    ]
    assert sum_up_to_plasma(radial_build) == 191


def test_sum_up_to_plasma_not_present():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "layer",
            5,
        ),
        (
            "gap",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert sum_up_to_plasma(radial_build) == 191


def test_sum_up_to_plasma_empty():
    radial_build = []
    assert sum_up_to_plasma(radial_build) == 0


def test_sum_up_to_plasma_multiple_entries():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            20,
        ),
        (
            "layer",
            30,
        ),
        (
            "gap",
            40,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert sum_up_to_plasma(radial_build) == 100


def test_get_gap_after_plasma_not_followed_by_gap():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            5,
        ),
        (
            "plasma",
            50,
        ),
        (
            "layer",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValueError, match="'plasma' entry is not followed by a 'gap'"):
        get_gap_after_plasma(radial_build)


def test_get_gap_after_plasma_not_found():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            5,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValueError, match="'plasma' entry not found"):
        get_gap_after_plasma(radial_build)


def test_sum_after_gap_following_plasma():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            5,
        ),
        (
            "plasma",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    assert sum_after_gap_following_plasma(radial_build) == 16


def test_sum_after_gap_following_plasma_not_found():
    radial_build = [
        (
            "gap",
            10,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            5,
        ),
        (
            "layer",
            50,
        ),
        (
            "gap",
            60,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "layer",
            2,
        ),
        (
            "gap",
            10,
        ),
    ]
    with pytest.raises(ValueError, match="'plasma' entry not found"):
        sum_after_gap_following_plasma(radial_build)
