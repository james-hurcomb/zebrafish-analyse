import zebrafishanalysis as za
import os
import csv
import pandas as pd

EXPLORATION_AREA: int = 250


class Polygon:

    def __init__(self, v: list) -> None:
        self.v = v


def remove_region(tr: dict,
                  v_list: dict) -> None:
    for fsh, removal_regions in v_list.items():
        for polygon_object in removal_regions:
            tr[fsh].remove_polygon_from_frames(polygon_object.v, output=True)

def rem_rg(tr: za.TrajectoryObject,
           v: list) -> None:
    for polygon_object in v:
        tr.remove_polygon_from_frames(polygon_object.v, output=True)

def measures_helper(same_tr: za.NovelObjectRecognitionTest,
                    diff_tr: za.NovelObjectRecognitionTest) -> dict:
    s = same_tr.determine_object_preference_by_frame(EXPLORATION_AREA)
    d = diff_tr.determine_object_preference_by_frame(EXPLORATION_AREA)
    return za.get_measures(s, d)

def load_fish(slicer: slice = None):
    pass

# DEFINE CONSTANTS:

# I worked out these values earlier for reproducibility. They can be got using a GUI instead
regions_to_remove_same: dict = {
    'm_1_f_4': [Polygon([[842, 315], [915, 311], [917, 370], [843, 373]])],
    'm_1_f_6': [Polygon([[862, 302], [845, 316], [838, 348], [847, 365], [871, 380], [894, 377], [915, 365],
                         [927, 349], [929, 328], [912, 315], [893, 304]])],
    'm_1_f_11': [Polygon([[1125, 592], [1184, 589], [1177, 426], [1123, 422]])],
    'm_1_f_13': [Polygon([[826, 322], [830, 360], [881, 375], [911, 358], [924, 331], [921, 301], [898, 288],
                          [853, 287]])],
    'm_1_f_17': [Polygon([[337, 436], [366, 455], [365, 422], [334, 423]]),
                 Polygon([[829, 490], [833, 511], [851, 512], [849, 493]])]
}

regions_to_remove_diff: dict = {
    'm_1_f_2': [Polygon([[172, 56], [177, 120], [237, 112], [224, 33]])],
    'm_1_f_6': [Polygon([[1105, 330], [1120, 330], [1120, 315], [1105, 315]])],
    'm_1_f_8': [Polygon([[667, 116], [684, 118], [686, 101], [665, 99]]),
                Polygon([[272, 167], [281, 167], [281, 156], [272, 156]])],
    'm_1_f_10': [Polygon([[79, 635], [115, 644], [112, 560], [63, 566]])],
    'm_1_f_12': [Polygon([[825, 82], [765, 86], [748, 12], [837, 2]])],
    'm_1_f_13': [Polygon([[380, 318], [355, 311], [317, 312], [300, 333], [307, 359], [328, 375],
                          [343, 392], [370, 396], [395, 385], [407, 368], [408, 346]])],
    'm_1_f_14': [Polygon([[590, 678], [622, 672], [620, 656], [589, 656]])],
    'm_1_f_15': [Polygon([[549, 659], [569, 659], [549, 649], [569, 649]])],
    'm_1_f_17': [Polygon([[690, 665], [710, 665], [710, 640], [690, 640]]),
                 Polygon([[1020, 312], [1040, 312], [1040, 298], [1020, 298]])]
}

# Now, object locations that I calculated earlier:

training_obj_locations: dict = {
    'm_1_f_1': ((409.18561543150116, 375.2420852604783), (868.2508355129323, 358.1916594013368)),
    'm_1_f_2': ((424.43770527698706, 374.66633822348734), (890.5503297765807, 356.0428536896992)),
    'm_1_f_3': ((414.80803488930775, 362.3900284584396), (876.1866666666666, 344.7154736842105)),
    'm_1_f_4': ((418.6220277466843, 361.05868186289473), (882.3823559201863, 345.34697322664505)),
    'm_1_f_5': ((416.0402194744166, 350.4632327846473), (878.4028311727014, 335.9190284607361)),
    'm_1_f_6': ((415.9102780257199, 357.2425534728421), (879.4426024955436, 338.61864527629234)),
    'm_1_f_7': ((368.7978717987882, 362.3631179675169), (876.2353075344028, 372.98659367951547)),
    'm_1_f_8': ((357.8556937950709, 366.86221834799375), (870.7612789115645, 363.8017142857143)),
    'm_1_f_9': ((358.0327945461543, 361.8261586673264), (871.6713243629554, 361.6673566957465)),
    'm_1_f_10': ((369.3826200780039, 367.65742373243575), (881.376998632351, 365.6054705955489)),
    'm_1_f_11': ((357.51697688421166, 370.7381868635304), (868.3920423169704, 362.1285494230825)),
    'm_1_f_12': ((346.8888220400592, 368.7566869719987), (864.8822067325876, 364.10212352082993)),
    'm_1_f_13': ((367.3264950888972, 333.60201417381575), (871.8908066535504, 328.8075776545639)),
    'm_1_f_14': ((363.7502920073419, 344.933394515824), (872.2412622646513, 329.78385043754975)),
    'm_1_f_15': ((354.4211217729038, 343.82108179118114), (860.1306170652495, 336.1553882491881)),
    'm_1_f_16': ((358.56542468656187, 337.92247925128027), (869.6998597475456, 329.34052127162226)),
    'm_1_f_17': ((371.55936348719854, 349.91334633602673), (878.2426534594026, 341.6643553954675)),
}

testing_obj_locations: dict = {
    'm_1_f_1': ((408.1435641850967, 335.8688955802444), (881.9322968612496, 328.05849222645935)),
    'm_1_f_2': ((417.525629695095, 343.9455368979231), (887.6114983616324, 335.2036341971999)),
    'm_1_f_3': ((414.70746703628674, 345.81643387710136), (886.8049807013222, 337.70052147491174)),
    'm_1_f_4': ((424.83168041201236, 347.98402756028815), (894.5181572121348, 335.4707529792113)),
    'm_1_f_5': ((419.5981024813705, 347.8972497503265), (893.3570411707761, 333.721902701061)),
    'm_1_f_6': ((424.14473829810777, 349.1400538526797), (895.4870117449022, 346.0570029457898)),
    'm_1_f_7': ((354.25498735951544, 367.66992065279965), (871.9635970688548, 344.30964441292673)),
    'm_1_f_8': ((351.13534082397, 360.3293183520599), (870.2826352907312, 344.86602259643064)),
    'm_1_f_9': ((357.5171282393504, 364.06634412189965), (877.0186811733817, 346.66570333012226)),
    'm_1_f_10': ((358.2894295063309, 351.93982074263766), (877.1236682302462, 338.45360168721135)),
    'm_1_f_11': ((357.63607594936707, 354.1019397562119), (877.3822592364876, 336.59314739254376)),
    'm_1_f_12': ((365.7320077282241, 365.4163849084957), (883.8979879654005, 339.79240315908237)),
    'm_1_f_13': ((355.0044270833333, 349.42311197916666), (862.5318117078623, 346.317305785422)),
    'm_1_f_14': ((351.43300431132286, 348.200079419106), (862.6982221388524, 342.330081910836)),
    'm_1_f_15': ((366.5216662739245, 339.98363574477), (867.6832855025979, 334.50880648247147)),
    'm_1_f_16': ((359.2742601708821, 339.81477394896166), (864.1068253462261, 334.9175787199377)),
    'm_1_f_17': ((367.5630622360933, 341.10947922403767), (871.0986776517502, 334.23664954949874)),

}

# Onto the real processing code now

if __name__ == "__main__":
    same_fish: dict = {}
    diff_fish: dict = {}
    for fish in os.listdir("nor_data"):
        same = za.NovelObjectRecognitionTest(za.load_gapless_trajectories("nor_data/" + fish + "/same_obj.npy"),
                                             video_path="nor_data/" + fish + "/same_obj.mp4",
                                             object_locations=training_obj_locations[str(fish)])
        diff = za.NovelObjectRecognitionTest(za.load_gapless_trajectories("nor_data/" + fish + "/diff_obj.npy"),
                                             video_path="nor_data/" + fish + "/diff_obj.mp4",
                                             object_locations=testing_obj_locations[str(fish)])
        same_fish[str(fish)] = same
        diff_fish[str(fish)] = diff

    # Remove the erronous data I discovered and bounded at the start of the file
    remove_region(same_fish, regions_to_remove_same)
    remove_region(diff_fish, regions_to_remove_diff)

    # Run some statistics
    measures: dict = {fish: measures_helper(same, diff_fish[fish]) for fish, same in same_fish.items()}
    df_for_exp = pd.DataFrame(measures)
    flipped: pd.DataFrame = df_for_exp.transpose()
    flipped.to_csv(os.getcwd() + "/export_first10.csv")

    # Construct dictionaries that hold the number of frames for each video. Now, what we're going to (try) to do, is
    # grab a snapshot of the fish for 5 minute intervals. This is complicated by the fact my data doesn't have a
    # consistent number of frames, which is really annoying
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
            fsh = za.NovelObjectRecognitionTest(za.load_gapless_trajectories("nor_data/" + fish + "/same_obj.npy"),
                                                video_path="nor_data/" + fish + "/same_obj.mp4",
                                                object_locations=training_obj_locations[str(fish)],
                                                period=slice(last_i, i))
            same_time_slices[fish][last_i] = fsh
            last_i = i
        last_i = 0
        for i in range(18000, num_frames_diff[fish] + 18000, 18000):
            # And now we do the same again for diff fish. todo: remove this duplication D:
            fsh = za.NovelObjectRecognitionTest(za.load_gapless_trajectories("nor_data/" + fish + "/diff_obj.npy"),
                                                video_path="nor_data/" + fish + "/same_obj.mp4",
                                                object_locations=training_obj_locations[str(fish)],
                                                period=slice(last_i, i))
            diff_time_slices[fish][last_i] = fsh
            last_i = i

    # Okay, now we have two dictionaries with arrangement dict[fish][time_period]. The issue is, the numbers of frames
    # aren't exactly the same. If the number of slices is
    sliced_measures = {}
    for fish_name, periods in same_time_slices.items():
        for period_name, tr_same in periods.items():
            if period_name not in sliced_measures:
                sliced_measures[period_name] = {}
            # Try to get the correspnding timepoint for the same fish
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
