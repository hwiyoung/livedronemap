class BaseConfig:
    # LDM_ADDRESS = 'http://61.38.45.117:5000/'
    #MAGO3D_ADDRESS = 'http://61.38.45.117:20080/'
    LDM_ADDRESS = 'http://192.168.0.8:8080/'	# Myself
    MAGO3D_ADDRESS = 'http://192.168.0.4/'	# Share computer
    LDM_PROJECT_NAME = 'watchdog'
    DIRECTORY_TO_WATCH = 'drone/downloads'
    # DIRECTORY_IMAGE_CHECK = 'drone/examples'
    DIRECTORY_IMAGE_CHECK = '.'
    IMAGE_FILE_EXT = 'jpg'
    EO_FILE_EXT = 'txt'
    UPLOAD_INTERVAL = 1
