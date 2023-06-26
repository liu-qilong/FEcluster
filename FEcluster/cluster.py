
from typing import Type

import yaml
import threading
from queue import Queue

from FEcluster import mentat, task, host

class Cluster:
    def __init__(self, mentat_cwd: str = None, hosts_conf: str = 'hosts.yml'):
        self.mentat = mentat.Mentat(cwd=mentat_cwd)

        with open("hosts.yml", "r") as file:
            self.hosts = yaml.safe_load(file)

    def launch_service(self, mentat_host: str, memtat_port: int):
        # self.mentat.connect(mentat_host, memtat_port)
        self.task_queue = Queue()
        self.service_kill_event = threading.Event()

        def service_thread():
            while not self.service_kill_event.is_set():
                if not self.task_queue.empty():
                    task_obj = self.task_queue.get()

                    # mentat operation
                    task_obj.mentat(self.mentat)

                    # start job thread
                    session = self.allocate_host_session()
                    job_thread = threading.Thread(target=task_obj.job, kwargs={'host_session': session})
                    job_thread.start()

                    # start watch thread
                    job_thread = threading.Thread(target=task_obj.watch, kwargs={'host_session': session})
                    job_thread.start()

        thread = threading.Thread(target=service_thread)
        thread.start()

    def kill_service(self):
        self.service_kill_event.set()
        # self.mentat.disconnect()

    def allocate_host_session(self) -> host.HostSession:
        """mock"""
        session = host.HostSession(self.hosts['sylvia'])

    def submit_task(self, task_obj: Type[task.Task]):
        self.task_queue.put(task_obj)