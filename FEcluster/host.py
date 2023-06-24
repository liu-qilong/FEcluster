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

        # create local_cwd and remote_cwd if they don't exist
        self.local_mkdir(self.local_cwd, cwd='C:\\')
        self.remote_mkdir(self.remote_cwd, cwd='C:\\')

    def remote_shell_exec(self, commands: str, cwd: str = None, description: str = "execute remote commands", is_log: bool = True):
        if cwd is None:
            cwd = self.remote_cwd

        stdin, stdout, stderr = self.ssh.exec_command(f'cd "{cwd}"; ' + commands)
        exit_status = stdout.channel.recv_exit_status()

        if is_log:
            self.write_log(exit_status, description)

        return exit_status
    
    def local_shell_exec(self, commands: str, cwd: str = None, description: str = "execute local commands", is_log: bool = True):
        if cwd is None:
            cwd = self.local_cwd

        result = subprocess.run(commands, shell=True, cwd=cwd)
        exit_status = result.returncode

        if is_log:
            self.write_log(exit_status, description)

        return exit_status

    def remote_mkdir(self, folder: str, cwd: str = None):
        if self.remote_shell_exec(commands=f'cd {folder}', cwd=cwd, is_log=False) == 0:
            self.write_log(0, f'remote folder "{folder}" already exists')

        else:
            self.remote_shell_exec(
                f'mkdir "{folder}"',
                description = f'create remote folder "{folder}"',
                cwd = cwd,
                )

    def local_mkdir(self, folder: str, cwd: str = None):
        if self.local_shell_exec(commands=f'cd {folder}', cwd=cwd, is_log=False) == 0:
            self.write_log(0, f'local folder "{folder}" already exists')
            
        else:
            self.local_shell_exec(
                f'mkdir "{folder}"',
                description = f'create remote folder "{folder}"',
                cwd=cwd,
                )

    def put_file(self, local_file_path: str, remote_file_folder: str, cwd: str = None, description: str = 'put file to remote folder'):
        self.local_shell_exec(
            f'scp "{local_file_path}" "{self.user}@{self.host}:{remote_file_folder}"', 
            description=description,
            cwd=cwd,
            )

    def put_file(self, remote_file_path: str, local_file_folder: str, cwd: str = None, description: str = 'get file from remote folder'):
        self.local_shell_exec(
            f'scp "{self.user}@{self.host}:{remote_file_path}" "{local_file_folder}" ', 
            description=description,
            cwd=cwd,
            )

    def write_log(self, exit_status: int, description: str):
        current_time = time.strftime("%H:%M:%S")

        if exit_status == 0:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[32m{current_time} > successful > {description}\033[0m')
        else:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[31m{current_time} > failed > {description}\033[0m')