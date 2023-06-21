import os

from FEcluster import mentat

class Cluster:
    def __init__(self, cwd: str = None):
        if cwd is None:
            self.cwd = os.getcwd()
        else:
            self.cwd = cwd

        self.mentat = mentat.Mentat(cwd=self.cwd)
        self.hosts = []