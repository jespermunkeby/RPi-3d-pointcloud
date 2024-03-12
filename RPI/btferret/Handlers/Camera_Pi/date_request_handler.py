import re
import subprocess
import os
import glob
import time
import pexpect
from datetime import datetime, timedelta

btferret_path = '/../../btferret/'
#local_image_dir = '/home/pi/deve/btferret/images/'  
#local_image_dir = '/home/pi/deve/ble-mesh-project/camera_test/captured_images/'  
local_image_dir = '/../../../ble-mesh-project/camera_test/debug_images/'  
local_handler_path= '../../btferret/Handlers/Camera_Pi/' # ?

def hex_to_ascii(hex_string):
    ascii_str = ''
    for hex_part in hex_string.split():
        try:
            ascii_str += chr(int(hex_part, 16))
        except ValueError:
            print(f"Error converting hex to ASCII: {hex_part} is not a valid hex value.")
            continue
    return ascii_str

filename_pattern = re.compile(r"(\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-?(\d{0,6})?.jpg")


def find_latest_jpg_image(directory_path):
    # Use glob to list all jpg files in the specified directory
    list_of_jpg_files = glob.glob(os.path.join(directory_path, '*.jpg'))
    
    # Check if the list is not empty
    if list_of_jpg_files:
        # Find the latest file based on creation time
        latest_jpg_file = max(list_of_jpg_files, key=os.path.getctime)
        
        # Print or return the latest jpg file
        print(f"Latest JPEG image: {latest_jpg_file}")
        return latest_jpg_file
    else:
        print("No JPEG images found in the directory.")
        return None

def parse_filename_to_datetime(filename):
    # Regex to match filenames with format "MM-DD_HH-MM-SS-ffffff.jpg"
    #match = re.match(r"(\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-?(\d{0,6})?.jpg", filename)
    match = filename_pattern.match(filename)
    if match:
        date_str, micro_str = match.groups()
        micro_str = (micro_str or '') + (6 - len(micro_str or '')) * '0'
        datetime_format = "%m-%d_%H-%M-%S"
        if micro_str:
            datetime_format += "-%f"
            date_str += "-" + micro_str
        try:
            return datetime.strptime(date_str, datetime_format)
        except ValueError as e:
            print(f"Error parsing datetime from filename: {e}")
            return None
    else:
        return None

def find_closest_image(requested_datetime_str, image_dir):
    requested_datetime = datetime.strptime(requested_datetime_str, "%m-%d_%H-%M-%S")
    closest_diff = timedelta.max
    closest_image = None

    for filename in os.listdir(image_dir):
        print("filename: ", filename)
        image_datetime = parse_filename_to_datetime(filename)
        print("image_datetime: ", image_datetime)
        if image_datetime:
            diff = abs(requested_datetime - image_datetime)
            print(f"Time difference with {filename}: {diff}")
            if diff < closest_diff:
                print(f"{filename} is now the closest file")
                closest_diff = diff
                closest_image = filename
        else:
            print(f"Skipping '{filename}', unable to parse datetime.")

    if closest_image:
        print(f"found {closest_image}")
        return os.path.join(image_dir, closest_image)
    else:
        print("aint find nothin, cuh")
        return os.path.join(image_dir, find_latest_jpg_image(image_dir))

def listen_for_datetime():
    print("starting btferret")
    child = pexpect.spawn('sudo ./btferret', cwd=btferret_path)
    #time.sleep(2)
    child.expect('h = help', timeout=20)
    child.sendline('s')  # Select server services
    #child.expect('? ', timeout=10) # some weird error
    child.sendline('3')  # Start a mesh server

    #time.sleep(2)
    child.expect('Mesh server listening', timeout=10)
    print("Listening on mesh network...")

    while True:
        try:
            #print("before expect mesh packet")
            #print(f"child = {child}")
            child.expect('Mesh packet from Pi3Bp', timeout=600)   # 1 min timeout for now
            print("after mesh packet from Pi3Bp")
            child.expect(' ', timeout=5)   
            print("after expect blank space")
            hex_message = child.readline().strip() 
            print(f"Received package from master pi: {hex_message}") 
            datetime_str = hex_to_ascii(hex_message) # actual useful datetime string from mesh
            print(f"Received package from Master Pi: {datetime_str}")
            return datetime_str

        except pexpect.TIMEOUT:
            print("Listening timeout, no messages received.")
            break
        except pexpect.EOF:
            print("btferret process ended.")
            break


    child.close()
    return None

# sends closest image from request string (%m-%d_%H-%M-%S")
def file_transfer(datetime_str):
    closest_image_path = find_closest_image(datetime_str, local_image_dir)


    if closest_image_path:
        print(f"[datetimehandler] Closest image found: {closest_image_path}")
    else:
        print("[datetimehandler] No close image found.")


    #file_name = os.path.join(local_image_dir, f"{datetime_str}.jpg")

    if not os.path.exists(closest_image_path):
        print(f"[datetimehandler] No image found for the specified datetime: {closest_image_path}")
        return

    print(f"closest image = {closest_image_path}")
    subprocess.run(['python3', 'camera_pi_send_image.py', closest_image_path], check=True, cwd=local_handler_path)

def main():
    datetime_str = listen_for_datetime()
    if datetime_str:
        print(f"[daterequesthandler] Received datetime for file transfer: {datetime_str}")
        file_transfer(datetime_str)
    else:
        print("[daterequesthandler] No datetime received or btferret timeout/exited.")

if __name__ == "__main__":
    main()
