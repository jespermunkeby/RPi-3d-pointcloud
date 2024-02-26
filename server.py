from flask import Flask, send_file
from datetime import datetime
import threading
import subprocess
import os

app = Flask(__name__)

lock = threading.Lock()
shared_refresh_images = False

pointcloud_timestamp = None
calibration = None

# Put data from rpis 
@app.route('/put', methods=['PUT'])
def put():
    #run depth anything 
    subprocess.run('python Depth-Anything/metric_depth/depth_to_pointcloud.py')

    #load the pointclouds


    #trasform them according to calibration

    #combine them and write pointcloud.ply

    return {}

# Poll for info 
@app.route('/poll', methods=['GET'])
def poll():
    return {"refreshing_calibration":shared_refresh_calibration, "refreshing_images":shared_refresh_images, "pointcloud_timestamp":pointcloud_timestamp}

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
@app.route('/calibrate', methods=['GET'])
def calibrate():
    #calibration
    return{}



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)