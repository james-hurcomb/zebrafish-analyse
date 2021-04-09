import numpy as np
import trajectorytools as tt
import matplotlib.path as pltpath
from pymediainfo import MediaInfo


class AcuityError(Exception):
    pass


class TrajectoryObject:
    """
    A class to store and provide basic tools for analysis of trajectories.
    """

    def __init__(self, raw_loaded_trajectories: tt.trajectories,
                 video_path: str = None,
                 invert_y: bool = True):

        # Set some generic params for easy inspection at a later date. Mostly just pull from tt properties
        self.num_fish: int = len(raw_loaded_trajectories.identity_labels)
        self.num_frames: int = int(raw_loaded_trajectories.number_of_frames)
        self.frame_rate: int = raw_loaded_trajectories.params['frame_rate']
        self.recording_length: float = raw_loaded_trajectories.number_of_frames / raw_loaded_trajectories.params['frame_rate']

        # If a video path is supplied, we set the path as a property and extract the dimensions. A video path isn't
        # necessary though, it's really only helpful for the GUI helpers
        if video_path:
            self.video_path: str = video_path

            media_info: MediaInfo.parse = MediaInfo.parse(self.video_path)

            for track in media_info.tracks:
                if track.track_type == 'Video':
                    self.video_dimensions = (track.width, track.height)

        # Organise trajectories data
        self.positions: np.ndarray = raw_loaded_trajectories.s
        if invert_y is True:
            self.positions[:, :, 1] = self.video_dimensions[1] - self.positions[:, :, 1]

        # This mostly exists for debugging purposes and will probably be removed at some point
        self.modified_positions: np.ndarray = self.positions

    def __getitem__(self, item):
        # Slicing should return a fish range, preserving the dimensions of the original trajectory object (i.e. we want
        # to avoid flattening it. This means a rather hacky solution to ensure we don't select). Other methods provided
        # for flattening a fish range's positions
        if type(item) is not slice:
            item = slice(item, item+1)
        return self.positions[:, item, :]

    def get_fish_pos(self,
                     fish_id: int,
                     frame_num: int) -> tuple:
        """Returns the X,Y coordinates of a fish at a requested frame

        Args:
            fish_id (int): The ID of the fish
            frame_num (int): The frame to inspect

        Returns:
            tuple: (X,Y) coordinates of a fish at a particular time
        """

        return self.positions[frame_num][fish_id][0], self.positions[frame_num][fish_id][1]

    @staticmethod
    def distance_between_points(point_a: tuple,
                                point_b: tuple) -> float:
        """Gets the distance between two points

        Args:
            point_a (tuple): (X, Y) of point a
            point_b (tuple): (X, Y) of point b

        Returns:
            float: distance between points in pixels
        """

        return np.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)

    def flatten_fish_positions(self,
                               fish_range: slice = None) -> np.ndarray:
        """Returns a flattened tuple containing all X and Y coordinates visited by fish in the range
        Args:
            fish_range (tuple): Range of fish to run on

        Returns:
            tuple: x,y lists of fish positions"""
        if fish_range is None:
            fish_range = slice(0, self.num_fish)

        return np.array(self.positions[:, fish_range, :]).reshape(self.positions.shape[1]*self.positions.shape[0], 2)

    def remove_polygon_from_frames(self,
                                   raw_vertices: list,
                                   output: bool = None) -> np.ndarray:
        """Returns a flattened tuple containing all X and Y coordinates visited by fish in the range
        Args:
            raw_vertices (list): List of points that bind the polygon
            output (bool): (debug tool) apply to self.positions or self.modified_positions?
        Returns:
            np.ndarray: positions sans polygonal bounded positions"""

        vertices: np.ndarray = np.array(raw_vertices)
        path: pltpath.Path = pltpath.Path(vertices)
        points_to_check: np.ndarray = self.flatten_fish_positions()
        point_bools: np.ndarray = ~path.contains_points(points_to_check)

        self.modified_positions = self.modified_positions[point_bools]
        if output is True:
            self.apply_modifications()

        return self.modified_positions

    def apply_modifications(self) -> None:
        self.positions = self.modified_positions


class NovelObjectRecognitionTest(TrajectoryObject):

    def __init__(self,
                 raw_loaded_trajectories: tt.trajectories,
                 object_locations: tuple,
                 video_path: str = None,
                 invert_y: bool = True
                 ):
        TrajectoryObject.__init__(self, raw_loaded_trajectories, video_path, invert_y)

        self.object_a: tuple = object_locations[0]
        self.object_b: tuple = object_locations[1]

    def determine_object_preference_by_frame(self,
                                             exploration_area_radius: float,
                                             fish_range: tuple = None) -> tuple:
        """Returns number of frames fish had preference for a particular object

        Args:
            exploration_area_radius (float): Frame to inspect
            fish_range (tuple): Range of fish to run on. Defaults to all fish

        Returns:
            tuple: num frames closer to object a, num frames closer to object b
        """

        if self.distance_between_points(self.object_a, self.object_b) <= exploration_area_radius:
            raise AcuityError(f"Exploration area supplied ({exploration_area_radius}) is greater than distance between novel objects "
                              f"(({self.distance_between_points(self.object_a, self.object_b)}).")

        if fish_range is None:
            fish_range = (0, self.num_fish)

        pref_a, pref_b, no_pref = 0, 0, 0
        for frame in self.positions:
            for fish in frame[fish_range[0]:fish_range[1] + 1]:
                dist_to_a, dist_to_b = self.distance_between_points(fish, self.object_a), \
                                       self.distance_between_points(fish, self.object_b)
                if dist_to_a < exploration_area_radius:
                    pref_a += 1
                elif dist_to_b < exploration_area_radius:
                    pref_b += 1
                else:
                    no_pref += 1

        return pref_a, pref_b, no_pref

