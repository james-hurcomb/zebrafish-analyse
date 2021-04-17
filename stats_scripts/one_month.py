import zebrafishanalysis as za
import os
import matplotlib.pyplot as plt
import pandas as pd
from stats_scripts.data_dicts import *

# Set some constants
EXPLORATION_AREA: int = 250
FOLDER: str = "nor_data"
SAME_FILE: str = "same_obj"
DIFF_FILE: str = "diff_obj"
DATA_EXT: str = ".npy"
VID_EXT: str = ".mp4"


def remove_region(tr: dict,
                  v_list: dict) -> None:
    """
    A helper for removing regions just to keep the code uncluttered
    :param tr: list of trajectory objects
    :param v_list: List of verticies to remove
    :return:
    """
    for fish_id, removal_regions in v_list.items():
        print(fish_id)
        rem_rg(tr[fish_id], removal_regions)


def rem_rg(tr: za.TrajectoryObject,
           v: list) -> None:
    """
    Another helper for region removal
    :param tr: TrajectoryObject
    :param v: Verticies to remove
    :return:
    """
    for polygon_object in v:
        tr.remove_polygon_from_frames(polygon_object.v)


def measures_helper(same_tr: za.NovelObjectRecognitionTest,
                    diff_tr: za.NovelObjectRecognitionTest) -> dict:
    """
    Helper for calculating measures
    :param same_tr: Same NovelObjectRecognitionTest obj
    :param diff_tr: Diff NovelObjectRecognitionTest obj
    :return: Recognition indicies
    """
    s = same_tr.determine_object_preference_by_frame(EXPLORATION_AREA)
    d = diff_tr.determine_object_preference_by_frame(EXPLORATION_AREA)
    return za.get_recognition_indices(s, d)


def load_fish(fish_id: str,
              same: bool,
              slicer: slice = None) -> za.NovelObjectRecognitionTest:
    """
    Loads in NORT objects. Some poor design choices here
    :param fish_id: ID of the fish to load
    :param same: If this is a same_obj or diff_obj test
    :param slicer: A slice to put through the object
    :return: NORT object
    """
    print(f"Loading fish {fish_id} {'same' if same is True else 'diff'} with slice {slicer if slicer else 'None'}")
    if same is True:
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{FOLDER}/{fish_id}/{SAME_FILE}{DATA_EXT}"),
                                             video_path=f"{FOLDER}/{fish_id}/{SAME_FILE}{VID_EXT}",
                                             object_locations=training_obj_locations[fish_id], period=slicer)
    else:
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{FOLDER}/{fish_id}/{DIFF_FILE}{DATA_EXT}"),
                                             video_path=f"{FOLDER}/{fish_id}/{DIFF_FILE}{VID_EXT}",
                                             object_locations=testing_obj_locations[fish_id], period=slicer)


if __name__ == "__main__":
    same_fish: dict = {}
    diff_fish: dict = {}
    for fish in os.listdir("nor_data"):
        same_raw, diff_raw = load_fish(fish, same=True), load_fish(fish, same=False)
        same_fish[str(fish)] = same_raw
        diff_fish[str(fish)] = diff_raw

    # Full analysis

    # Remove the erronous data I discovered and bounded at the start of the file
    remove_region(same_fish, regions_to_remove_same)
    remove_region(diff_fish, regions_to_remove_diff)

    # Run some statistics
    measures: dict = {fish: measures_helper(same, diff_fish[fish]) for fish, same in same_fish.items()}
    df_for_exp = pd.DataFrame(measures)
    full_measures: pd.DataFrame = df_for_exp.transpose()
    full_measures.to_csv(os.getcwd() + "/all_fish_by_fish.csv")

    # Analysis by timepoint

    # Construct dictionaries that hold the number of frames for each video
    num_frames_same = {fish: tr.num_frames for fish, tr in same_fish.items()}
    num_frames_diff = {fish: tr.num_frames for fish, tr in diff_fish.items()}

    # Right, this is going to be horrific.
    same_time_slices = {}
    diff_time_slices = {}
    for fish in os.listdir('nor_data'):
        last_i = 0
        same_time_slices[fish] = {}
        diff_time_slices[fish] = {}
        for i in range(18000, num_frames_same[fish] + 18000, 18000):
            # Here we're incrementing in 5 minute intervals from 0 to the maximum possible value
            # Python is super-forgiving, so we can just blast past the max value and it'll give us an irregular slice
            same_raw = load_fish(fish, same=True, slicer=slice(last_i, i))
            same_time_slices[fish][last_i] = same_raw
            last_i = i
        last_i = 0
        for i in range(18000, num_frames_diff[fish] + 18000, 18000):
            diff_raw = load_fish(fish, same=False, slicer=slice(last_i, i))
            diff_time_slices[fish][last_i] = diff_raw
            last_i = i

    # Okay, now we have two dictionaries with arrangement dict[fish][time_period]
    sliced_measures = {}
    for fish_name, periods in same_time_slices.items():
        for period_name, tr_same in periods.items():
            if period_name not in sliced_measures:
                sliced_measures[period_name] = {}
            # Try to get the corresponding timepoint for the same fish
            tr_diff: za.NovelObjectRecognitionTest = diff_time_slices[fish_name][period_name]
            # Now we remove erroneous data. This is a really bad way of doing it, but whatever. todo: .get instead
            try:
                rem_rg(tr_same, regions_to_remove_same[fish_name])
                rem_rg(tr_diff, regions_to_remove_diff[fish_name])
            except KeyError:
                pass
            ms = measures_helper(tr_same, tr_diff)
            sliced_measures[period_name][fish_name] = measures_helper(tr_same, tr_diff)

    # Now we have sliced measures, we'll put them into a csv so I can do proper statistics in R

    for n, time_period in sliced_measures.items():
        df_for_exp = pd.DataFrame(time_period).transpose()
        df_for_exp.to_csv(os.getcwd() + f"/export_{n}.csv")
