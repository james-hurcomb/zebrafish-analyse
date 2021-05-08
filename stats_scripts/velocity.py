from data_dicts import *
from helpers import *
import zebrafishanalysis as za
import os
import numpy as np

def export_speeds(same_fish, diff_fish, month):
    speeds_same = [fish.drop_errors(factor='speed', cutoff=2500)[['speed', 'frame_id']].to_numpy()
                  for fish in same_fish.values()]
    speeds_diff = [fish.drop_errors(factor='speed', cutoff=2500)[['speed', 'frame_id']].to_numpy()
                  for fish in diff_fish.values()]

    np.savetxt(f"speeds_same_{month}m.csv", np.vstack(speeds_same), delimiter=',')
    np.savetxt(f"speeds_diff_{month}m.csv", np.vstack(speeds_diff), delimiter=',')

def speeds_restricted(same_fish, diff_fish, month):
    speeds_same_obj_a = [fish.trim_based_on_objs('obj_a', 200, df = fish.drop_errors(factor='speed', cutoff=2500))[['speed', 'frame_id']].to_numpy()
                  for fish in same_fish.values()]
    speeds_same_obj_b = [fish.trim_based_on_objs('obj_b', 200, df = fish.drop_errors(factor='speed', cutoff=2500))[['speed', 'frame_id']].to_numpy()
                  for fish in same_fish.values()]

    speeds_diff_obj_a = [fish.trim_based_on_objs('obj_a', 200, df = fish.drop_errors(factor='speed', cutoff=2500))[['speed', 'frame_id']].to_numpy()
                  for fish in diff_fish.values()]
    speeds_diff_obj_b = [fish.trim_based_on_objs('obj_b', 200, df = fish.drop_errors(factor='speed', cutoff=2500))[['speed', 'frame_id']].to_numpy()
                  for fish in diff_fish.values()]

    np.savetxt(f"speeds_same_obj_a_{month}m.csv", np.vstack(speeds_same_obj_a), delimiter=',')
    np.savetxt(f"speeds_same_obj_b_{month}m.csv", np.vstack(speeds_same_obj_b), delimiter=',')

    np.savetxt(f"speeds_diff_obj_a_{month}m.csv", np.vstack(speeds_diff_obj_a), delimiter=',')
    np.savetxt(f"speeds_diff_obj_b_{month}m.csv", np.vstack(speeds_diff_obj_b), delimiter=',')

if __name__ == "__main__":
    same_fish_1m = {fish: load_fish(fish, same=True) for fish in os.listdir("nor_data")}
    diff_fish_1m = {fish: load_fish(fish, same=False) for fish in os.listdir("nor_data")}

    remove_region(same_fish_1m, regions_to_remove_same)
    remove_region(diff_fish_1m, regions_to_remove_diff)

    export_speeds(same_fish_1m, diff_fish_1m, 1)
    speeds_restricted(same_fish_1m, diff_fish_1m, 1)

    same_fish_2m = {fish: load_fish(fish, same=True, month=2) for fish in os.listdir("month_2")}
    diff_fish_2m = {fish: load_fish(fish, same=False, month=2) for fish in os.listdir("month_2")}

    remove_region(same_fish_2m, regions_to_remove_same_two_month)
    remove_region(diff_fish_2m, regions_to_remove_diff_two_month)

    export_speeds(same_fish_2m, diff_fish_2m, 2)
    speeds_restricted(same_fish_2m, diff_fish_2m, 2)


