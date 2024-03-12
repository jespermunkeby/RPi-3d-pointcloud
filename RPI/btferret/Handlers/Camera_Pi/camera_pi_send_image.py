import subprocess
import os
import time
import sys
import pexpect

local_images_path = '/home/pi/deve/ble-mesh-project/camera_test/captured_images/'
btferret_path = '/home/pi/deve/btferret/'

remote_image_path = '/home/group5/deve/btferret/Handlers/Master_Pi/requested_images/'
remote_address = 'B8:27:EB:4F:D6:56' # address for rpi3bp

class StdOutWrapper:
    def __init__(self, stdout):
        self.stdout = stdout

    def write(self, s):
        if isinstance(s, str):
            s = s.encode('utf-8')
        self.stdout.buffer.write(s)

    def flush(self):
        self.stdout.flush()


def prepare_for_file_transfer(file_name):
    os.chdir(btferret_path) 
    #print(f"[camerapisendimage] Received datetime for file transfer: {file_name}")

    #os.system("sudo hciconfig hci0 piscan")
    time.sleep(2)
    
    os.chdir(btferret_path) 

    # Start the filetransfer process with pexpect
    print("starting filetransfer in pexpect")
    child = pexpect.spawn('python3 filetransfer.py', cwd=btferret_path)
    time.sleep(2)
    
    child.logfile = StdOutWrapper(sys.stdout)

    print("sending c")
    child.sendline('c')  # set camera pi as client
    time.sleep(1)
    
    print("address set")
    child.sendline(remote_address)  # MAC/BT address for master pi
    time.sleep(1)
    
    print("send file")
    child.sendline('s')  # for `send file`
    time.sleep(1)
    
    print("local image path")
    child.sendline(file_name)  # local image path
    time.sleep(1)
    
    print("remote image path")
    child.sendline(remote_image_path)  # remote path of the image dir
    time.sleep(120)
    
    # Here, you might need to adjust the interaction based on what filetransfer.py expects or outputs
    #child.expect('Transfer complete', timeout=120)  # Adjust based on the actual completion message
    
    # Disconnect both parties
    child.sendline('x')
    print("disconnected both parties")
    time.sleep(2)
    child.close()


##


##name is actuall the path I think
#def prepare_for_file_transfer(file_name):
#    # Run filetransfer.py in server mode
#    os.chdir(btferret_path) 
#    print(file_name)
#
#    # Make the device discoverable
#    subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=True)
#    time.sleep(3)
#    
#    process = subprocess.Popen(['python3', 'filetransfer.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#    time.sleep(1)
#    
#    process.stdin.write('c\n')  # set camera pi as client
#    process.stdin.flush()
#    time.sleep(2)
#
#    process.stdin.write(remote_address + '\n')  # MAC/bt address for master pi
#    process.stdin.flush()
#    time.sleep(5)
#
#    process.stdin.write('s\n')  # for `send file`
#    process.stdin.flush()
#    time.sleep(1)
#
#    process.stdin.write(file_name + '\n')  # local image path
#    process.stdin.flush()
#    time.sleep(1)
#
#    process.stdin.write(remote_image_path + '\n')  # remote path of the image dir
#    process.stdin.flush()
#    print(f"Transferring {file_name} to master pi")
#    time.sleep(15) # Waiting while it's transferring
#
#    process.stdin.write('x\n')  # disconnect both parties
#    process.stdin.flush()
#    time.sleep(2)
#
#    # Closing the process
#    process.stdin.close()
#    process.wait()


    
if __name__ == "__main__":
    # Prepare for file transfer based on the received file name
    if len(sys.argv) != 2:
        print(f"Usage: `python3 camera_pi_send_image.py <date-time of photograph>`\ne.g. 2025-02-12_10-08-23")
        sys.exit(1)


    file_name = sys.argv[1]
    print(f"[camerapisendimage]Received datetime for file transfer: {file_name}")

    # Make the device discoverable
    subprocess.run(["sudo", "hciconfig", "hci0", "piscan"], check=True)

    prepare_for_file_transfer(file_name)


