from abc import *
import math


class BaseDrone(metaclass=ABCMeta):
    polling_config = {
        'asked_health_check': False,
        'asked_sim': False,
        'checklist_result': None,
        'polling_time': 0.5,
        'timeout': 10
    }

    @abstractmethod
    def preprocess_eo_file(self, fname, pre_calibrated):
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


class DJIMavic(BaseDrone):
    def __init__(self, precalibrated=False):
        self.ipod_params = {
            "sensor_width": 0.00000156425,
            'focal_length': 0.0047,
            'gsd': 0.25,
            'ground_height': 0
        }
        self.precalibrated = precalibrated

    def preprocess_eo_file(self, fname):
        f = open(fname, 'r')
        if self.pre_calibrated:
            pass
        else:
            data = f.readline()
            data = data.split('\t')

            eo_line = np.genfromtxt(path, delimiter='\t',
                                    dtype={
                                        'names': ('Image', 'Latitude', 'Longitude', 'Height', 'Omega', 'Phi', 'Kappa'),
                                        'formats': ('U15', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')})

            eo_line['Omega'] = eo_line['Omega'] * math.pi / 180
            eo_line['Phi'] = eo_line['Phi'] * math.pi / 180
            eo_line['Kappa'] = eo_line['Kappa'] * math.pi / 180

            parsed_eo = [float(eo_line['Latitude']), float(eo_line['Longitude']), float(eo_line['Height']),
                         float(eo_line['Omega']), float(eo_line['Phi']), float(eo_line['Kappa'])]

            return parsed_eo
