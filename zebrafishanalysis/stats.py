import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from typing import Callable
from zebrafishanalysis.structs import TrajectoryObject, NovelObjectRecognitionTest


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
def draw_heatmap(trajectories: np.ndarray or TrajectoryObject,
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
def draw_histogram(trajectories: TrajectoryObject or pd.DataFrame,
                   factor: str,
                   bins: int = 10):
    """
    Draws a histogram
    :param trajectories: A TrajectoryObject or Filtered DataFrame
    :param factor: The factor to plot
    :param bins: The number of bins to use
    :return:
    """
    if isinstance(trajectories, TrajectoryObject) or isinstance(trajectories, NovelObjectRecognitionTest):
        trajectories = trajectories.positions_df[factor]
    else:
        trajectories = trajectories[factor]

    return plt.hist(trajectories, bins=bins)


@draw_figure
def draw_rolling(series_to_plot):

    datapoints_index: np.ndarray = series_to_plot.index.to_numpy()
    series_to_plot: np.ndarray = series_to_plot.to_numpy()

    # Mask & remove NaNs, create polyfit line then a 1D line
    idx = np.isfinite(datapoints_index) & np.isfinite(series_to_plot)
    polyfit_line = np.polyfit(datapoints_index[idx], series_to_plot[idx], 1)
    p = np.poly1d(polyfit_line)

    plt.plot(datapoints_index, p(datapoints_index), 'r--')
    return plt.plot(datapoints_index, series_to_plot)


def calculate_rolling_sd(df: pd.DataFrame,
                         factor: str,
                         window: int = 600):
    datapoints = pd.Series(df[factor])
    return datapoints.rolling(window).std()


def calculate_avg_rolling_sd(df_list: list,
                             factor: str,
                             window: int = 600):
    master: pd.DataFrame = pd.DataFrame({i: calculate_rolling_sd(df, factor, window) for i, df in enumerate(df_list)})
    master['mean'] = master.mean(axis=1)
    return pd.Series(master['mean'])


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

