import os
import numpy as np
import cv2

for root, dirs, files in os.walk('./'):
    for file in files:
        filename = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        file_path = root + '/' + file

        image = cv2.imread(file_path, -1)
        print('Read: ' + file)

        # if extension == '.JPG':
        #     print('Read the image - ' + file)
        #     image = cv2.imread(file_path, -1)
