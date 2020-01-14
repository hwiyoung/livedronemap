import json
import os
import time
import cv2
import socket
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request
from werkzeug.utils import secure_filename

from config import config_flask
from server.image_processing.img_metadata_generation import create_img_metadata
from clients.webodm import WebODM
from clients.mago3d import Mago3D
# from drone.drone_image_check import start_image_check
from drone_image_check import start_image_check

from server.image_processing.orthophoto_generation.Orthophoto import rectify
from server.image_processing.system_calibration import calibrate

# Convert pixel bbox to world bbox
from server.image_processing.orthophoto_generation.Boundary import pcs2ccs, projection
from server.image_processing.orthophoto_generation.EoData import Rot3D, latlon2tmcentral, tmcentral2latlon

# # socket for sending
# TCP_IP = '192.168.0.24'
# TCP_PORT = 5001 #18080
# 
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 
# s.connect((TCP_IP, TCP_PORT))
# print('connected!')


# Initialize flask
app = Flask(__name__)
app.config.from_object(config_flask.BaseConfig)

# Initialize multi-thread
executor = ThreadPoolExecutor(2)

# # Initialize Mago3D client
# mago3d = Mago3D(
#     url=app.config['MAGO3D_CONFIG']['url'],
#     user_id=app.config['MAGO3D_CONFIG']['user_id'],
#     api_key=app.config['MAGO3D_CONFIG']['api_key']
# )

from server.my_drones import DJIMavic
my_drone = DJIMavic(pre_calibrated=True)

def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/project/', methods=['GET', 'POST'])
def project():
    """
    GET : Query project list
    POST : Add a new project
    :return: project_list (GET), project_id (POST)
    """
    if request.method == 'GET':
        project_list = os.listdir(app.config['UPLOAD_FOLDER'])
        return json.dumps(project_list)
    if request.method == 'POST':
        project_id = 'LOCAL_%s' % round(time.time())

        # Using the assigned ID, ldm makes a new folder to projects directory
        new_project_dir = os.path.join(app.config['UPLOAD_FOLDER'], project_id)
        os.mkdir(new_project_dir)

        # LDM returns the project ID that Mago3D assigned
        return project_id


# 라이브 드론맵: 이미지 업로드, 기하보정 및 가시화
@app.route('/ldm_upload/<project_id_str>', methods=['POST'])
def ldm_upload(project_id_str):
    """
    POST : Input images to the image processing and object detection chain of LDM
    The image processing and object detection chain of LDM covers following procedures.
        1) System calibration
        2) Individual ortho-image generation
        3) Object detection (red tide, ship, etc.)
    :param project_id_str: project_id which LDM assigned for each projects
    :return:
    """
    if request.method == 'POST':
        # Initialize variables
        project_path = os.path.join(app.config['UPLOAD_FOLDER'], project_id_str)
        fname_dict = {
            'img': None,
            'img_rectified': None,
            'eo': None
        }

        # Check integrity of uploaded files
        for key in ['img', 'eo']:
            if key not in request.files:  # Key check
                return 'No %s part' % key
            file = request.files[key]
            if file.filename == '':  # Value check
                return 'No selected file'
            if file and allowed_file(file.filename):  # If the keys and corresponding values are OK
                fname_dict[key] = secure_filename(file.filename)
                file.save(os.path.join(project_path, fname_dict[key]))  # 클라이언트로부터 전송받은 파일을 저장한다.
            else:
                return 'Failed to save the uploaded files'

        # IPOD chain 1: System calibration
        parsed_eo = my_drone.preprocess_eo_file(os.path.join(project_path, fname_dict['eo']))
        if not my_drone.pre_calibrated:
            OPK = calibrate(parsed_eo[3], parsed_eo[4], parsed_eo[5], my_drone.ipod_params["R_CB"])
            parsed_eo[3] = OPK[0]
            parsed_eo[4] = OPK[1]
            parsed_eo[5] = OPK[2]

        if abs(OPK[0]) > 0.175 or abs(OPK[1]) > 0.175:
            print('Too much omega/phi will kill you')
            return 'Too much omega/phi will kill you'

        # IPOD chain 2: Individual orthophoto generation
        fname_dict['img_rectified'] = fname_dict['img'].split('.')[0][:-3] + '.tif'
        bbox_wkt = rectify(
            project_path=project_path,
            img_fname=fname_dict['img'],
            img_rectified_fname=fname_dict['img_rectified'],
            eo=parsed_eo,
            ground_height=my_drone.ipod_params['ground_height'],
            sensor_width=my_drone.ipod_params['sensor_width']
        )

        # if bbox_wkt is not None:
        #     detected_objects=[]
        #     # IPOD chain 3: Object detection
        #     imgencode = cv2.imread(project_path + '/' + fname_dict['img'])
        #     print(project_path + '/' + fname_dict['img'])
        #     hei = imgencode.shape[0]
        #     wid = imgencode.shape[1]
        # 
        #     stringData = imgencode.tostring()
        # 
        #     s.send(str(hei).encode().ljust(16))
        #     s.send(str(wid).encode().ljust(16))
        #     s.send(stringData)
        #     print("start sending")
        # 
        #     # Receiving Bbox info
        #     data_len = s.recv(16)
        # 
        #     x1 = json.loads(s.recv(int(data_len)))
        #     y1 = json.loads(s.recv(int(data_len)))
        #     x2 = json.loads(s.recv(int(data_len)))
        #     y2 = json.loads(s.recv(int(data_len)))
        # 
        #     print("BBox info received!!!!!")
        #     for i in range(len(x1)):
        #         bbox_px = np.array([[x1[i], x2[i], x2[i], x1[i]], [y2[i], y2[i], y1[i], y1[i]]])
        # 
        #         tm_eo = latlon2tmcentral(parsed_eo)
        #         R_GC = Rot3D(tm_eo)
        #         R_CG = R_GC.transpose()
        # 
        #         print("bbox is like this", bbox_px)
        # 
        #         # Convert pixel coordinate system to camera coordinate system
        #         bbox_camera = pcs2ccs(bbox_px, hei, wid,
        #                               my_drone.ipod_params['sensor_width'] / wid,
        #                               my_drone.ipod_params['focal_length'] * 1000)  # shape: 3 x bbox_point
        #         # input params unit: px, px, px, mm/px, mm
        # 
        #         # Project camera coordinates to ground coordinates
        #         proj_coordinates = projection(bbox_camera, tm_eo, R_CG,
        #                                       my_drone.ipod_params['ground_height'])
        # 
        #         bbox_ground1 = tmcentral2latlon(proj_coordinates[:, 0])
        #         bbox_ground2 = tmcentral2latlon(proj_coordinates[:, 1])
        #         bbox_ground3 = tmcentral2latlon(proj_coordinates[:, 2])
        #         bbox_ground4 = tmcentral2latlon(proj_coordinates[:, 3])
        # 
        #         print(bbox_ground1, '\n', bbox_ground2, '\n', bbox_ground3, '\n', bbox_ground4)
        # 
        #         bboxcenter0 = np.mean(np.array([bbox_ground1[0], bbox_ground2[0], bbox_ground3[0], bbox_ground4[0]]))
        #         bboxcenter1 = np.mean(np.array([bbox_ground1[1], bbox_ground2[1], bbox_ground3[1], bbox_ground4[1]]))
        #         detected_objects_single = {
        #             "number": 0,
        #             "ortho_detected_object_id": None,
        #             "drone_project_id": None,
        #             "ortho_image_id": None,
        #             "user_id": None,
        #             "object_type": "0",
        #             "geometry": "POINT (%f %f)" % (bboxcenter0, bboxcenter1),
        #             "detected_date": "20180929203800",
        #             "bounding_box_geometry": "POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))"
        #                                      % (bbox_ground1[0], bbox_ground1[1],
        #                                         bbox_ground2[0], bbox_ground2[1],
        #                                         bbox_ground3[0], bbox_ground3[1],
        #                                         bbox_ground4[0], bbox_ground4[1],
        #                                         bbox_ground1[0], bbox_ground1[1]),
        #             "major_axis": None,  # 30,
        #             "minor_axis": None,  # 50,
        #             "orientation": None,  # 260,
        #             "bounding_box_area": None,  # 150,
        #             "length": None,  # 30,
        #             "speed": None,  # 12,
        #             "insert_date": None}
        # 
        #         detected_objects.append(detected_objects_single)
        # 
        #         return 'Image upload and IPOD chain complete'
        #     else:
        #         pass



@app.route('/check/drone_polling')
def check_drone_polling():
    """
    Maintains polling connection with drone system. Whenever Mago3D asks to check the drone system (START_HEALTH_CHECK),
    this polling connection will be disconnected and be connected again immediately.
    :return:
    """
    app.config['DRONE']['asked_health_check'] = False
    app.config['DRONE']['asked_sim'] = False
    while True:
        time.sleep(app.config['DRONE']['polling_time'])
        if app.config['DRONE']['asked_health_check']:
            return 'START_HEALTH_CHECK'
        elif app.config['DRONE']['asked_sim']:
            return app.config['SIMULATION_ID']


@app.route('/check/drone_checklist_result')
def check_drone_result():
    app.config['DRONE']['checklist_result'] = 'OK'
    return 'OK'


@app.route('/check/drone')
def check_drone():
    app.config['DRONE']['asked_health_check'] = True
    time.sleep(app.config['DRONE']['timeout'])
    if app.config['DRONE']['checklist_result'] == 'OK':
        app.config['DRONE']['checklist_result'] = 'None'
        return 'OK'
    else:
        return 'DISCONNECTED_OR_NOT_RESPONDING'


@app.route('/check/beacon')
def check_beacon():
    # UN Test
    return 'OK'


@app.route('/check/sim/from_ldm')
def check_sim_from_ldm():
    app.config['SIMULATION_ID'] = request.args.get('simulation_id')
    executor.submit(start_image_check, app.config['SIMULATION_ID'])
    return 'OK'


@app.route('/check/sim/from_drone')
def check_sim_from_drone():
    app.config['SIMULATION_ID'] = request.args.get('simulation_id')
    app.config['DRONE']['asked_sim'] = True
    return 'OK'


# 오픈드론맵: 후처리
@app.route('/webodm_upload/start_processing/<project_id>')
def webodm_start_processing(project_id_str):
    webodm = WebODM(
        url=app.config['WEBODM_CONFIG']['url'],
        username=app.config['WEBODM_CONFIG']['username'],
        password=app.config['WEBODM_CONFIG']['password']
    )
    webodm.create_project(project_name=project_id_str)
    project_folder = 'project/' + project_id_str
    webodm.create_task(project_folder)

    return 'ODM'


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=30005)
    # socket.close()


