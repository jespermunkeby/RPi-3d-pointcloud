from flask import Flask, send_file, request
from datetime import datetime
import threading
import subprocess
import os
import json
import numpy as np
import open3d as o3d
from functools import reduce
import cv2

##RUN WITH BASE!!!

DEBUG = True

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}

lock = threading.Lock()
shared_refresh_images = False

# Put data from rpis 
# test it with:
# curl -X POST -F "images=@example3.jpg" -F "images=@example2.jpg" -F "images=@example1.jpg" http://localhost:5000/post 
@app.route('/post', methods=['POST'])
def put():
    if 'images' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    files = request.files.getlist('images')

    if not files or files[0].filename == '':
        return jsonify({'message': 'No selected file'}), 400

    for i, file in enumerate(files):
        file.save(f'Depth-Anything/metric_depth/my_test/input/{i}.jpg')

    #run depth anything
    working_directory = './Depth-Anything/metric_depth'
    command = ['conda', 'run', '-n', 'depth-anything', 'python', 'depth_to_pointcloud.py']
    subprocess.run(command, cwd=working_directory, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    generate_pointcloud()

    return {}

# Poll for info 
@app.route('/poll', methods=['GET'])
def poll():
    return {"refreshing_images":shared_refresh_images, "pointcloud_timestamp":pointcloud_timestamp}

# Refresh capture
@app.route('/refresh', methods=['GET'])
def refresh():
    global shared_refresh_images
    with lock:
        shared_refresh_images = True
    return {}

# Get pointcloud
@app.route('/get', methods=['GET'])
def get():
    path_to_ply_file = "pointcloud.ply"
    return send_file(path_to_ply_file, as_attachment=False, attachment_filename='model.ply')

# Calibrate camera parameters
# curl -X GET http://localhost:5000/calibrate
@app.route('/calibrate', methods=['GET'])
def calibrate():
    #calibration
    working_directory='Calibration'
    subprocess.run(['python', 'calibrate.py', '../Depth-Anything/metric_depth/my_test/input/'], stderr=subprocess.PIPE, text=True, cwd=working_directory)
    generate_pointcloud()
    return{}
    
def generate_pointcloud():
    #generates pointcloud.ply using the calibration data
    
    #Load all pointclouds

    all_files = sorted(os.listdir('Depth-Anything/metric_depth/my_test/output/'))
    pointclouds = [o3d.io.read_point_cloud("Depth-Anything/metric_depth/my_test/output/"+f) for f in all_files]

    #Load all rv, tv

    with open('Calibration/image_vectors.json', 'r') as f:
        data = json.load(f)
    
    sorted_keys = sorted(data.keys())

    rvecs = [data[key]['rotation_vector'] for key in sorted_keys]
    tvecs = [data[key]['translation_vector'] for key in sorted_keys]

    #flatten quickfix
    rvecs = [np.array([value[0] for value in vec], dtype="float32") for vec in rvecs]
    tvecs = [np.array([value[0] for value in vec], dtype="float32")  for vec in tvecs]


    pcls_with_reference_frame = list(zip(pointclouds, rvecs, tvecs))

    if DEBUG:
        #insert a visual of the reference frame in each pointcloud
        for i, (cloud, rvec, tvec) in enumerate(pcls_with_reference_frame):
            relative_frame = o3d.geometry.PointCloud(cloud)
            draw_reference_frame(relative_frame, rvec, tvec)
            draw_reference_frame(relative_frame, np.array([0,0,0],dtype="float32"), np.array([0,0,0],dtype="float32"))
            o3d.io.write_point_cloud(f"debug/relative_frame/{i}.ply", relative_frame)

            aligned_frame = o3d.geometry.PointCloud(cloud)
            draw_reference_frame(aligned_frame, rvec, tvec)
            align_pointcloud_to_origin(aligned_frame, rvec, tvec)
            draw_reference_frame(aligned_frame, np.array([0,0,0],dtype="float32"), np.array([0,0,0],dtype="float32"))

            o3d.io.write_point_cloud(f"debug/aligned_frame/{i}.ply", aligned_frame)



            

    aligned = [align_pointcloud_to_origin(cloud, rvec, tvec) for cloud, rvec, tvec in pcls_with_reference_frame]
    combined = reduce(lambda pcd1, pcd2: pcd1 + pcd2, aligned)

    # Save the combined pointcloud
    o3d.io.write_point_cloud("pointcloud.ply", combined)

def align_pointcloud_to_origin(pcd, rotation_vector, translation_vector):
    """
    Align a pointcloud to the origin by neutralizing the rotation and translation of its coordinate frame.
    """
    
    pcd.translate(-np.array([translation_vector[0], translation_vector[1], translation_vector[2]]))
    rotation_matrix, _ = cv2.Rodrigues(-np.array([rotation_vector[0], rotation_vector[1], rotation_vector[2]]))
    pcd.rotate(rotation_matrix, np.array([0,0,0], dtype="float64"))
    
    return pcd

def draw_reference_frame(pcd, rvec, tvec):
    
    # Convert rotation vector to rotation matrix
    R, _ = cv2.Rodrigues(rvec)
    x = np.array([1,0,0])
    y = np.array([0,1,0])
    z = np.array([0,0,1])

    n_points = 100
    length = 3

    for axis in [x,y,z]:
        #create all points
        axis_points = [d*axis for d in np.linspace(0, length, n_points)]
        color = np.array([axis])

        # #rotate the points
        axis_points = [R@p for p in axis_points]
        
        #translate the points
        axis_points = [p+tvec for p in axis_points]
       

        for p in axis_points:
            pcd.points = o3d.utility.Vector3dVector(np.vstack((np.asarray(pcd.points), p)))
            pcd.colors = o3d.utility.Vector3dVector(np.vstack((np.asarray(pcd.colors), color)))



        


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)

