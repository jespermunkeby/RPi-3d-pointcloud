import subprocess
import time

btferret_path = '/../../btferret/'
master_pi_handler_path = '/' # TODO

def send_datetime_to_mesh(datetime_str):
    process = subprocess.Popen(['sudo', './btferret'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=btferret_path)
    time.sleep(2) # wait for boot 
    
    print(f"sending {datetime_str} to mesh network")
    process.stdin.write('T\n')  # Command to send string to mesh network
    time.sleep(2)
    process.stdin.write(f"{ datetime_str}\n")  # Sending datetime to mesh

    time.sleep(2)
    process.stdin.write('q\n')  # Quit btferret
    process.stdin.flush()
    process.wait()

# This function starts the file transfer server
def wait_for_file():
    print("listening for connections.")
    subprocess.run(['python3', 'wait_for_file.py'], cwd=master_pi_handler_path)

def main():
    datetime_str = input("Enter the datetime to send (format MM-DD_HH-MM-SS)")
    send_datetime_to_mesh(datetime_str)
    wait_for_file()

if __name__ == "__main__":
    main()

