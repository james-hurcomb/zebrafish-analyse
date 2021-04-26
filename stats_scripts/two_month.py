import zebrafishanalysis as za
import pandas as pd
from one_month import remove_region, rem_rg, measures_helper
from data_dicts import *
import os

# Set some constants
EXPLORATION_AREA: int = 250
DATA_DIR: str = "month_2"
SAME_FILE: str = "same_obj"
DIFF_FILE: str = "diff_obj"
DATA_EXT: str = ".npy"
VID_EXT: str = ".mp4"

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
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{DATA_DIR}/{fish_id}/{SAME_FILE}{DATA_EXT}"),
                                             video_path=f"{DATA_DIR}/{fish_id}/{SAME_FILE}{VID_EXT}",
                                             object_locations=training_obj_locations_two_month[fish_id], period=slicer)
    else:
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{DATA_DIR}/{fish_id}/{DIFF_FILE}{DATA_EXT}"),
                                             video_path=f"{DATA_DIR}/{fish_id}/{DIFF_FILE}{VID_EXT}",
                                             object_locations=testing_obj_locations_two_month[fish_id], period=slicer)


if __name__ == "__main__":
    same_fish = {fish: load_fish(fish, same=True) for fish in os.listdir(DATA_DIR)}
    diff_fish = {fish: load_fish(fish, same=False) for fish in os.listdir(DATA_DIR)}

    remove_region(same_fish, regions_to_remove_same_two_month)
    remove_region(diff_fish, regions_to_remove_diff_two_month)

    measures: dict = {fish: measures_helper(same, diff_fish[fish]) for fish, same in same_fish.items()}
    df_for_exp = pd.DataFrame(measures)
    full_measures: pd.DataFrame = df_for_exp.transpose()
    full_measures.to_csv(os.getcwd() + "/two_month_fish_measures.csv")

    print(za.get_ri_significance([m['d1'] for m in measures.values()], index_name = 'd1p '))

    num_frames_same = {fish: tr.num_frames for fish, tr in same_fish.items()}
    num_frames_diff = {fish: tr.num_frames for fish, tr in diff_fish.items()}

    # Right, this is going to be horrific.
    same_time_slices = {}
    diff_time_slices = {}
    for fish in os.listdir(DATA_DIR):
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
            # Try to get the correspnding timepoint for the same fish
            try:
                tr_diff: za.NovelObjectRecognitionTest = diff_time_slices[fish_name][period_name]
            except KeyError:
                # If the recordings are different lengths, just continue
                continue
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
        df_for_exp.to_csv(os.getcwd() + f"/export_2month_{n}.csv")
