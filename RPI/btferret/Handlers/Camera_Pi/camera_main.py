import threading
import subprocess
import time
import os
import logging
import signal
from picamera2 import Picamera2
from datetime import datetime
from shutil import copy2



date_request_handler = './date_request_handler.py'
captured_images = '../../../captured_images/'

os.makedirs(captured_images, exist_ok=True)

# Initialize logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def capture_photos_continuously(debug=False, calibrate=False): 
    debug_img = "/home/pi/deve/ble-mesh-project/camera_test/debug_images/03-07_17-33-55-438471.jpg"
    calibrate_img = "/home/pi/deve/ble-mesh-project/camera_test/calibrate_images/03-07_17-33-55-438471.jpg"
    #debug_img = "/home/pi/deve/ble-mesh-project/camera_test/debug_images/2.jpg"

    picamera2 = Picamera2()
    picamera2.ISO = 100
    picamera2.configure(picamera2.create_preview_configuration(main={"size":(3280, 2464)}))
    #picamera2.configure(picamera2.create_preview_configuration(main={"size":(1920, 1080)}))

    if not debug:
        picamera2.start()

    while True:
        try:
            timestamp = datetime.now().strftime("%m-%d_%H-%M-%S-%f")
            file_path = os.path.join(captured_images, f"{timestamp}.jpg")

            if debug:
                if calibrate:
                    if os.path.exists(calibrate_img):
                        print("faking picture in 30...")
                        time.sleep(30)  
                        copy2(calibrate_img, file_path)

                if os.path.exists(debug_img):
                    print("faking picture in 30...")
                    time.sleep(30)  
                    copy2(debug_img, file_path)
                else:
                    loggin.error("debug mode, but couldn't find photo")
                    break
            else:
                print("taking picture in 1...")
                picamera2.capture_file(file_path)

            #logging.info(f"Image captured and stored as: {file_path}")
            #time.sleep(1)  

        except Exception as e:
            if not debug:
                picamera2.stop()
            #logging.error(f"Error during photo capture: {e}")
            break

def listen_for_master_mesh_request():
    while True:
        try:
            print("while true, try inside listen for mesh req")
            #logging.info("Listening for datetime requests...")
            subprocess.run(['python3', date_request_handler], check=True)
            #logging.info("Datetime request handled.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during datetime request handling: {e}")
        except KeyboardInterrupt:
            break

def main():
    #Start the continuous photo capture in a separate thread
    photo_thread = threading.Thread(target=capture_photos_continuously, args=(True, True), daemon=True)
    photo_thread.start()

    #Handle mesh network listening and file transfer in the main thread
    try:
        listen_for_master_mesh_request()
    except KeyboardInterrupt:
        logging.info("Shutting down...")

if __name__ == '__main__':
    main()

