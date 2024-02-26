from flask import Flask, send_file, request
from datetime import datetime
import threading
import subprocess
import os

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}

lock = threading.Lock()
shared_refresh_images = False

# Put data from rpis 
@app.route('/post', methods=['POST'])
def put():
    if 'images' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    files = request.files.getlist('images')

    if not files or files[0].filename == '':
        return jsonify({'message': 'No selected file'}), 400

    for i, file in enumerate(files):
        file.save(f"Depth-Anything/metric_depth/my_test/input/{i}.jpg")
        
    #clear input and output folders

    #add images to input folder
    print(subprocess.run('pwd'))
    #run depth anything 
    working_directory = './Depth-Anything/metric_depth'
    subprocess.run(['python','depth_to_pointcloud.py'], cwd=working_directory)

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
@app.route('/calibrate', methods=['GET'])
def calibrate():
    #calibration
    #TODO: call calibration code
    generate_pointcloud()
    subprocess.run('todo')
    return{}

def generate_pointcloud():
    #generates pointcloud.ply using the calibration data
    pass

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)