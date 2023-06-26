import os
import time
import py_mentat as pm

class Mentat:
    def __init__(self, cwd: str = ".\\"):
        self.cwd = cwd

    def exec_proc(self, proc: str):
        pm.py_send(proc)
    
    def exec_procs(self, procs: list):
        for proc in procs:
            self.exec_proc(proc)

    def connect(self, host: str = "127.0.0.1", port: int = 40007):
        pm.py_connect(host, port)
        self.exec_proc(f'*change_directory "{self.cwd}"')

    def disconnect(self):
        pm.py_disconnect()

    def open_model(self, model_dir: str):
        self.exec_proc(f'*open_model "{model_dir}"')

    def close_model(self):
        self.exec_proc(f'*new_model yes')

    def export_dat(self, export_folder: str = '.\\output', export_name: str = 'input'):
        # create export_path if it doesn't exist
        export_path = os.path.join(self.cwd, export_folder)
        if not os.path.exists(export_path):
            os.makedirs(export_path)
            
        pm.py_send(f'*write_marc "{os.path.join(export_folder, export_name)}.dat" yes')

    def write_log(self, task_name: str = 'task', description: str = 'mentat interface operation'):
        current_time = time.strftime("%H:%M:%S")

        print(f'mentat:{task_name}\n\033[32m{current_time} > successful > {description}\033[0m')