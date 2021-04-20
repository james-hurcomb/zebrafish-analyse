import logging
import trajectorytools as tt
import tkinter as tk
import sys
from PIL import ImageTk, Image
import av
import numpy as np
from shapely.geometry import Polygon
from zebrafishanalysis.structs import TrajectoryObject, get_video_dimensions


class SelectPolygon:

    def __init__(self,
                 master: tk.Tk,
                 vid_path: str,
                 title_text: str = "za: Generic Window"):
        master: tk.Tk = master
        master.title(title_text)
        self.dimensions: tuple = get_video_dimensions(vid_path)

        # Get frame of video. I **really** hate this, but cannot get it to work otherwise and cannot be bothered to \
        # improve it as it works. Urgh.
        vid_container = av.open(vid_path)
        for f in vid_container.decode(video=0):
            fr = f.to_image()
            break
        img = ImageTk.PhotoImage(fr)

        # Generate canvas, pack canvas into window, fill canvas with image
        self.canvas: tk.Canvas = tk.Canvas(master)
        self.canvas.pack()
        self.canvas.configure(height=img.height(), width=img.width())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

        self.vertices: list = []
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


def get_centroid(v: np.ndarray) -> tuple:
    """Gets centre point of a irregular shape, converts from POINT to tuple
    Args:
        v (np.ndarray): The list of coordinates of the points of shape
    Returns:
        tuple: (X, Y) of centroid. Note centre point of irregular shape may fall outside bounding of shape
    """
    poly = Polygon(v)
    centroid = poly.centroid
    return centroid.x, centroid.y


def invert_y(v: list,
             tr: TrajectoryObject = None,
             dimensions: tuple = None) -> np.ndarray:
    """Inverts y axis due to tkinter grid structure where (0, 0) is NW
    Args:
        v (list): The list of coordinates to flip
        tr (TrajectoryObject): TrajectoryObject to get dimensions from
        dimensions (tuple): Raw dimensions to use if TrajectoryObject not supplied
    Returns:
        np.ndarray: List with inverted y axis
    """
    if tr:
        height: int = tr.video_dimensions[1]
    elif dimensions:
        height: int = dimensions[1]

    v_arr: np.array = np.array(v)
    v_arr[:, 1] = height - v_arr[:, 1]
    return v_arr


def select_pos_from_video(tr: TrajectoryObject = None,
                          vid_path: str = None) -> tuple:
    """Allows for GUI selection of objects in NORT video
    Args:
        tr (TrajectoryObject): The trajectory object to select objects from
    Returns:
        tuple: Tuple of structure:
            ((obj_a_X, obj_a_Y), (obj_b_X, obj_b_Y), ((obj_a_vertices_list), (obj_b_vertices_list)))
    """
    if not vid_path:
        vid_path = tr.video_path
    obj_a: np.ndarray = select_polygon(video_path=vid_path, window_title="Select Object A")
    obj_b: np.ndarray = select_polygon(video_path=vid_path, window_title="Select Object B")

    return get_centroid(obj_a), get_centroid(obj_b), (obj_a, obj_b)


def select_polygon(tr: TrajectoryObject = None,
                   video_path: str = None,
                   window_title: str = "Select Polygon") -> np.ndarray:
    """Helper for polygonal selection from video frame
    Args:
        tr (TrajectoryObject): The trajectory object to inspect
        window_title (str): Help text to put in window title
    Returns:
        np.ndarray: array of vertices
    """
    if not video_path:
        video_path = tr.video_path

    root = tk.Tk()
    win = SelectPolygon(root, vid_path=video_path, title_text=window_title)
    root.mainloop()
    # We need to flip the verticies
    vertices: np.array = invert_y(win.vertices, dimensions=get_video_dimensions(video_path))
    return vertices


def load_gapless_trajectories(wo_gaps: str,
                              interpolate_nans: bool = True,
                              smooth: dict = {'sigma': 1}) -> tt.Trajectories:
    """Loads gapless trajectories from a idtrackerai numpy file
    Args:
        wo_gaps (str): Path to numpy file (should be trajectories_wo_gaps or trajectories .npy originally)
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


def crush_multiple_objects(objects: list,
                           factor: str = 'positions') -> np.ndarray:
    """Combines the positions of fish from multiple objects
    Args:
        objects (list): list of TrajectoryObjects
    Returns:
        np.ndarray: Stack of all positions from all objects
    """
    if factor == 'positions':
        try:
            positions: list = [obj.flatten_fish_positions() for obj in objects]
        except ValueError:
            # todo error handling
            raise ValueError
        return np.vstack(positions)
    elif factor == 'speeds' or factor == 'speed':
        try:
            speeds: list = [obj.positions_df[['speed']].to_numpy() for obj in objects]
        except ValueError:
            raise ValueError
        return np.vstack(speeds)
    elif factor == 'accelerations' or factor == 'acceleration':
        try:
            speeds: list = [obj.positions_df[['acceleration']].to_numpy() for obj in objects]
        except ValueError:
            raise ValueError
        return np.vstack(speeds)
    else:
        raise ValueError("This factor does not exist")


