import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from drone.config import BaseConfig as Config
from clients.ldm_client import Livedronemap
import subprocess
import os

image_list = []
eo_list = []

ldm = Livedronemap(Config.LDM_ADDRESS)
project_id = ldm.create_project(Config.LDM_PROJECT_NAME)
ldm.set_current_project(project_id)

print('Current project ID: %s' % project_id)


def upload_data(image_fname, eo_fname):
    result = ldm.ldm_upload(image_fname, eo_fname)
    print('response from LDM server:')
    print(result)


def get_metadata_exiftool(input_file):
    # input_file = "C:/DJI_0018.MOV"    # Model - 1929
    # input_file = "C:/DJI_0114.MOV"  # Model - 1933
    exe = "exiftool.exe"

    process = subprocess.Popen([exe, input_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    metadata = process.stdout.read().decode()
    if not(metadata.find('GPS Longitude                   : ') == -1):
        longitude_field = metadata.find('GPS Longitude                   : ')
        latitude_field = metadata.find('GPS Latitude                    : ')
        altitude_field = metadata.find('GPS Altitude                    : ')
        roll_field = metadata.find('MAV Roll')
        pitch_field = metadata.find('MAV Pitch')
        yaw_field = metadata.find('MAV Yaw')

        """ Longitude """
        lon_deg_value = float(metadata[longitude_field + 34:longitude_field + 34 + 3])
        lon_min_value = float(metadata[longitude_field + 34 + 3 + 5:longitude_field + 34 + 3 + 5 + 2])
        try:
            lon_sec_value = float(
                metadata[longitude_field + 34 + 3 + 5 + 2 + 2:longitude_field + 34 + 3 + 5 + 2 + 2 + 5])
        except ValueError:
            lon_sec_value = float(
                metadata[longitude_field + 34 + 3 + 5 + 2 + 2:longitude_field + 34 + 3 + 5 + 2 + 2 + 4])
        lon_value = lon_deg_value + lon_min_value / 60 + lon_sec_value / 3600

        """ Latitude """
        lat_deg_value = float(metadata[latitude_field + 34:latitude_field + 34 + 2])
        lat_min_value = float(metadata[latitude_field + 34 + 2 + 5:latitude_field + 34 + 2 + 5 + 2])
        try:
            lat_sec_value = float(
                metadata[latitude_field + 34 + 2 + 5 + 2 + 2:latitude_field + 34 + 2 + 5 + 2 + 2 + 5])
        except ValueError:
            lat_sec_value = float(
                metadata[latitude_field + 34 + 2 + 5 + 2 + 2:latitude_field + 34 + 2 + 5 + 2 + 2 + 4])
        lat_value = lat_deg_value + lat_min_value / 60 + lat_sec_value / 3600

        """ Altitude """
        try:
            alt_value = float(metadata[altitude_field + 34:altitude_field + 34 + 5])
        except ValueError:
            alt_value = float(metadata[altitude_field + 34:altitude_field + 34 + 3])

        """ Roll """
        roll_value = float(metadata[roll_field + 34:roll_field + 34 + 6].split("\r")[0])
        """ Pitch """
        pitch_value = float(metadata[pitch_field + 34:pitch_field + 34 + 6].split("\r")[0])
        """ Yaw """
        yaw_value = float(metadata[yaw_field + 34:yaw_field + 34 + 6].split("\r")[0])

        result = {
            'longitude': lon_value,
            'latitude': lat_value,
            'altitude': alt_value,
            'roll': roll_value,
            'pitch': pitch_value,
            'yaw': yaw_value
        }

        return result
    else:
        return None


class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            path = event.src_path.split('\\')[0]
            file_name = event.src_path.split('\\')[-1].split('.')[0]
            extension_name = event.src_path.split('.')[-1]
            # print(path + '/' + file_name + '.' + extension_name)
            print('A new file detected: %s' % file_name)
            print('extenstion: ', extension_name)
            if Config.IMAGE_FILE_EXT in extension_name:
                image_list.append(file_name)
                #############################
                time.sleep(1)
                #############################
                eo_dict = get_metadata_exiftool(path + "/" + file_name + "." + extension_name)
                if not(eo_dict is None):
                    with open(path + "/" + file_name + '.' + Config.EO_FILE_EXT, 'w') as f:
                        eo_file_data = str(eo_dict['longitude']) + '\t' + \
                                       str(eo_dict['latitude']) + '\t' + \
                                       str(eo_dict['altitude']) + '\t' + \
                                       str(eo_dict['roll']) + '\t' + \
                                       str(eo_dict['pitch']) + '\t' + \
                                       str(eo_dict['yaw'])
                        print(eo_file_data)
                        f.write(eo_file_data)
                    eo_list.append(file_name + Config.EO_FILE_EXT)
                    print('uploading data...')
                    upload_data(
                        event.src_path,
                        path + "/" + file_name + '.' + Config.EO_FILE_EXT
                    )
                else:
                    print("The image is broken")
                    print('===========================================================')
                    return
            else:
                print('But it is not an image file.')
            print('===========================================================')


if __name__ == '__main__':
    if not (os.path.isdir(Config.DIRECTORY_TO_WATCH)):
        os.mkdir(Config.DIRECTORY_TO_WATCH)
        print("The folder is created")

    filelist = [f for f in os.listdir(Config.DIRECTORY_TO_WATCH)]
    for f in filelist:
        os.remove(Config.DIRECTORY_TO_WATCH + "/" + f)
    print('Removal is done!')

    w = Watcher(directory_to_watch=Config.DIRECTORY_TO_WATCH)
    w.run()
