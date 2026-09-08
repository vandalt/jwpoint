from types import SimpleNamespace

import pytest

from jwpoint import pointing
from jwpoint.constants import PSCALE_DICT, V2V3_REF_DICT


class FakeWCS:
    def __init__(self, v2_offset=0, v3_offset=0):
        self.v2_offset = v2_offset
        self.v3_offset = v3_offset
        self.calls = []

    def transform(self, source, target, first, second):
        self.calls.append((source, target, first, second))
        if (source, target) == ("v2v3", "detector"):
            return first - self.v2_offset, second - self.v3_offset
        if (source, target) == ("detector", "v2v3"):
            return first + self.v2_offset, second + self.v3_offset
        raise ValueError("unsupported transform")


@pytest.fixture
def model():
    return SimpleNamespace(
        meta=SimpleNamespace(
            instrument=SimpleNamespace(detector="NRCBLONG"),
            aperture=SimpleNamespace(pps_name="NRCB5_FULLP"),
            wcs=FakeWCS(v2_offset=10, v3_offset=20),
        )
    )


@pytest.fixture(autouse=True)
def use_provided_models(monkeypatch):
    monkeypatch.setattr(pointing, "_ensure_model", lambda model: model)


def test_get_pointing_position_applies_detector_pixel_offsets(model):
    xoffset, yoffset = 0.126, 0.189
    v2_ref, v3_ref = V2V3_REF_DICT["NRCB5_FULLP"]
    wcs = model.meta.wcs

    result = pointing.get_pointing_position(xoffset, yoffset, model)

    assert result == pytest.approx(
        (
            v2_ref - wcs.v2_offset + xoffset / PSCALE_DICT["NRCBLONG"],
            v3_ref - wcs.v3_offset + yoffset / PSCALE_DICT["NRCBLONG"],
        )
    )


def test_get_pointing_position_applies_v2v3_sign_convention(model):
    v2_ref, v3_ref = V2V3_REF_DICT["NRCB5_FULLP"]
    wcs = model.meta.wcs

    result = pointing.get_pointing_position(0.5, 0.25, model, offset_frame="v2v3")

    assert result == pytest.approx(
        (v2_ref - 0.5 - wcs.v2_offset, v3_ref + 0.25 - wcs.v3_offset)
    )


def test_calculate_offset_converts_detector_pixels_to_arcseconds(model):
    v2_ref, v3_ref = V2V3_REF_DICT["NRCB5_FULLP"]
    wcs = model.meta.wcs
    xref, yref = v2_ref - wcs.v2_offset, v3_ref - wcs.v3_offset

    result = pointing.calculate_offset(xref + 2, yref + 3, model)

    assert result == pytest.approx(
        (2 * PSCALE_DICT["NRCBLONG"], 3 * PSCALE_DICT["NRCBLONG"])
    )


def test_calculate_offset_applies_v2v3_sign_convention(model):
    v2_ref, v3_ref = V2V3_REF_DICT["NRCB5_FULLP"]
    wcs = model.meta.wcs

    result = pointing.calculate_offset(
        v2_ref - 0.5 - wcs.v2_offset,
        v3_ref + 0.25 - wcs.v3_offset,
        model,
        "v2v3",
    )

    assert result == pytest.approx((0.5, 0.25))


@pytest.mark.parametrize(
    ("function", "kwargs"),
    [
        (pointing.get_pointing_position, {"xoffset": 0, "yoffset": 0, "offset_frame": "sky"}),
        (pointing.calculate_offset, {"xpoint": 0, "ypoint": 0, "coords": "sky"}),
    ],
)
def test_offset_functions_reject_invalid_coordinate_frames(function, kwargs, model):
    with pytest.raises(ValueError, match="detector.*v2v3"):
        function(file=model, **kwargs)


def test_long_to_short_converts_through_telescope_coordinates():
    lw_model = SimpleNamespace(meta=SimpleNamespace(wcs=FakeWCS(10, 20)))
    sw_model = SimpleNamespace(meta=SimpleNamespace(wcs=FakeWCS(100, 200)))

    x, y = 5, 7
    assert pointing.long_to_short(x, y, lw_model, sw_model) == (
        x + lw_model.meta.wcs.v2_offset - sw_model.meta.wcs.v2_offset,
        y + lw_model.meta.wcs.v3_offset - sw_model.meta.wcs.v3_offset,
    )


def test_wcs_wrapper_functions_delegate_to_model(model):
    x, y = 5, 7
    wcs = model.meta.wcs

    assert pointing.xy_to_v2v3(x, y, model) == (
        x + wcs.v2_offset,
        y + wcs.v3_offset,
    )
    assert pointing.v2v3_to_xy(
        x + wcs.v2_offset, y + wcs.v3_offset, model
    ) == (x, y)
