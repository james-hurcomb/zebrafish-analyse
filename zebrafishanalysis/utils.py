import logging
import trajectorytools as tt
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import av
import numpy as np
from shapely.geometry import Polygon
# Import internal utils
from zebrafishanalysis.structs import TrajectoryObject

class SelectPolygon:

    def __init__(self,
                 master: Tk,
                 tr: TrajectoryObject,
                 title_text: str = "za: Generic Window"):
        master: Tk = master
        master.title(title_text)
        path = tr.video_path
        self.dimensions = tr.video_dimensions

        # Get frame of video. I **really** hate this, but cannot get it to work otherwise and cannot be bothered to \
        # improve it as it works. Urgh.
        vid_container = av.open(path)
        for f in vid_container.decode(video=0):
            fr = f.to_image()
            break
        img = ImageTk.PhotoImage(fr)

        # Generate canvas, pack canvas into window, fill canvas with image
        self.canvas: tk.Canvas = tk.Canvas(master)
        self.canvas.pack()
        self.canvas.configure(height=img.height(), width=img.width())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

        self.vertices = []
        self.canvas.bind_all("<Button 1>", self.place_marker)

        self.final_connection = self.canvas.create_line(0, 0, 0, 0)
        self.centre = self.canvas.create_oval(0, 0, 0, 0, fill="blue")

        tk.mainloop()

    def place_marker(self, eventcoords):
        x, y = eventcoords.x, eventcoords.y
        self.vertices.append((x, y))
        x_max, x_min = x + 5, x - 5
        y_max, y_min = y + 5, y - 5

        self.canvas.create_oval(x_max, y_max, x_min, y_min, fill="red")
        self.canvas.create_text(x + 10, y + 10, text=f"{x}, {self.dimensions[1] - y}")

        if len(self.vertices) > 1:
            self.connect_to_previous(x, y)

    def connect_to_previous(self, x, y):
        self.canvas.create_line(self.vertices[-2][0], self.vertices[-2][1], x, y)
        self.canvas.coords(self.final_connection, x, y, self.vertices[0][0], self.vertices[0][1])

        if len(self.vertices) > 2:
            polygon = Polygon(self.vertices)
            cx, cy = polygon.centroid.x, polygon.centroid.y

            x_max, x_min = cx + 5, cx - 5
            y_max, y_min = cy + 5, cy - 5
            self.canvas.coords(self.centre, x_max, y_max, x_min, y_min)


def get_centroid(v: np.ndarray):
    poly = Polygon(v)
    centroid = poly.centroid
    return centroid.x, centroid.y

def invert_y(v: list,
             tr: TrajectoryObject):
    v_arr: np.array = np.array(v)
    v_arr[:, 1] = tr.video_dimensions[1] - v_arr[:, 1]
    return v_arr


def select_pos_from_video(tr: TrajectoryObject):
    root_a = tk.Tk()
    obj_a = SelectPolygon(root_a, tr, "Select Object A")
    obj_a_vertices: np.array = invert_y(obj_a.vertices, tr)
    root_a.mainloop()

    root_b = tk.Tk()
    obj_b = SelectPolygon(root_b, tr, "Select Object B")
    obj_b_vertices: np.array = invert_y(obj_b.vertices, tr)
    root_b.mainloop()

    return get_centroid(obj_a_vertices), get_centroid(obj_b_vertices)


def select_polygon(tr: TrajectoryObject):
    root = tk.Tk()
    win = SelectPolygon(root, tr)
    root.mainloop()
    # We need to flip the verticies
    vertices: np.array = invert_y(win.vertices, tr)
    return vertices

def load_gapless_trajectories(wo_gaps: str,
                              interpolate_nans: bool = True,
                              smooth: dict = {'sigma': 1}) -> tt.Trajectories:
    """Function to load gapless trajectories from a idtrackerai numpy file
    Args:
        wo_gaps (str): Path to long.npy
        interpolate_nans (bool): When loading from idtrackerai interpolate NaN values
        smooth (dict): Define how to smooth params when loading from idtrackerai
    Returns:
        TrajectoryObject: Processed trajectories
    """

    warnings: list = []

    # Attempts to load the file, throws exception if the file isn't found
    try:
        trajectories_raw: tt.Trajectories = tt.Trajectories.from_idtrackerai(wo_gaps,
                                                                             interpolate_nans=interpolate_nans,
                                                                             smooth_params=smooth)
        logging.info(f'Loaded file {wo_gaps}')
    except FileNotFoundError:
        logging.fatal(f'File {wo_gaps} not found')
        exit(1)

    # Set length (calculated from body length), and time (calculated from FPS) units
    trajectories_raw.new_time_unit(trajectories_raw.params['frame_rate'], 's')

    # Logs the params of the file to the terminal
    logging.info('Parameters:')
    for key, value in trajectories_raw.params.items():
        logging.info(f'{key} : {value}')

    # Prints any warning to the terminal after the params for easier debugging
    for warning in warnings:
        logging.warning(warning)

    # Set recursion limit to be the number of frames + a few extra to allow for recursive methods to analyse
    sys.setrecursionlimit(trajectories_raw.number_of_frames + 30)

    return trajectories_raw


def crush_multiple_objects(objects: list):
    if len(objects) <= 1:
        raise ValueError
    positions = [obj.flatten_fish_positions() for obj in objects]
    return np.vstack(positions)
