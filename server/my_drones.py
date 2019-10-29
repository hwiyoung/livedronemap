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
            'ground_height': 0,   # m
            "R_CB": np.array(
                [[0.8780885519,	-0.4770646178, 0.03701142457],
                 [0.4760363467,	0.8631176389, -0.1685744288],
                 [0.04847568207, 0.1656420594, 0.9849938154]], dtype=float)  # Must check
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        # eo_line = np.genfromtxt(
        #     eo_path,
        #     delimiter='\t',
        #     dtype={
        #         'names': ('Image', 'Latitude', 'Longitude', 'Altitude', 'Roll', 'Pitch', 'Yaw'),
        #         'formats': ('U15', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
        #     }
        # )

        eo_line = np.genfromtxt(
            eo_path,
            delimiter='\t',
            dtype={
                'names': ('Latitude', 'Longitude', 'Altitude', 'Roll', 'Pitch', 'Yaw'),
                'formats': ('<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
            }
        )

        eo_line['Roll'] = eo_line['Roll'] * math.pi / 180
        eo_line['Pitch'] = eo_line['Pitch'] * math.pi / 180
        eo_line['Yaw'] = eo_line['Yaw'] * math.pi / 180

        parsed_eo = [float(eo_line['Longitude']), float(eo_line['Latitude']), float(eo_line['Altitude']),
                     float(eo_line['Roll']), float(eo_line['Pitch']), float(eo_line['Yaw'])]

        return parsed_eo
