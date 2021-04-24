import numpy as np
import pandas as pd
import trajectorytools as tt
import matplotlib.path as pltpath
from pymediainfo import MediaInfo


class TrajectoryObject:
    """
    A class to store and provide basic tools for analysis of trajectories.
    """

    def __init__(self, raw_loaded_trajectories: tt.trajectories,
                 video_path: str = None,
                 invert_y: bool = True,
                 period: slice = None):

        # Set some generic params for easy inspection at a later date. Mostly just pull from tt properties
        self.num_fish: int = len(raw_loaded_trajectories.identity_labels)
        self.num_frames: int = int(raw_loaded_trajectories.number_of_frames)
        self.frame_rate: int = raw_loaded_trajectories.params['frame_rate']
        self.recording_length: float = raw_loaded_trajectories.number_of_frames / raw_loaded_trajectories.params[
            'frame_rate']

        # If a video path is supplied, we set the path as a property and extract the dimensions. A video path isn't
        # necessary though, it's really only helpful for the GUI helpers
        if video_path:
            self.video_path: str = video_path
            self.video_dimensions: tuple = get_video_dimensions(self.video_path)
        # period allows for slicing. So, we could (e.g.) grab recordings by 10 minute periods by passing incrementing
        # slices. We apply this **before** frame removal for several important reasons.
        if period is None:
            self.positions: np.ndarray = raw_loaded_trajectories.s
        else:
            self.positions: np.ndarray = raw_loaded_trajectories.s[period, :, :]

        # Organise trajectories data. tr.positions_df should be preferred over tr.positions, but both contain the
        # same data.
        if invert_y is True:
            self.positions[:, :, 1] = self.video_dimensions[1] - self.positions[:, :, 1]

        # Now we've inverted the positions array, we need to turn it into a dataframe. This is because we're giving the
        # option of removing frames. Calculations of speed assume the same time difference between datapoints, if we're
        # removing all points that lie in one area, then we're creating irregular periods between datapoints. We want
        # to store data in a table with cols X, Y, fish_id, frame_id. This is also good from a tidy-data pov.

        list_of_dicts: list = []
        # There's probably a better way of doing this, but this way turned out to be quite quick anyway
        for frame_id, frame in enumerate(self.positions):
            for fish_id, fish in enumerate(frame):
                list_of_dicts.append({'frame_id': frame_id,
                                      'fish_id': fish_id,
                                      'x_pos': fish[0],
                                      'y_pos': fish[1]})
        self.positions_df = pd.DataFrame(list_of_dicts, columns=['frame_id', 'fish_id', 'x_pos', 'y_pos'])
        self.calculate_speeds(inplace=True)

    def get_fish_pos(self,
                     fish_num: int,
                     frame_num: int) -> tuple:
        """Returns the X,Y coordinates of a fish at a requested frame

        Args:
            fish_num (int): The fish to inspect
            frame_num (int): The frame to inspect

        Returns:
            tuple: (X,Y) coordinates of a fish at a particular time
        """
        fish = self.positions_df[self.positions_df['fish_id'] == fish_num]
        row = fish[fish['frame_id'] == frame_num]
        return float(row['x_pos']), float(row['y_pos'])

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

        return np.sqrt((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2)

    def flatten_fish_positions(self) -> np.ndarray:
        """
        Returns X and Y positions of fish in numpy array
        :return: np.ndarray: list of fish positions
        """
        # todo: re-implement fish-index based slicing
        df_sel = self.positions_df[['x_pos', 'y_pos']]
        return df_sel.to_numpy()

    def remove_polygon_from_frames(self,
                                   raw_vertices: list,
                                   df: pd.DataFrame = None,
                                   inplace: bool = False,
                                   calc_speed_including_skipped_frames: bool = False) -> pd.DataFrame:
        """
        Removes all points falling inside a particular polygon from the positions_df array
        :param raw_vertices: List of vertices bounding the polygon of interest
        :param df: Dataframe to perform removal on
        :param inplace: Modify the object dataframe if true
        :param calc_speed_including_skipped_frames: Should speeds after skipped frames be NaN or calculated based on the
        time elapsed? Defaults to NaN
        :return:
        """
        if df is None:
            df = self.positions_df.copy()

        df.reset_index(inplace=True)
        point_bools = self.get_point_bools(raw_vertices, df)
        df = df[-point_bools]
        df_w_speeds = self.calculate_speeds(raw_df=df, include_skipped_frames=calc_speed_including_skipped_frames)
        if inplace is True:
            self.positions_df = df_w_speeds
        return df_w_speeds

    def trim_to_polygon(self,
                        vertices: list,
                        df: pd.DataFrame = None,
                        inplace: bool = False):
        """
        Trims out a polygon and returns all points lying within it
        :param vertices:
        :param df:
        :param inplace:
        :return:
        """

        if df is None:
            df = self.positions_df.copy()

        df.reset_index(inplace=True)
        point_bools = self.get_point_bools(vertices, df)
        df = df[point_bools]

        if inplace is True:
            self.positions_df = df

        return df

    @staticmethod
    def get_point_bools(raw_vertices: list,
                        df: pd.DataFrame) -> np.ndarray:
        """
        Method to return boolean values if point within bounded area
        :param raw_vertices: Vertices binding the polygon
        :param df: Dataframe to inspect
        :return: np.ndarray True/False
        """
        vertices: np.ndarray = np.array(raw_vertices)
        path: pltpath.Path = pltpath.Path(vertices)
        points_to_check: np.ndarray = df[['x_pos', 'y_pos']].to_numpy().astype(float)
        return pd.Series(path.contains_points(points_to_check)).astype(bool)

    def calculate_speeds(self,
                         raw_df: pd.DataFrame = None,
                         inplace: bool = False,
                         include_skipped_frames: bool = False) -> pd.DataFrame:
        """
        Method invoked when a dataframe update occurs, e.g. when we remove rows from it
        :return: None
        """
        if raw_df is None:
            df = self.positions_df.copy()
        else:
            # This is required to suppress some weird errors that occur because of
            df = raw_df.copy()

        df.sort_values(['fish_id', 'frame_id'], inplace=True)
        df['fish_match'] = df['fish_id'].diff().eq(0)
        distances = df.diff().fillna(0)
        df['distance'] = np.where(df['fish_match'] == True,
                                  np.sqrt(distances.x_pos ** 2 + distances.y_pos ** 2), np.NaN)
        # We can now calculate speeds. If include_skipped_frames is true, we'll just take an average over the timepoints
        # where the fish is missing. Obviously, this can distort the numbers quite a lot if the fish is missing for
        # a long time, so I don't do this by default
        if include_skipped_frames is True:
            df['speed'] = df.distance / (df['frame_id'].diff() * (1 / self.frame_rate))
            df['acceleration'] = df['speed'].diff() / (df['frame_id'].diff() * (1 / self.frame_rate))
        else:
            df['frame_match'] = df['frame_id'].diff().eq(1)
            df['speed'] = np.where(df['frame_match'] == True,
                                   df.distance / (df['frame_id'].diff() * (1 / self.frame_rate)), np.NaN)
            df['acceleration'] = np.where(df['frame_match'] == True,
                                          df['speed'].diff() / (df['frame_id'].diff() * (1 / self.frame_rate)), np.NaN)
        if inplace is True:
            self.positions_df = df
        return df

    def drop_errors(self,
                    factor: str,
                    cutoff: int,
                    df: pd.DataFrame = None,
                    sds: int = None,
                    inplace: bool = False,
                    recalculate: bool = False,
                    include_skip_frames_on_recalc: bool = False):
        if df is None:
            df = self.positions_df

        try:
            output_df = df[df[factor] < cutoff]
            output_df = output_df[output_df[factor] > -cutoff]

            mean = output_df[factor].mean()
            sd = output_df[factor].std()
            if sds:
                output_df = output_df[output_df[factor] < mean + sd * sds]
                output_df = output_df[output_df[factor] > mean - sd * sds]

            if recalculate is True:
                output_df = self.calculate_speeds(raw_df=output_df,
                                                  include_skipped_frames=include_skip_frames_on_recalc)

            if inplace is True:
                self.positions_df = output_df

        except KeyError:
            raise KeyError(f"{factor} does not exist in positions_df")

        return output_df


class NovelObjectRecognitionTest(TrajectoryObject):

    def __init__(self,
                 raw_loaded_trajectories: tt.trajectories,
                 object_locations: tuple,
                 video_path: str = None,
                 invert_y: bool = True,
                 period: slice = None
                 ):

        # TODO: to be reworked to avoid duplication
        TrajectoryObject.__init__(self,
                                  raw_loaded_trajectories=raw_loaded_trajectories,
                                  video_path=video_path,
                                  invert_y=invert_y,
                                  period=period)
        self.object_a: tuple = object_locations[0]
        self.object_b: tuple = object_locations[1]

        self.positions_df['dist_obj_a'] = np.sqrt((self.object_a[0] - self.positions_df['x_pos']) ** 2 +
                                                  (self.object_a[1] - self.positions_df['y_pos']) ** 2)
        self.positions_df['dist_obj_b'] = np.sqrt((self.object_b[0] - self.positions_df['x_pos']) ** 2 +
                                                  (self.object_b[1] - self.positions_df['y_pos']) ** 2)

    def determine_object_preference_by_frame(self,
                                             exploration_area_radius: float) -> tuple:
        """Returns number of frames fish had preference for a particular object.

        Args:
            exploration_area_radius (float): Frame to inspect

        Returns:
            tuple: num frames closer to object a, num frames closer to object b
        """

        if self.distance_between_points(self.object_a, self.object_b) <= exploration_area_radius:
            raise ValueError(
                f"Exploration area supplied ({exploration_area_radius}) is greater than distance between novel objects "
                f"(({self.distance_between_points(self.object_a, self.object_b)}).")

        # FILTER BY dist_obj_a and DIST_obj_b!
        pref_a = len(self.positions_df[self.positions_df['dist_obj_a'] < exploration_area_radius])
        pref_b = len(self.positions_df[self.positions_df['dist_obj_b'] < exploration_area_radius])
        no_pref = len(self.positions_df) - (pref_a + pref_b)
        return pref_a, pref_b, no_pref

    def trim_based_on_objs(self,
                           obj: str,
                           exploration_area_radius: int,
                           df: pd.DataFrame = None,
                           inplace: bool = False) -> pd.DataFrame:
        """
        Trims dataframe down to only frames where fish near objects
        :param obj: Object to inspect
        :param exploration_area_radius: Radius considered near
        :param df: Dataframe to inspect
        :param inplace: Destructively change self.positions_df?
        :return:
        """
        if df is None:
            df = self.positions_df.copy()

        df = df[df[f'dist_{obj}'] < exploration_area_radius]

        if inplace is True:
            self.positions_df = df

        return df


def get_video_dimensions(path: str) -> tuple:
    media_info: MediaInfo.parse = MediaInfo.parse(path)

    for track in media_info.tracks:
        if track.track_type == 'Video':
            video_dimensions = (track.width, track.height)
    return video_dimensions
