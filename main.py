"""
Visualize elevation data from TIF files using matplotlib
Focus on San Diego area with custom colormap for below-sea-level areas
"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import rasterio
from rasterio.plot import show
from rasterio.windows import from_bounds
import numpy as np
from pathlib import Path


def zoom_to_location(
    tif_path,
    threshold_m: int = 1,
    lon: tuple[str, str] = (-118.5, -116.5),
    lat: tuple[str, str] = (32.5, 34.0),
):
    """
    Zoom in on a specific location and visualize elevation data

    Args:
        tif_path: Path to the TIF file
    """
    # San Diego approximate bounds (lon, lat)
    # Downtown San Diego is roughly at 32.7157°N, 117.1611°W

    with rasterio.open(tif_path) as src:
        # Read window for San Diego area
        window = from_bounds(lon[0], lat[0], lon[1], lat[1], src.transform)
        elevation = src.read(1, window=window)

        # Get the transform for the windowed area
        window_transform = src.window_transform(window)

        # Count pixels below threshold
        below_threshold = np.sum(elevation < threshold_m)
        total_pixels = elevation.size
        pct_below = (below_threshold / total_pixels) * 100

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 12))

        # Create masked array for below threshold
        below_mask = elevation < threshold_m

        # Plot main terrain (only areas above threshold)
        im = ax.imshow(
            elevation,
            cmap="Greys_r",
            interpolation="bilinear",
            vmin=threshold_m,
            vmax=np.nanmax(elevation),
        )

        # Overlay white for areas below threshold
        below_overlay = np.ma.masked_where(~below_mask, elevation)
        im_below = ax.imshow(
            below_overlay,
            cmap="Greys_r",
            interpolation="bilinear",
            vmin=np.nanmin(elevation),
            vmax=threshold_m,
            alpha=0.9,
        )

        # Remove axes, labels, and gridlines
        ax.axis("off")

        plt.tight_layout(pad=0)
        return fig, ax, elevation


if __name__ == "__main__":
    # Set data directory
    data_dir = "data/sd-data"

    # Use mean elevation for cleaner visualization
    tif_file = "data/sd-data/30n120w_20101117_gmted_mea075.tif"

    fig, ax, elevation = zoom_to_location(
        tif_file,
        lat=(32.5, 33.5),
        lon=(-117.3, -116.2),
    )
    plt.savefig("elevation.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
