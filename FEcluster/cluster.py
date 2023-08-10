
from typing import Type

import yaml
import threading
from queue import Queue

from FEcluster import mentat, task, host

class Cluster:
    def __init__(self, hosts_conf: str = 'hosts.yml'):
        with open(hosts_conf, "r") as file:
            self.hosts = yaml.safe_load(file)

            for host_info in self.hosts.values():
                host_info['running_tasks'] = 0

    def launch_service(self):
        self.wait_queue = Queue()
        self.service_kill_event = threading.Event()

        def service_thread():
            while not self.service_kill_event.is_set():
                if not self.wait_queue.empty():
                    task_obj = self.wait_queue.get()

                    # start job thread
                    session = self.allocate_host_session()
                    job_thread = threading.Thread(target=task_obj.job, kwargs={'host_session': session})
                    job_thread.start()

                    # start watch thread
                    watch_thread = threading.Thread(target=task_obj.watch, kwargs={'host_session': session})
                    watch_thread.start()

        thread = threading.Thread(target=service_thread)
        thread.start()

    def kill_service(self):
        self.service_kill_event.set()

    def allocate_host_session(self) -> host.HostSession:
        while not self.service_kill_event.is_set():
            for host_name, host_info in self.hosts.items():
                if host_info['running_tasks'] < host_info['max_running_tasks']:
                    host_info['running_tasks'] += 1
                    return host.HostSession(host_info, host_name)

    def submit_task(self, task_obj: Type[task.Task]):
        self.wait_queue.put(task_obj)


class FECluster(Cluster):
    def launch_service(self, connect_mentat: bool = True, mentat_host: str = "127.0.0.1", mentat_port: int = 40007, mentat_cwd: str = "D:\\"):
        self.wait_queue = Queue()
        self.service_kill_event = threading.Event()

        # connect the mentat interface
        if connect_mentat:
            self.mentat = mentat.Mentat(cwd=mentat_cwd)
            self.mentat.connect(mentat_host, mentat_port)

        else:
            self.mentat = None

        def service_thread():
            while not self.service_kill_event.is_set():
                if not self.wait_queue.empty():
                    task_obj = self.wait_queue.get()

                    # mentat operation
                    if self.mentat is not None:
                        task_obj.mentat(self.mentat)

                    # start job thread
                    session = self.allocate_host_session()
                    job_thread = threading.Thread(target=task_obj.job, kwargs={'host_session': session})
                    job_thread.start()

                    # start watch thread
                    watch_thread = threading.Thread(target=task_obj.watch, kwargs={'host_session': session})
                    watch_thread.start()

        thread = threading.Thread(target=service_thread)
        thread.start()

    def kill_service(self):
        self.service_kill_event.set()
        self.mentat.disconnect()