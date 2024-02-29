from picamera2 import Picamera2
import numpy as np
import time
from datetime import datetime, timedelta
import os
import time
import cv2
import psutil

picamera2 = Picamera2()
picamera2.configure(picamera2.create_preview_configuration(main={"size":(1920, 1080)}))

image_dir = "/home/pi/deve/ble-mesh-project/camera_test/captured_images"
os.makedirs(image_dir, exist_ok=True)

fps = 10
duration = 5 # seconds

def capture_image_to_buffer(duration=5, fps=10, threshold=85):
    picamera2.start()
    frames = []
    timestamps = []
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration)

    while datetime.now() < end_time:
        #frames.append(picamera2.capture_array())
        frame = np.empty((1080,1920,3), dtype=np.uint8)
        picamera2.capture_request(frame)
        frames.append(frame)
        timestamps.append(datetime.now())
        time.sleep(1/fps)

    picamera2.stop()
    return frames, timestamps


def write_frames_to_disk(frames, timestamps):
    for f, t in zip(frames, timestamps):
        filename = os.path.join(image_dir, t.strftime("%Y-%m-%d_%H-%M-%S-%f") + ".jpg")
        cv2.imwrite(filename, f)

    print('done writing images from ram to disk')

fs, ts = capture_image_to_buffer(duration, fps)
write_frames_to_disk(fs, ts)



