from abc import *
import math
import numpy as np


class BaseDrone(metaclass=ABCMeta):
    polling_config = {
        'asked_health_check': False,
        'asked_sim': False,
        'checklist_result': None,
        'polling_time': 0.5,
        'timeout': 10
    }

    @abstractmethod
    def preprocess_eo_file(self, eo_path):
        """
        This abstract function parses a given EO file and returns parsed_eo (see below).
        It SHOULD BE implemented for each drone classes.

        An example of parsed_eo
        parsed_eo = [latitude, longitude, altitude, omega, phi, kappa]
        Unit of omega, phi, kappa: radian
        """
        pass

    # @abstractmethod
    def calibrate_initial_eo(self):
        pass

class VueProR(BaseDrone):
    def __init__(self, pre_calibrated=False):
        self.ipod_params = {
            "sensor_width": 10.88,  # mm
            'focal_length': 0.013,  # m
            'gsd': 0.25,            # m
            'ground_height': 363.7,     # m, 363.7(asl)
            "R_CB": np.array([[0.996892729, -0.01561805212,	-0.0772072755],
                              [0.01841927538, 0.999192656, 0.03570387246],
                              [0.07658731773, -0.03701503292, 0.9963755668]], dtype=float)  # 191029
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        # #-------------- drone_image_check --------------
        # eo_line = np.genfromtxt(
        #     eo_path,
        #     delimiter='\t',
        #     dtype={
        #         'names': ('Image', 'Longitude', 'Latitude', 'Altitude', 'Roll', 'Pitch', 'Yaw'),
        #         'formats': ('U25', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
        #     }
        # )
        # # ----------------------------------------------

        # -------------- drone_file_upload --------------
        eo_line = np.genfromtxt(
            eo_path,
            delimiter='\t',
            dtype={
                'names': ('Longitude', 'Latitude', 'Altitude', 'Roll', 'Pitch', 'Yaw'),
                'formats': ('<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
            }
        )
        # ----------------------------------------------

        eo_line['Roll'] = eo_line['Roll'] * math.pi / 180
        eo_line['Pitch'] = eo_line['Pitch'] * math.pi / 180
        eo_line['Yaw'] = eo_line['Yaw'] * math.pi / 180

        parsed_eo = [float(eo_line['Longitude']), float(eo_line['Latitude']), float(eo_line['Altitude']),
                     float(eo_line['Roll']), float(eo_line['Pitch']), float(eo_line['Yaw'])]

        return parsed_eo
