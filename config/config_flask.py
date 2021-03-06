import json
from abc import *


class BaseConfig(object, metaclass=ABCMeta):
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = '/hdd/ldm_workspace'
    ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])
    WEBODM_CONFIG = json.load(open('config/config_webodm.json', 'r'))
    MAGO3D_CONFIG = json.load(open('config/config_mago3d.json', 'r'))
    SIMULATION_ID = None
    CALIBRATION = True
