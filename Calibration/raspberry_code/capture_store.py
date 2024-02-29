from picamera2 import Picamera2
import time
from datetime import datetime
import os
import time

picamera2 = Picamera2()
picamera2.ISO = 100

#preview_config = picamera2.create_preview_configuration()
#iso_value = 100
#preview_config["controls"]["AeExposureMode"] = 0
#preview_config["controls"]["Sensitivity"] = iso_value
#picamera2.configure(preview_config)

picamera2.configure(picamera2.create_preview_configuration(main={"size":(3280, 2464)}))

image_dir = "/home/pi/deve/ble-mesh-project/camera_test/captured_images"
os.makedirs(image_dir, exist_ok=True)

def capture_image():

    picamera2.start()

    for _ in range(5):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        file_path = os.path.join(image_dir, f"{timestamp}.jpg")

        picamera2.capture_file(file_path)
        #print(f"Image captured and stored via name: {file_path}")

        time.sleep(0.5)

    picamera2.stop()


capture_image()

