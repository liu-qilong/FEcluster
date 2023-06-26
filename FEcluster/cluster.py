
from typing import Type

import yaml
import threading
from queue import Queue

from FEcluster import mentat, task

class Cluster:
    def __init__(self, mentat_cwd: str = None, hosts_conf: str = 'hosts.yml'):
        self.mentat = mentat.Mentat(cwd=mentat_cwd)

        with open("hosts.yml", "r") as file:
            self.hosts = yaml.safe_load(file)

    def launch_mentat_server(self, host: str, port: int):
        self.mentat_queue = Queue()
        self.mentat_kill_event = threading.Event()
        # self.mentat.connect(host, port)

        def mentat_thread(event):
            while not event.is_set():
                if not self.mentat_queue.empty():
                    task_obj = self.mentat_queue.get()
                    task_obj.mentat(self.mentat)

        thread = threading.Thread(
            target = mentat_thread,
            kwargs = { 'event': self.mentat_kill_event },
            )
        thread.start()

    def kill_mentat_server(self):
        self.mentat_kill_event.set()
        # self.mentat.disconnect()

    def submit_task(self, task_obj: Type[task.Task]):
        self.mentat_queue.put(task_obj)