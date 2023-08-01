from FEcluster import mentat, host

class Task:
    def __init__(self, task_name: str = 'task', nps: int = 4, nts: int = 4, nte: int = 3, nsolver: int = 6):
        self.task_name = task_name
        self.stop_watch = False
        self.complete = False

        # parallel computation settings
        self.nps, self.nts, self.nte, self.nsolver = nps, nts, nte, nsolver

    def mentat(self, mentat_obj: mentat.Mentat):
        pass

    def job(self, host_session: host.HostSession):
        pass

    def watch(self, host_session: host.HostSession):
        pass