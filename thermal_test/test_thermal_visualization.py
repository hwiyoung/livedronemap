import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as mtpltcm

for root, dirs, files in os.walk('./'):
    for file in files:
        filename = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        file_path = root + '/' + file

        if extension == '.tiff':
            print('Read the image - ' + file)
            image = cv2.imread(file_path, -1)
            converted_image = image * 0.04 - 273.15

            # plot heat map image
            # https://www.geeksforgeeks.org/python-visualizing-image-in-different-color-spaces/
            plt.imshow(image, cmap='hot')
            plt.colorbar(label='color')
            plt.show()
            plt.imshow(converted_image, cmap='hot')
            plt.colorbar(label='color')
            plt.show()

            # # https://blog.bastelhalde.de/post/creating-fake-thermal-images-using-python
            # # initialize the colormap (jet)
            # # colormap = mpl.cm.jet
            # colormap = plt.cm.gist_gray   # https://pythonkim.tistory.com/82
            # # add a normalization
            # cNorm = mpl.colors.Normalize(vmin=np.min(converted_image), vmax=np.max(converted_image))
            # # init the mapping
            # scalarMap = mtpltcm.ScalarMappable(norm=cNorm, cmap=colormap)
            #
            # colors = scalarMap.to_rgba(converted_image)
            # cv2.imshow('frame', colors)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
