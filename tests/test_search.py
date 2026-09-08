import numpy as np
import pytest
from pandas import DataFrame

from jwpoint.search import _shift_with_fill, do_region_search, find_regions


def test_shift_with_fill_samples_offset_pixels_and_fills_edges():
    array = np.arange(9).reshape(3, 3)

    result = _shift_with_fill(array, dx=1, dy=-1, fill_value=-1)

    assert np.array_equal(result, [[-1, -1, -1], [1, 2, -1], [4, 5, -1]])


def test_find_regions_returns_non_overlapping_xy_positions():
    x, y = find_regions(
        np.zeros((10, 10), dtype=bool), window_size=2, n_top=2, min_edge_distance=2
    )

    assert np.array_equal(x, [2, 4])
    assert np.array_equal(y, [2, 2])


def test_find_regions_marks_forbidden_pixels_invalid_in_weighted_result():
    mask = np.zeros((11, 11), dtype=bool)
    mask[5, 5] = True

    _, _, weighted = find_regions(
        mask,
        window_size=3,
        forbidden_size=1,
        min_edge_distance=3,
        return_weighted=True,
    )

    assert np.isinf(weighted[5, 5])


def test_find_regions_accepts_dataframe_joint_offsets():
    offsets = DataFrame({"x": [0, 1], "y": [0, 0]})

    x, y = find_regions(
        np.zeros((10, 10), dtype=bool),
        window_size=2,
        joint_offsets=offsets,
        n_top=1,
        min_edge_distance=2,
    )

    np.testing.assert_array_equal(x, [[2, 3]])
    np.testing.assert_array_equal(y, [[2, 2]])


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"kernel": "invalid"}, "Invalid kernel"),
        ({"forbidden_size": 3}, "must be smaller"),
        ({"joint_offsets": np.zeros((2, 3))}, "shape"),
        ({"subarray": "SUB160"}, "Only FULL"),
    ],
)
def test_find_regions_rejects_invalid_arguments(kwargs, error):
    with pytest.raises(ValueError, match=error):
        find_regions(
            np.zeros((10, 10), dtype=bool),
            window_size=3,
            min_edge_distance=3,
            **kwargs,
        )


def test_do_region_search_returns_best_position_without_displaying_plots():
    x, y = do_region_search(
        np.zeros((10, 10), dtype=bool),
        np.ones((10, 10)),
        region_size=2,
        psf=np.ones((2, 2)),
        n_top=1,
        min_edge_distance=2,
        show=False,
    )

    assert np.array_equal(x, [2])
    assert np.array_equal(y, [2])
