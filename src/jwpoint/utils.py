from pathlib import Path

import numpy as np
from astropy.io import fits
from astroquery.mast import Observations
from scipy.ndimage import median_filter


def filter_nans(img_crop: np.ndarray) -> np.ndarray:
    """Fix bad pixel in a cropped image via median filter

    This function uses :func:`scipy.ndimage.median_filter`,
    but it sets the NaNs to zero beforehand to avoid propagation.

    :param img_crop: Cropped image of a PSF
    :return: The image with bad pixels replaced by median filter
    """
    img_crop_clean = img_crop.copy()
    nan_crop_mask = np.isnan(img_crop)
    img_crop_clean[nan_crop_mask] = 0.0
    img_crop_clean[nan_crop_mask] = median_filter(img_crop_clean, size=5)[nan_crop_mask]
    return img_crop_clean


def get_sw_detector(x: int, y: int, subarray: str) -> str:
    """Get the short-wavelength detector for a given long-wavelength position

    .. warning::

       Only ``FULL`` and ``SUB400P`` subarrays are supported. Support for
       additional subarrays has not yet been implemented.

    :param x: X position in the long-wavelength channel
    :param y: Y position in the long-wavelength channel
    :param subarray: Subarray in the long-wavelength channel
    :raises ValueError: Raises an error if an unsupported subarray is passed
    :return: The short-wavelength detector name in lowercase
    """
    if subarray == "FULL" or subarray == "FULLP":
        npix = 2048
        top = y > npix // 2
        right = x > npix // 2
        if top and right:
            det_sw = "nrcb1"
        elif top and not right:
            det_sw = "nrcb3"
        elif not top and right:
            det_sw = "nrcb2"
        elif not top and not right:
            det_sw = "nrcb4"
    elif subarray == "SUB400P":
        det_sw = "nrcb1"
    else:
        raise ValueError(
            f"Unexpected subarray {subarray}. Only FULL and SUB400P supported."
        )
    return det_sw


def download_sw_file(lw_path: Path | str, x: int, y: int) -> Path:
    """Download the SW file associated with a LW file and a pointing

    The LW subarray is inferred from the LW file and the directory
    is the same as for the LW file.

    :param lw_path: Full path to the LW file
    :param x: X position in the LW image
    :param y: Y position in the LW image
    :return: Full path to the SW file
    """
    lw_path = Path(lw_path)

    with fits.open(lw_path) as hdul:
        subarray = hdul[0].header["SUBARRAY"]
    detector_sw = get_sw_detector(x, y, subarray)

    filename_sw = lw_path.name.replace("nrcblong", detector_sw)

    uri = f"mast:JWST/product/{filename_sw}"

    filepath_sw = lw_path.parent / filename_sw

    _ = Observations.download_file(uri, local_path=filepath_sw)
    return filepath_sw
