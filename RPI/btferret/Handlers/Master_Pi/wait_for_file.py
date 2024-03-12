import subprocess
import pexpect
import os
import time

btferret_path = '../../btferret/'

def filetransfer_server():
    os.chdir(btferret_path)

    # Make the device discoverable
    subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'])
    time.sleep(1)

    child = pexpect.spawn('python3 filetransfer.py', cwd=btferret_path)
    time.sleep(1)

    child.sendline('s')  # set this device to be server

    # Wait for the server to indicate it's waiting for a connection or has received a connection
    print("Server set. Waiting for connections...")

    while not child.expect(pexpect.EOF):
        sleep(5)

    child.terminate()


    print("something happened")

def main():
    filetransfer_server()

if __name__ == "__main__":
    main()


