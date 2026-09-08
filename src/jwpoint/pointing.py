from pathlib import Path
from typing import TypeAlias

from jwst import datamodels
from stdatamodels.jwst.datamodels import JwstDataModel

from jwpoint.constants import PSCALE_DICT, V2V3_REF_DICT

InputFile: TypeAlias = str | Path | JwstDataModel


def _ensure_model(file: InputFile) -> JwstDataModel:
    """Utility function to ensure that the input file is a JWST data model

    If ``file`` is a data model, it is returned directly.
    Otherwise the file is opened with :func:`jwst.datamodels.open`.

    :param file: The input file path or data model
    :return: The data model
    """
    if not isinstance(file, JwstDataModel):
        return datamodels.open(file)
    else:
        return file


def get_pointing_position(
    xoffset: float,
    yoffset: float,
    file: InputFile,
    offset_frame: str = "detector",
) -> tuple[float, float]:
    """Get the pointing position coordinates with an offset applied

    The pointing position is always returned in detector coordinates (pixels).

    :param xoffset: x or V2 offset [arcsec]
    :param yoffset: y or V3 offset [arcsec]
    :param file: File that will be used to get the WCS
                 and derive the pointing posision
    :param coords: Coordinates in which the transofmration is applied internally.
                   This does not change the output coordinates which are always pixels.
                   Can be ``"detector"`` or ``"v2v3"``.
    :raises ValueError: Raised if an invalid ``coords`` argument is provided
    :return: The pointing detector coordinates in pixels
    """
    model = _ensure_model(file)

    detector = model.meta.instrument.detector
    pscale = PSCALE_DICT[detector]

    aperture = model.meta.aperture.pps_name
    v2_ref, v3_ref = V2V3_REF_DICT[aperture]

    if offset_frame == "detector":
        xref_pix, yref_pix = model.meta.wcs.transform(
            "v2v3", "detector", v2_ref, v3_ref
        )

        xoff_pix = xoffset / pscale
        yoff_pix = yoffset / pscale

        return xref_pix + xoff_pix, yref_pix + yoff_pix

    elif offset_frame == "v2v3":
        v2_point = v2_ref - xoffset
        v3_point = v3_ref + yoffset

        return model.meta.wcs.transform("v2v3", "detector", v2_point, v3_point)
    else:
        raise ValueError(f"coords should be 'detector' or 'v2v3'. Got {offset_frame}")


def calculate_offset(
    xpoint: float,
    ypoint: float,
    file: InputFile,
    coords: str = "detector",
) -> tuple[float, float]:
    """Calculate the applied offset based on the final pointing position

    The offset is always returned in detector coordinates (X-Y) with units of arcseconds.

    :param xoffset: x pointing position [pixel or arcsec]
    :param yoffset: y pointing position [pixel or arcsec]
    :param file: File that will be used to get the WCS
                 and derive the offsets.
    :param coords: Coordinates in which the transofmration is applied internally.
                   This does not change the output coordinates which are always arcsec.
                   Can be ``"detector"`` or ``"v2v3"``.
    :raises ValueError: Raised if an invalid ``coords`` argument is provided
    :return: The offset applied to the reference position
    """
    model = _ensure_model(file)

    detector = model.meta.instrument.detector
    pscale = PSCALE_DICT[detector]

    aperture = model.meta.aperture.pps_name
    v2_ref, v3_ref = V2V3_REF_DICT[aperture]

    if coords == "detector":
        xref_pix, yref_pix = model.meta.wcs.transform(
            "v2v3", "detector", v2_ref, v3_ref
        )

        xoff_pix = xpoint - xref_pix
        yoff_pix = ypoint - yref_pix

        xoff_arcsec = xoff_pix * pscale
        yoff_arcsec = yoff_pix * pscale
    elif coords == "v2v3":
        v2_point, v3_point = model.meta.wcs.transform(
            "detector", "v2v3", xpoint, ypoint
        )

        v2_off = v2_point - v2_ref
        v3_off = v3_point - v3_ref

        xoff_arcsec = -v2_off
        yoff_arcsec = v3_off
    else:
        raise ValueError(f"coords should be 'detector' or 'v2v3'. Got {coords}")

    return xoff_arcsec, yoff_arcsec


def long_to_short(
    x: float, y: float, file_lw: InputFile, file_sw: InputFile
) -> tuple[float, float]:
    """Convert position from the long- to short-wavelength channel for NIRCam

    The long-wavelenth (LW) X-Y detector position is converted to V2-V3 using
    the LW file. This is then converted to short-wavelength (SW)
    X-Y detector position using the SW file.

    :param x: X position in the LW channel
    :param y: Y position in the SW channel
    :param file_lw: LW file to use for WCS
    :param file_sw: SW file to use for WCS
    :return: The X and Y positions in SW
    """
    model_lw = _ensure_model(file_lw)
    model_sw = _ensure_model(file_sw)

    v2, v3 = model_lw.meta.wcs.transform("detector", "v2v3", x, y)
    x_sw, y_sw = model_sw.meta.wcs.transform("v2v3", "detector", v2, v3)

    return x_sw, y_sw


def xy_to_v2v3(x: float, y: float, model: InputFile) -> tuple[float, float]:
    """Convert X-Y detector position to V2-V3

    :param x: X position in detector coordinates
    :param y: Y position in detector coordinates
    :param model: File used to define WCS
    :return: V2 and V3 cooordinates
    """
    model = _ensure_model(model)
    return model.meta.wcs.transform("detector", "v2v3", x, y)


def v2v3_to_xy(v2: float, v3: float, model: InputFile) -> tuple[float, float]:
    """Convert V2-V3 coordinates to detector position

    :param v2: V2 position
    :param v3: V3 position
    :param model: File used to define WCS coordinates
    :return: x and y detector coordinates
    """
    model = _ensure_model(model)
    return model.meta.wcs.transform("v2v3", "detector", v2, v3)
