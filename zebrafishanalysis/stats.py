import matplotlib.pyplot as plt
import numpy as np
from typing import Callable
from zebrafishanalysis.structs import TrajectoryObject, NovelObjectRecognitionTest


def draw_figure(func: Callable) -> Callable:
    """ Decorator to help draw figures

    Args:
        func (Callable): graphing function to perform
    """
    def inner(*args, **kwargs):
        plt.clf()
        if isinstance(args[0], TrajectoryObject) or isinstance(args[0], NovelObjectRecognitionTest):
            trajectories = args[0].flatten_fish_positions()
        else:
            trajectories = args[0]
        func(trajectories, *args[1:], **kwargs)
        plt.show()
    return inner


@draw_figure
def create_heatmap(trajectories: np.ndarray or TrajectoryObject,
                   bins: int,
                   fish_range: slice = None) -> np.ndarray:
    """Plots a heatmap of fish positions

    Args:
        trajectories (TrajectoryObject): tuple containing two arrays, x and y pos to use
        bins (bool): Number of bins to use when plotting
        fish_range (tuple): Range of fish to run this on. e.g. (0, 0) = fish 0 / (1, 10) = fish 1 to fish 10. Defaults
        to all fish

    Returns:
        TrajectoryObject: Processed trajectories
    """

    x, y = trajectories[:, 0], trajectories[:, 1]

    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=(bins, bins))
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    return plt.imshow(heatmap.T, extent=extent, origin='lower')


def get_measures(same_pref: tuple,
                 diff_pref: tuple) -> dict:

    e1 = same_pref[0] + same_pref[1]
    e2 = diff_pref[0] + diff_pref[1]

    d1 = diff_pref[1] - diff_pref[0]
    d2 = d1 / e2
    d3 = diff_pref[1] / e2

    return {"e1": e1,
            "e2": e2,
            "d1": d1,
            "d2": d2,
            "d3": d3}

