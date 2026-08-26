from importlib.resources import files

from pandas import DataFrame, read_csv

DITHER_FILES = {
    "INTRAMODULEBOX": "NircamImagingIntramoduleBox.txt",
    "SUBARRAY_DITHER": "NircamImagingSubarrayDither.txt",
}


def get_dither_info(pattern: str, ndithers: int | None = None) -> DataFrame:
    data_dir = files("jwpoint") / "data"
    filepath = data_dir / DITHER_FILES[pattern]
    dither_df = read_csv(
        filepath,
        sep=r"\s+",
        skiprows=1,
        header=None,
        names=["x", "y"],
        index_col=0,
    ).reset_index(drop=True)[:ndithers]
    return dither_df
