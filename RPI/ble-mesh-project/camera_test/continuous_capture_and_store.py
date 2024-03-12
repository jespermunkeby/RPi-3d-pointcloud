from picamera2 import Picamera2
from datetime import datetime
import os
import time

picamera2 = Picamera2()
picamera2.ISO = 100

#picamera2.configure(picamera2.create_preview_configuration(main={"size":(3280, 2464)}))
picamera2.configure(picamera2.create_preview_configuration(main={"size":(1920, 1080)}))

image_dir = "/captured_images"
os.makedirs(image_dir, exist_ok=True)

def capture_image():

    picamera2.start()

    #for _ in range(1):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    #timestamp = '2'
    file_path = os.path.join(image_dir, f"{timestamp}.jpg")

    print(f"capturing in 1")
    time.sleep(1)

    picamera2.capture_file(file_path)
    print(f"Image captured and stored via name: {file_path}")

    picamera2.stop()

if __name__ == "__main__":
    print("capturing image")
    capture_image()

