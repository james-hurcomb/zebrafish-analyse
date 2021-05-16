from data_dicts import *
from helpers import *
import zebrafishanalysis as za
import os
import numpy as np

def export_erratic(same_fish, diff_fish, month):
    same_sd = za.calculate_avg_rolling_sd([fish.drop_errors('acceleration', 10000) for fish in same_fish.values()], 'acceleration_cm', window=60)
    diff_sd = za.calculate_avg_rolling_sd([fish.drop_errors('acceleration', 10000) for fish in diff_fish.values()], 'acceleration_cm', window=60)

    same_sd.to_csv(os.getcwd() + f"/acc_sds_same_{month}m.csv")
    diff_sd.to_csv(os.getcwd() + f"/acc_sds_diff_{month}m.csv")


if __name__ == "__main__":
    same_fish_1m = {fish: load_fish(fish, same=True) for fish in os.listdir("nor_data")}
    diff_fish_1m = {fish: load_fish(fish, same=False) for fish in os.listdir("nor_data")}

    remove_region(same_fish_1m, regions_to_remove_same)
    remove_region(diff_fish_1m, regions_to_remove_diff)

    export_erratic(same_fish_1m, diff_fish_1m, 1)

    same_fish_2m = {fish: load_fish(fish, same=True, month=2) for fish in os.listdir("month_2")}
    diff_fish_2m = {fish: load_fish(fish, same=False, month=2) for fish in os.listdir("month_2")}

    remove_region(same_fish_2m, regions_to_remove_same_two_month)
    remove_region(diff_fish_2m, regions_to_remove_diff_two_month)

    export_erratic(same_fish_2m, diff_fish_2m, 2)
