import requests
import subprocess
import time
import os
from datetime import datetime
import pexpect

# Configuration
server_url = "http://your.server.ip:port"
polling_interval = 20  # seconds
btferret_path = '../../btferret/' # TODO: make sure this is right
master_pi_handler_path = f'{bt_ferret_path}/Master_Pi/'

def poll_for_datetime_request():
    response = requests.get(f"{server_url}/poll")

    if response.status_code == 200:
        data = response.json()
        if data.get("refreshing_images"):
            # Assuming the server sends the datetime string when refreshing_images is True
            datetime_str = data.get("pointcloud_timestamp")
            print(f"datetime string in poll function: {datetime_str}")
            return datetime_str
    return None

def send_datetime_to_mesh(datetime_str):

    child = pexpect.spawn('sudo ./btferret', cwd=btferret_path)
    print("after pexpect.spawn")
    time.sleep(3)
    child.sendline('T')
    child.sendline(datetime_str)
    child.sendline('q')
    child.expect(pexpect.EOF)


    #process.wait()

def wait_for_file_and_upload():
    # Assuming subprocess.run(['python3', 'wait_for_file.py'], cwd=master_pi_handler_path) is handled elsewhere.
    subprocess.run(['python3', 'wait_for_file.py'], cwd=master_pi_handler_path)

    req_images_dir = '/home/group5/deve/btferret/Handlers/Master_Pi/requested_images/'
    post_url = server_url + '/post'

    # Collecting all the image files in the directory
    files = [('images', (filename, open(os.path.join(req_images_dir, filename), 'rb'))) for filename in os.listdir(req_images_dir) if filename.endswith('.jpg')]

    # Check if there are any files to upload
    if not files:
        print("No images found for upload.")
        return

    # Sending all files in a single POST request
    response = requests.post(post_url, files=files)

    # Closing all the files that were opened
    for _, file_tuple in files:
        file_tuple[1].close()

    if response.status_code == 200:
        print("Uploaded all files successfully.")
    else:
        print("Failed to upload files.")



def main():
    while True:
        datetime_str = poll_for_datetime_request()
        if datetime_str:
            print(f"New datetime request received: {datetime_str}")
            send_datetime_to_mesh(datetime_str)
            print("After send_datetime_to_mesh function")
            #time.sleep(10)
            wait_for_file_and_upload()
        else:
            print(f"No new datetime request. Polling again in {polling_interval} seconds.")
        time.sleep(polling_interval)

if __name__ == "__main__":
    main()

