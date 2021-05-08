from data_dicts import *
from helpers import *
import zebrafishanalysis as za
import os
import pandas as pd

def measures_helper(same_tr: za.NovelObjectRecognitionTest,
                    diff_tr: za.NovelObjectRecognitionTest) -> dict:
    """
    Helper for calculating measures
    :param same_tr: Same NovelObjectRecognitionTest obj
    :param diff_tr: Diff NovelObjectRecognitionTest obj
    :return: Recognition indicies
    """
    return za.get_recognition_indices(same_tr, diff_tr, 250)


if __name__ == "__main__":
    same_fish_1m = {fish: load_fish(fish, same=True) for fish in os.listdir("nor_data")}
    diff_fish_1m = {fish: load_fish(fish, same=False) for fish in os.listdir("nor_data")}

    remove_region(same_fish_1m, regions_to_remove_same)
    remove_region(diff_fish_1m, regions_to_remove_diff)

    same_fish_2m = {fish: load_fish(fish, same=True, month=2) for fish in os.listdir("month_2")}
    diff_fish_2m = {fish: load_fish(fish, same=False, month=2) for fish in os.listdir("month_2")}

    remove_region(same_fish_2m, regions_to_remove_same_two_month)
    remove_region(diff_fish_2m, regions_to_remove_diff_two_month)

    measures: dict = {fish: measures_helper(same, diff_fish_1m[fish]) for fish, same in same_fish_1m.items()}
    df_for_exp = pd.DataFrame(measures)
    full_measures: pd.DataFrame = df_for_exp.transpose()
    full_measures.to_csv(os.getcwd() + "/all_fish_by_fish.csv")

    measures: dict = {fish: measures_helper(same, diff_fish_2m[fish]) for fish, same in same_fish_2m.items()}
    df_for_exp = pd.DataFrame(measures)
    full_measures: pd.DataFrame = df_for_exp.transpose()
    full_measures.to_csv(os.getcwd() + "/two_month_fish_measures.csv")

    # Construct dictionaries that hold the number of frames for each video
    num_frames_same_1m = {fish: tr.num_frames for fish, tr in same_fish_1m.items()}
    num_frames_diff_1m = {fish: tr.num_frames for fish, tr in diff_fish_1m.items()}

    get_sliced_measures(num_frames_same_1m, num_frames_diff_1m, "nor_data", "export")

    num_frames_same_2m = {fish: tr.num_frames for fish, tr in same_fish_2m.items()}
    num_frames_diff_2m = {fish: tr.num_frames for fish, tr in same_fish_2m.items()}
    get_sliced_measures(num_frames_same_2m, num_frames_diff_2m, "month_2", "export_2month")
