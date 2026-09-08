import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from jwpoint.constants import PSCALE_DICT
from jwpoint.dithers import get_dither_info


@pytest.fixture
def expected_offsets():
    return DataFrame(
        {
            "x": [-0.335, 0.335, -0.295, 0.295],
            "y": [-0.335, 0.335, 0.295, -0.295],
        }
    )


def test_get_dither_info_returns_subarray_offsets(expected_offsets):
    result = get_dither_info("SUBARRAY_DITHER")

    assert_frame_equal(result, expected_offsets)


def test_get_dither_info_limits_number_of_dithers(expected_offsets):
    result = get_dither_info("SUBARRAY_DITHER", n_dithers=2)

    assert_frame_equal(result, expected_offsets.iloc[:2])


def test_get_dither_info_converts_offsets_to_detector_pixels(expected_offsets):
    detector = "NRCBLONG"
    result = get_dither_info("SUBARRAY_DITHER", detector=detector)

    assert_frame_equal(result, expected_offsets / PSCALE_DICT[detector])


def test_get_dither_info_rejects_unknown_pattern():
    with pytest.raises(KeyError):
        get_dither_info("UNKNOWN")
