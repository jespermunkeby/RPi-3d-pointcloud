import subprocess
import time
import os
import fcntl

def non_blocking_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    try:
        return output.read()
    except Exception:
        return ""

def run_btferret_commands():
    process = subprocess.Popen(['sudo', './btferret'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True, bufsize=1)

    # Make stdout non-blocking
    fcntl.fcntl(process.stdout.fileno(),fcntl.F_SETFL,fcntl.fcntl(process.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)

    #commands = ['s\n', '3\n', 'x\n', 'q\n']
    commands = ['s\n', '3\n']

    for cmd in commands:
        print(f"Sending command: {cmd.strip()}")
        process.stdin.write(cmd)
        process.stdin.flush()
        time.sleep(1)  # Adjust based on the expected response time

        # Attempt to read the response
        stdout = non_blocking_read(process.stdout)
        if stdout:
            print("STDOUT:", stdout)
        else:
            print("No output or output not captured")
        time.sleep(2)


    for i in range(100):
        print(i,'\n')
        stdout = non_blocking_read(process.stdout)
        if stdout:
            print("STDOUT:\n", stdout)
        else:
            print("No output or output not captured")
        time.sleep(2)

    process.stdin.close()
    process.wait()

run_btferret_commands()

