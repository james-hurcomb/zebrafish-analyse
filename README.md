# zebrafish-analyse

Toolkit for analysing and graphing results of zebrafish memory paradigms, using 2D trajectories from idtrackerai.

The code behind my BMS402 project.

```
zebrafish-anayse/
├── zebrafishanalysis/ → Main package
│   ├── requirements.txt → Requirements for zebrafishanalysis
│   ├── __init__.py
│   ├── stats.py → Helpers for plotting & statistics
│   ├── structs.py → Classes for holding video information
│   └── utils.py → Important utilities
├── stats_scripts/ → Scripts used to generate data in the report
│   ├── data_dicts.py → Dictionaries containing locations of objects etc
│   ├── one_month.py → Scripts for analysis of the one month old fish
│   ├── plotting.r → R scripts used to plot (prettier than stats.py) graphs
└── 
```
