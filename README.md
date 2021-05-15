# zebrafish-analyse

Toolkit for analysing and graphing results of zebrafish memory paradigms, using 2D trajectories from idtrackerai.

The code behind my BMS402 project.

```
zebrafish-analyse/
├── zebrafishanalysis/ → Main package
│   ├── __init__.py
│   ├── stats.py → Helpers for plotting & statistics
│   ├── structs.py → Contains classes for holding video information
│   └── utils.py → Misc utils, GUIs, etc
└── stats_scripts/
    ├── data_dicts.py → Points of interest from my analysis
    ├── discrim_indicies.py → Analysis of 1/2 month fish memory
    ├── edges.py → Analysis of 1/2 month edge preference
    ├── erratic.py → Analysis of 1/2 month fish erratic behaviour
    ├── helpers.py → Various analysis helpers
    ├── plotting.r → Creation of graphs
    └── velocity.py → Analysis of 1/2 month fish velocity
```
## Basic use

Example use for getting memory indexes from a NORT:

```python
import zebrafishanalysis as za

same_path = "path/to/training/dir/"
diff_path = "path/to/testing/dir/"

# Get object positions using GUI

same_pos, diff_pos = za.select_pos_from_video(video_path=same_path + "v.mp4"),
                     za.select_pos_from_video(video_path=diff_path + "v.mp4")

# Set pixel length of wall

wall_length_same = 100
wall_length_diff = 100

# Load in trajectories files
same_obj_raw = za.load_gapless_trajectories(same_path + "t.npy")
diff_obj_raw = za.load_gapless_trajectories(diff_path + "t.npy")

# Init TrajectoryObjects

same_obj = za.NovelObjectRecognitionTest(same_obj_raw, same_pos, wall_length_same, video_path=same_path + "v.mp4")
same_obj = za.NovelObjectRecognitionTest(diff_obj_raw, diff_pos, wall_length_diff, video_path=diff_path + "v.mp4")

# Inspect objects using heatmaps

za.draw_heatmap(same_obj, bins = 100)
za.draw_heatmap(diff_obj, bins = 100)

# Use GUI to remove erronous data

error_data = za.select_polygon(same_obj)
same_obj.remove_polygon_from_frames(error_data, inplace=True)

# Get discrimination indicies

discrim = za.get_recognition_indicies(same_obj, diff_obj, exploration_area_radius=250)
```
