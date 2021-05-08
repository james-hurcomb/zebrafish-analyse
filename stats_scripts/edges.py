from data_dicts import *
from helpers import *
import zebrafishanalysis as za
import os
import pandas as pd

def edge_analysis(same_fish_full, diff_fish_full, month):

    if month == 1:
        ctl_same = central_regions_same_1_m
        ctl_diff = central_regions_diff_1_m
    else:
        ctl_same = central_regions_same_2_m
        ctl_diff = central_regions_diff_2_m

    s = pd.DataFrame(
        {
            fish: {"Trial": "Same",
                   "Total Frames": len(full.positions_df),
                   "Frames at edge": len(full.positions_df) - len(full.trim_to_polygon(ctl_same[fish]))} for fish, full in same_fish_full.items()
        }
    ).transpose()

    d = pd.DataFrame(
        {
            fish: {"Trial": "Diff",
                   "Total Frames": len(full.positions_df),
                   "Frames at edge": len(full.positions_df) - len(full.trim_to_polygon(ctl_diff[fish]))} for fish, full in diff_fish_full.items()
        }
    ).transpose()

    together = s.append(d)

    return together


if __name__ == "__main__":
    same_fish_1m = {fish: load_fish(fish, same=True) for fish in os.listdir("nor_data")}
    diff_fish_1m = {fish: load_fish(fish, same=False) for fish in os.listdir("nor_data")}

    remove_region(same_fish_1m, regions_to_remove_same)
    remove_region(diff_fish_1m, regions_to_remove_diff)

    edge_analysis(same_fish_1m, diff_fish_1m, 1).to_csv(os.getcwd() + "/edge_analysis_full_one_month.csv")

    same_fish_2m = {fish: load_fish(fish, same=True, month=2) for fish in os.listdir("month_2")}
    diff_fish_2m = {fish: load_fish(fish, same=False, month=2) for fish in os.listdir("month_2")}

    remove_region(same_fish_2m, regions_to_remove_same_two_month)
    remove_region(diff_fish_2m, regions_to_remove_diff_two_month)

    edge_analysis(same_fish_2m, diff_fish_2m, 2).to_csv(os.getcwd() + "/edge_analysis_full_two_month.csv")
