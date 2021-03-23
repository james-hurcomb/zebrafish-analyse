import logging
import trajectorytools as tt
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import av
# Import internal utils
from zebrafishanalysis.structs import TrajectoryObject


class ObjectOfInterest:

    def __init__(self, marker, label):
        self.x_pos = 0
        self.y_pos = 0
        self.marker = marker
        self.label = label


class GuiForObjectPos:

    def __init__(self,
                 master: Tk,
                 path: str):

        # Initiate vars
        self.master: Tk = master

        # Get frame of video. I **really** hate this, but cannot get it to work otherwise and cannot be bothered to \
        # improve it as it works. Urgh.
        vid_container = av.open(path)
        for f in vid_container.decode(video=0):
            fr = f.to_image()
            break
        img = ImageTk.PhotoImage(fr)

        # Generate canvas, pack canvas into window, fill canvas with image
        self.canvas: tk.Canvas = tk.Canvas(self.master)
        self.canvas.pack()
        self.canvas.configure(height=img.height(), width=img.width())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

        # Create objects
        self.object_a = ObjectOfInterest(self.canvas.create_oval(0, 0, 0, 0, fill="red"),
                                         self.canvas.create_text(0, 0, text=f""))
        self.object_b = ObjectOfInterest(self.canvas.create_oval(0, 0, 0, 0, fill="blue"),
                                         self.canvas.create_text(0, 0, text=f""))


        # Bind click events
        self.canvas.bind_all("<Button 1>",
                             lambda event, obj=self.object_a: self.update_marker_coords(event, obj))
        self.canvas.bind_all("<Button 3>",
                             lambda event, obj=self.object_b: self.update_marker_coords(event, obj))

        tk.mainloop()

    def update_marker_coords(self,
                             eventcoords: Event,
                             obj: ObjectOfInterest,
                             radius: int = 8) -> None:
        """ Method to run on click event to update coordinates of objects
        Args:
            eventcoords (Event): Click event
            obj (ObjectOfInterest): The object to update
            radius (int): Radius of markers
        Returns:
            None
        """

        # Grab coordinates from eventcoords and set the object positions
        x, y = eventcoords.x, eventcoords.y
        obj.x_pos, obj.y_pos = x, y

        # Update locations of objects, redraw circles and edit text on label
        x_max, x_min = x + radius, x - radius
        y_max, y_min = y + radius, y - radius
        self.canvas.coords(obj.marker, x_max, y_max, x_min, y_min)
        self.canvas.coords(obj.label, x + (radius * 2), y + (radius * 2))
        self.canvas.itemconfigure(obj.label, text=f"{x}, {y}")


def select_pos_from_video(path: str):
    root = tk.Tk()
    win = GuiForObjectPos(root, path)
    root.mainloop()
    return (win.object_a.x_pos, win.object_a.y_pos), (win.object_b.x_pos, win.object_b.y_pos)


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
