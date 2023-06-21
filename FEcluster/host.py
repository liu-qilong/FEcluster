import os
import time
import paramiko
import subprocess

class HostSession:
    def __init__(self, addr: str, user: str, local_cwd: str, remote_cwd: str, session_name: str = None):
        self.session_name = session_name
        self.addr = addr
        self.user = user
        self.local_cwd = local_cwd
        self.remote_cwd = remote_cwd

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(hostname=self.addr, username=self.user)

        # create local_cwd if it doesn't exist
        if not self.local_shell_exec(commands='', is_log=False):
            self.local_mkdir(self.local_cwd, cwd='~', description='create local cwd')

        # create remote_cwd if it doesn't exist
        if not self.remote_shell_exec(commands='', is_log=False):
            self.remote_mkdir(self.local_cwd, cwd='~', description='create remote cwd')

    def remote_shell_exec(self, commands: str, description: str, cwd: str = None, is_log: bool = True):
        if cwd is None:
            cwd = self.remote_cwd

        stdin, stdout, stderr = self.ssh.exec_command(f'cd "{cwd}"; ' + commands)
        exit_status = stdout.channel.recv_exit_status()

        if is_log:
            self.write_log(exit_status, description)

        return exit_status
    
    def local_shell_exec(self, commands: str, description: str, cwd: str = None, is_log: bool = True):
        if cwd is None:
            cwd = self.local_cwd

        result = subprocess.run(commands, shell=True, cwd=cwd)
        exit_status = result.returncode

        if is_log:
            self.write_log(exit_status, description)

        return exit_status

    def remote_mkdir(self, folder: str, cwd: str = None, description: str = 'create remote folder'):
        self.remote_shell_exec(
            f'mkdir "{folder}"',
            description=description,
            cwd=cwd,
            )

    def local_mkdir(self, folder: str, cwd: str, description: str = 'create remote folder'):
        self.local_shell_exec(
            f'mkdir "{folder}"',
            description=description,
            cwd=cwd,
            )

    def put_file(self, local_file_path: str, remote_file_folder: str, description: str = 'put file to remote folder'):
        self.local_shell_exec(
            f'scp "{self.dat_file}" "{self.user}@{self.host}:{self.remote_dat_folder}"', 
            description=description,
            )

    def get_file(self):
        pass

    def write_log(self, exit_status: int, description: str):
        current_time = time.strftime("%H:%M:%S")

        if exit_status == 0:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[32m{current_time} > successful > {description}\033[0m')
        else:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[31m{current_time} > failed > {description}\033[0m')


class HostSession_FE(HostSession):
    def __init__(self, addr: str, user: str, marc_bat_path: str, local_dat_folder: str, remote_dat_folder: str, dat_file: str):
        super().__init__(addr, user)
        self.marc_bat_path = marc_bat_path
        self.local_dat_folder = local_dat_folder
        self.remote_dat_folder = remote_dat_folder
        self.dat_file = dat_file

    def workflow(self, back: str = 'yes', nps: int = 4, nts: int = 3, nte: int = 3, nsolver: int = 6):
        pass