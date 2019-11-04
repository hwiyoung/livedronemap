import os
import numpy as np
import cv2
import time
from osgeo import ogr
from osgeo import gdal
from osgeo import osr
from server.image_processing.orthophoto_generation.ExifData import exiv2, restoreOrientation
from server.image_processing.orthophoto_generation.EoData import latlon2tmcentral, Rot3D
from server.image_processing.orthophoto_generation.Boundary import boundary
from server.image_processing.orthophoto_generation.BackprojectionResample import projectedCoord, backProjection, \
    resample, createGeoTiff, convert2PNG


def export_bbox_to_wkt(bbox, dst):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(bbox[0][0], bbox[2][0])
    ring.AddPoint(bbox[0][0], bbox[3][0])
    ring.AddPoint(bbox[1][0], bbox[2][0])
    ring.AddPoint(bbox[1][0], bbox[3][0])
    geom_poly = ogr.Geometry(ogr.wkbPolygon)
    geom_poly.AddGeometry(ring)
    wkt = geom_poly.ExportToWkt()

    # Create a polygon
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(bbox[0][0], bbox[2][0])   # Xmin, Ymin
    ring.AddPoint(bbox[0][0], bbox[3][0])   # Xmin, Ymax
    ring.AddPoint(bbox[1][0], bbox[3][0])   # Xmax, Ymax
    ring.AddPoint(bbox[1][0], bbox[2][0])   # Xmax, Ymin
    ring.AddPoint(bbox[0][0], bbox[2][0])   # Xmin, Ymin

    geom_poly = ogr.Geometry(ogr.wkbPolygon)
    geom_poly.AddGeometry(ring)

    # Export geometry to WKT
    wkt = geom_poly.ExportToWkt()

    f = open(dst + '.txt', 'w')
    f.write(wkt)
    f.close()

    return wkt


def rectify(project_path, img_fname, img_rectified_fname, eo, ground_height, sensor_width, gsd='auto'):
    """
    In order to generate individual ortho-image, this function rectifies a given drone image on a reference plane.
    :param img_fname:
    :param img_rectified_fname:
    :param eo:
    :param project_path:
    :param ground_height: Ground height in m
    :param sensor_width: Width of the sensor in mm
    :param gsd: GSD in m. If not specified, it will automatically determine gsd.
    :return File name of rectified image, boundary polygon in WKT  string
    """
    img_path = os.path.join(project_path, img_fname)

    start_time = time.time()

    print('Read the image - ' + img_fname)
    image = cv2.imread(img_path)

    # 0. Extract EXIF data from a image
    focal_length, orientation = exiv2(img_path)  # unit: m

    # 1. Restore the image based on orientation information
    restored_image = restoreOrientation(image, orientation)

    image_rows = restored_image.shape[0]
    image_cols = restored_image.shape[1]

    pixel_size = sensor_width / image_cols  # unit: mm/px
    pixel_size = pixel_size / 1000  # unit: m/px

    end_time = time.time()
    print("--- %s seconds ---" % (time.time() - start_time))

    read_time = end_time - start_time

    print('Read EOP - ' + img_fname)
    print('Easting | Northing | Height | Omega | Phi | Kappa')
    converted_eo = latlon2tmcentral(eo)
    print(converted_eo)
    R = Rot3D(converted_eo)

    # 2. Extract a projected boundary of the image
    bbox = boundary(restored_image, converted_eo, R, ground_height, pixel_size, focal_length)
    print("--- %s seconds ---" % (time.time() - start_time))

    if gsd == 'auto':
        gsd = (pixel_size * (converted_eo[2] - ground_height)) / focal_length  # unit: m/px

    # Boundary size
    boundary_cols = int((bbox[1, 0] - bbox[0, 0]) / gsd)
    boundary_rows = int((bbox[3, 0] - bbox[2, 0]) / gsd)

    print('projectedCoord')
    start_time = time.time()
    proj_coords = projectedCoord(bbox, boundary_rows, boundary_cols, gsd, converted_eo, ground_height)
    print("--- %s seconds ---" % (time.time() - start_time))

    # Image size
    image_size = np.reshape(restored_image.shape[0:2], (2, 1))

    print('backProjection')
    start_time = time.time()
    backProj_coords = backProjection(proj_coords, R, focal_length, pixel_size, image_size)

    if backProj_coords is not None:
        print("--- %s seconds ---" % (time.time() - start_time))

        print('resample')
        start_time = time.time()
        b, g, r, a = resample(backProj_coords, boundary_rows, boundary_cols, image)
        print("--- %s seconds ---" % (time.time() - start_time))

        print('Save the image in PNGA')
        start_time = time.time()
        filename = os.path.splitext(img_fname)[0]
        createGeoTiff(b, g, r, a, bbox, gsd, boundary_rows, boundary_cols, project_path + filename)
        convert2PNG(project_path + filename + '.tif', project_path + filename + '.png')  # src, dst
        print("--- %s seconds ---" % (time.time() - start_time))

        print('*** Processing time per each image')
        print("--- %s seconds ---" % (time.time() - start_time + read_time))

        bbox_wkt = export_bbox_to_wkt(bbox, dst=project_path + filename)
        return bbox_wkt
    else:
        return None
