import matplotlib.pyplot as plt
import numpy as np
from typing import Callable
from zebrafishanalysis.structs import TrajectoryObject


def draw_figure(func: Callable) -> Callable:
    """ Decorator to help draw figures

    Args:
        func (Callable): graphing function to perform
    """
    def inner(*args, **kwargs):
        plt.clf()
        func(*args, **kwargs)
        plt.show()
    return inner


@draw_figure
def create_heatmap(trajectories: TrajectoryObject,
                   bins: int,
                   fish_range: tuple = None) -> np.ndarray:
    """Plots a heatmap of fish positions

    Args:
        trajectories (TrajectoryObject): tuple containing two arrays, x and y pos to use
        bins (bool): Number of bins to use when plotting
        fish_range (tuple): Range of fish to run this on. e.g. (0, 0) = fish 0 / (1, 10) = fish 1 to fish 10. Defaults
        to all fish

    Returns:
        TrajectoryObject: Processed trajectories
    """

    x, y = trajectories.flatten_fish_positions(fish_range)

    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=(bins, bins))
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    return plt.imshow(heatmap.T, extent=extent, origin='lower')
