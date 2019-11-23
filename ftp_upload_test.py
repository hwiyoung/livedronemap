import shutil
import os
import time

# local_path = 'C:/Users/InnoPAM/Desktop/20191121/1/'
# local_path = 'C:/Users/InnoPAM/Desktop/20191121/2-500m/'
# local_path = 'C:/Users/InnoPAM/Desktop/20191121/3-700/'
# local_path = 'C:/Users/InnoPAM/Desktop/20191121/4-1000m/'
# local_path = 'C:/Users/InnoPAM/Desktop/20191121/5-1000m500mRTL/'
# local_path = 'C:/Users/InnoPAM/Desktop/20191121/6-1000m500m/'
local_path = 'C:/Users/InnoPAM/Desktop/20191121/7-1000m1000m/'
remote_path = 'drone/downloads/'

for root, dirs, files in os.walk(local_path):
    files.sort()
    for file in files:
        print("Copy ", local_path + file, " to ", remote_path + file)
        shutil.copy(local_path + file, remote_path + file)
        ############################
        time.sleep(1)
        ############################

print("Done")
