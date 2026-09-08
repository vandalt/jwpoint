from pathlib import Path

import numpy as np
import pytest

from jwpoint import utils


def test_filter_nans_replaces_bad_pixels_without_mutating_input():
    image = np.ones((5, 5))
    image[2, 2] = np.nan

    result = utils.filter_nans(image)

    assert result[2, 2] == 1
    assert not np.isnan(result).any()
    assert np.isnan(image[2, 2])


@pytest.mark.parametrize(
    ("x", "y", "detector"),
    [
        (1025, 1025, "nrcb1"),
        (1024, 1025, "nrcb3"),
        (1025, 1024, "nrcb2"),
        (1024, 1024, "nrcb4"),
    ],
)
def test_get_sw_detector_selects_full_frame_quadrant(x, y, detector):
    assert utils.get_sw_detector(x, y, "FULL") == detector


@pytest.mark.parametrize("subarray", ["FULLP", "SUB400P"])
def test_get_sw_detector_handles_supported_subarrays(subarray):
    expected = "nrcb1"

    assert utils.get_sw_detector(1500, 1500, subarray) == expected


def test_get_sw_detector_rejects_unsupported_subarray():
    with pytest.raises(ValueError, match="Only FULL and SUB400P supported"):
        utils.get_sw_detector(0, 0, "SUB160")


def test_download_sw_file_uses_matching_detector_and_lw_directory(
    monkeypatch, tmp_path
):
    lw_path = tmp_path / "jw123_nrcblong_cal.fits"
    downloaded = []

    class FakeHDUList:
        def __enter__(self):
            return [type("FakeHDU", (), {"header": {"SUBARRAY": "FULL"}})()]

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(utils.fits, "open", lambda path: FakeHDUList())
    monkeypatch.setattr(
        utils.Observations,
        "download_file",
        lambda uri, local_path: downloaded.append((uri, local_path)),
    )

    result = utils.download_sw_file(lw_path, x=1500, y=1500)

    expected_path = Path(tmp_path, "jw123_nrcb1_cal.fits")
    assert result == expected_path
    assert downloaded == [("mast:JWST/product/jw123_nrcb1_cal.fits", expected_path)]
