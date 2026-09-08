from importlib.resources import files

from pandas import DataFrame, read_csv

from jwpoint.constants import PSCALE_DICT

__all__ = ["get_dither_info"]

DITHER_FILES = {
    "INTRAMODULEBOX": "NircamImagingIntramoduleBox.txt",
    "SUBARRAY_DITHER": "NircamImagingSubarrayDither.txt",
}


def get_dither_info(
    pattern: str, n_dithers: int | None = None, detector: str | None = None
) -> DataFrame:
    data_dir = files("jwpoint") / "data"
    filepath = data_dir / DITHER_FILES[pattern]
    dither_df = read_csv(
        filepath,
        sep=r"\s+",
        skiprows=1,
        header=None,
        names=["x", "y"],
        index_col=0,
    ).reset_index(drop=True)[:n_dithers]
    if detector is None:
        return dither_df
    pscale = PSCALE_DICT[detector]
    dither_df.x = dither_df.x / pscale
    dither_df.y = dither_df.y / pscale
    return dither_df
