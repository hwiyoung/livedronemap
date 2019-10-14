import socket

class BaseConfig:
    MAGO3D_ADDRESS = 'http://61.38.45.99:20080/'
    # LDM_ADDRESS = 'http://' + socket.gethostbyname(socket.getfqdn())  + ':5000/' # Local server
    LDM_ADDRESS = 'http://localhost:8080/'  # Local server
    LDM_PROJECT_NAME = 'watchdog'
    DIRECTORY_TO_WATCH = 'drone/downloads'
    # DIRECTORY_IMAGE_CHECK = 'drone/examples'
    DIRECTORY_IMAGE_CHECK = '.'
    IMAGE_FILE_EXT = 'tiff'
    EO_FILE_EXT = 'txt'
    UPLOAD_INTERVAL = 1
