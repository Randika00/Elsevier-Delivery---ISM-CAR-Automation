import psutil

def terminate_process_by_name(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            print(f"Terminating process {process_name} with PID {process.info['pid']}")
            process.terminate()
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                print(f"Process {process_name} did not terminate in time, forcing kill")
                process.kill()

process_name = 'chrome.exe'
terminate_process_by_name(process_name)