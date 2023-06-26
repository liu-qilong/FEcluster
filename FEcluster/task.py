from FEcluster import mentat, host

class Task:
    def __init__(self, task_name: str = 'task'):
        self.name = task_name

    def mentat(self, mentat_obj: mentat.Mentat):
        pass

    def job(self, host_session: host.HostSession):
        pass

    def watch(self, host_session: host.HostSession):
        pass