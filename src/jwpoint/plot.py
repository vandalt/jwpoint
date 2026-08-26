from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def zoom_plot(
    img: np.ndarray,
    x: int,
    y: int,
    size: int,
    axs: np.ndarray[Axes] | None = None,
    show_mask: bool = True,
    psf: np.ndarray | None = None,
) -> np.ndarray:
    """Zoomed plot on a region of an image

    Also plots the NaN mask on a second panel, optionally with a reference PSF
    to see where bad pixels would fall on a point source image in that region.

    The mask can be turned off with ``show_mask=False``.

    :param img: The full image as a 2D array
    :param x: x coordinates of the image center
    :param y: y coordinate of the image center
    :param size: The size of the region to crop
    :param show_mask: Show the bad pixel mask if True
    :param axs: Two Axes on which the plots should go.
                Fetch from the current figure if None.
                Defaults to None.
    :param psf: Image of a reference PSF as a 2D array.
                Must have a shape ``(size,  size)``.
                Defalts to None.
    :return: The boolean mask indicating NaNs in the final zoomed in region.
    """
    axs = axs if axs is not None else plt.gcf().axes
    if show_mask and len(axs) == 0:
        plt.close()
        _, axs = plt.subplots(1, 2, figsize=(10, 5))
    elif len(axs) == 0:
        axs = [plt.gca()]
    hs = size // 2
    region = img[y - hs : y + hs, x - hs : x + hs]
    axs[0].imshow(region, norm="symlog")

    region_mask = np.isnan(region)
    if not show_mask:
        return region_mask

    if psf is not None and psf.shape == region.shape:
        img_with_bad = psf.copy()
        img_with_bad[region_mask] = np.nan
        axs[1].imshow(img_with_bad, norm="symlog")
    else:
        axs[1].imshow(region_mask)
    return region_mask


# TODO: Check that zoom_plot renders here
def plot_dithers(
    img: np.ndarray,
    xopt_all: Iterable[int],
    yopt_all: Iterable[int],
    size: int,
    full_frame: bool = True,
    show_mask: bool = True,
    psf: np.ndarray | None = None,
) -> tuple[Figure, Figure]:
    """Plot the pointing for multiple dithers

    This function produces two plots:

    - A full image with the dithers marked by their pattern number
    - A figure with a zoomed-in view on each dither using :func:`zoom_plot`.

    :param img: The full-frame image
    :param xopt_all: The x position of each dither
    :param yopt_all: The y position of each dither
    :param size: The size to use for the zoomed-in plots
    :param full_frame: Show the full frame image with the dithers on it.
    :param show_mask: Show the bad pixel mask for each dither if True
    :param psf: A PSF with shape ``(size, size)`` to visualize a point source
                in the region corresponding to each dither. Only the bad pixel
                mask is shown if no PSF is passsed. Defaults to None.
    :return: The two figures (full frame and zoomed-in)
    """
    xopt_all = list(map(int, xopt_all))
    yopt_all = list(map(int, yopt_all))
    ndithers = len(xopt_all)
    if full_frame:
        fig_full = plt.figure()
        plt.imshow(img, norm="symlog")
        for i in range(ndithers):
            plt.scatter(xopt_all[i], yopt_all[i], marker=f"${i + 1}$", color="r")

    fig_zoom, axs = plt.subplots(
        2 if show_mask else 1, ndithers, figsize=(10, 5), squeeze=False
    )
    for i in range(ndithers):
        region_mask = zoom_plot(
            img,
            xopt_all[i],
            yopt_all[i],
            size,
            axs=axs[:, i],
            psf=psf,
            show_mask=show_mask,
        )
        nbad = np.sum(region_mask)
        axs[0, i].set_title(f"Dither {i + 1}: {nbad} DQ")
    if full_frame:
        return fig_full, fig_zoom
    else:
        return fig_zoom
