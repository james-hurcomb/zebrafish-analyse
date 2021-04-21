import matplotlib.pyplot as plt
import numpy as np
from typing import Callable
from zebrafishanalysis.structs import TrajectoryObject, NovelObjectRecognitionTest
from scipy import stats


def draw_figure(func: Callable) -> Callable:
    """
    Decorator to help draw figures. Clears canvas, plots figure
    :param func: graphing function to perform
    :return: graphed function
    """
    def inner(*args, **kwargs):
        plt.clf()
        func(*args, **kwargs)
        plt.show()
    return inner


@draw_figure
def create_heatmap(trajectories: np.ndarray or TrajectoryObject,
                   bins: int) -> np.ndarray:
    """
    Plots a heatmap of fish positions
    :param trajectories: tuple containing two arrays, x and y pos to use. Can be an array,
    or pass an entire TrajectoryObject and the decorator extracts it
    :param bins: Number of bins to use when plotting
    :return: Plot
    """
    if isinstance(trajectories, TrajectoryObject) or isinstance(trajectories, NovelObjectRecognitionTest):
        trajectories = trajectories.flatten_fish_positions()

    x, y = trajectories[:, 0], trajectories[:, 1]

    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=(bins, bins))
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    return plt.imshow(heatmap.T, extent=extent, origin='lower')

@draw_figure
def create_histogram(trajectories: TrajectoryObject or list,
                     factor: str,
                     bins: int = 10):
    if isinstance(trajectories, TrajectoryObject) or isinstance(trajectories, NovelObjectRecognitionTest):
        trajectories = trajectories.positions_df[factor]

    return plt.hist(trajectories, bins=bins)

def get_recognition_indices(same_pref: tuple,
                            diff_pref: tuple) -> dict:
    """
    Gets measures of recognition from the novel object test
    :param same_pref: Preferences during training phase
    :param diff_pref: Preferences during testing phase, assuming [1] is the novel object
    :return: dict of different measures
    """

    e1 = same_pref[0] + same_pref[1]
    e2 = diff_pref[0] + diff_pref[1]

    d1 = diff_pref[1] - diff_pref[0]
    try:
        d2 = d1 / e2
        d3 = diff_pref[1] / e2
    except ZeroDivisionError:
        d2 = np.NaN
        d3 = np.NaN

    d1_familiar = same_pref[1] - same_pref[0]
    try:
        d2_familiar = d1_familiar / e1
        d3_familiar = same_pref[1] / e1
    except ZeroDivisionError:
        d2_familiar = np.NaN
        d3_familiar = np.NaN

    return {"e1": e1,
            "e2": e2,
            "d1": d1,
            "d2": d2,
            "d3": d3,
            "d1_familiar": d1_familiar,
            "d2_familiar": d2_familiar,
            "d3_familiar": d3_familiar}


def get_ri_significance(index: list,
                        index_name: str = None,
                        mu: float = None) -> float:
    """
    Performs 1sample t-test to determine if a particular recognition index is significant or not
    :param index: A list of values to test
    :param index_name: The name of the index (d1, d2, d3)
    :param mu: A value to compare to, should index not be supplied
    :return: float: the p-value
    """
    mus = {"d1": 0, "d2": 0, 'd3': 0.5}
    if mu is None:
        try:
            mu = mus[index_name]
        except KeyError:
            raise KeyError("Index not recognised. Please supply a mu value.")

    return stats.ttest_1samp(index, popmean=mu, nan_policy='omit', alternative='two-sided')[1]

