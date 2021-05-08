from data_dicts import *
import zebrafishanalysis as za
import os
import pandas as pd


def remove_region(tr: dict,
                  v_list: dict) -> None:
    """
    A helper for removing regions just to keep the code uncluttered
    :param tr: list of trajectory objects
    :param v_list: List of verticies to remove
    :return:
    """
    for fish_id, removal_regions in v_list.items():
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
        tr.remove_polygon_from_frames(polygon_object.v, inplace=True)

def load_fish(fish_id: str,
              same: bool,
              slicer: slice = None,
              month: int = 1) -> za.NovelObjectRecognitionTest:
    """
    Loads in NORT objects. Some poor design choices here
    :param fish_id: ID of the fish to load
    :param same: If this is a same_obj or diff_obj test
    :param slicer: A slice to put through the object
    :return: NORT object
    """
    same_file: str = "same_obj"
    diff_file: str = "diff_obj"
    data_ext: str = ".npy"
    vid_ext: str = ".mp4"

    if month == 1:
        data_dir = "nor_data"
        same_obj_locations = training_obj_locations
        dff_obj_locations = testing_obj_locations
        lengths_same = lengths_1m_same
        lengths_diff = lengths_1m_diff

    else:
        data_dir = "month_2"
        same_obj_locations = training_obj_locations_two_month
        dff_obj_locations = testing_obj_locations_two_month
        lengths_same = lengths_2m_same
        lengths_diff = lengths_2m_diff

    print(f"Loading fish {fish_id} {'same' if same is True else 'diff'} with slice {slicer if slicer else 'None'}")
    if same is True:
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{data_dir}/{fish_id}/{same_file}{data_ext}"),
                                             video_path=f"{data_dir}/{fish_id}/{same_file}{vid_ext}",
                                             object_locations=same_obj_locations[fish_id], period=slicer,
                                             left_wall_coords=lengths_same[fish_id])
    else:
        return za.NovelObjectRecognitionTest(za.load_gapless_trajectories(f"{data_dir}/{fish_id}/{diff_file}{data_ext}"),
                                             video_path=f"{data_dir}/{fish_id}/{diff_file}{vid_ext}",
                                             object_locations=dff_obj_locations[fish_id], period=slicer,
                                             left_wall_coords=lengths_diff[fish_id])

def measures_helper(same_tr: za.NovelObjectRecognitionTest,
                    diff_tr: za.NovelObjectRecognitionTest) -> dict:
    """
    Helper for calculating measures
    :param same_tr: Same NovelObjectRecognitionTest obj
    :param diff_tr: Diff NovelObjectRecognitionTest obj
    :return: Recognition indicies
    """
    return za.get_recognition_indices(same_tr, diff_tr, 250)


def get_sliced_measures(num_frames_same, num_frames_diff, dir, filename):
    same_time_slices_1m = {}
    diff_time_slices_1m = {}
    for fish in os.listdir(dir):
        last_i = 0
        same_time_slices_1m[fish] = {}
        diff_time_slices_1m[fish] = {}
        for i in range(18000, num_frames_same[fish] + 18000, 18000):
            # Here we're incrementing in 5 minute intervals from 0 to the maximum possible value
            # Python is super-forgiving, so we can just blast past the max value and it'll give us an irregular slice
            same_raw_1m = load_fish(fish, same=True, slicer=slice(last_i, i))
            same_time_slices_1m[fish][last_i] = same_raw_1m
            last_i = i
        last_i = 0
        for i in range(18000, num_frames_diff[fish] + 18000, 18000):
            diff_raw_1m = load_fish(fish, same=False, slicer=slice(last_i, i))
            diff_time_slices_1m[fish][last_i] = diff_raw_1m
            last_i = i

    # Okay, now we have two dictionaries with arrangement dict[fish][time_period]
    sliced_measures_1m = {}
    for fish_name, periods in same_time_slices_1m.items():
        for period_name, tr_same in periods.items():
            if period_name not in sliced_measures_1m:
                sliced_measures_1m[period_name] = {}
            # Try to get the correspnding timepoint for the same fish
            tr_diff: za.NovelObjectRecognitionTest = diff_time_slices_1m[fish_name][period_name]
            # Now we remove erroneous data. This is a really bad way of doing it, but whatever. todo: .get instead
            try:
                rem_rg(tr_same, regions_to_remove_same[fish_name])
                rem_rg(tr_diff, regions_to_remove_diff[fish_name])
            except KeyError:
                pass
            ms = measures_helper(tr_same, tr_diff)
            sliced_measures_1m[period_name][fish_name] = measures_helper(tr_same, tr_diff)

    # Now we have sliced measures, we'll put them into a csv so I can do proper statistics in R

    for n, time_period in sliced_measures_1m.items():
        df_for_exp = pd.DataFrame(time_period).transpose()
        df_for_exp.to_csv(os.getcwd() + f"/{filename}_{n}.csv")