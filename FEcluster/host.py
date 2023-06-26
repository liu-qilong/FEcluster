import os
import time
import paramiko
import subprocess

class HostSession:
    def __init__(self, addr: str, user: str, pwd: str, local_cwd: str, remote_cwd: str, session_name: str = None):
        self.session_name = session_name
        self.addr = addr
        self.user = user
        self.pwd = pwd
        self.local_cwd = local_cwd
        self.remote_cwd = remote_cwd

        # init ssh connection
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.addr, username=self.user, password=self.pwd)

        # create local_cwd and remote_cwd if they don't exist
        self.local_mkdir(self.local_cwd, cwd='C:\\')
        self.remote_mkdir(self.remote_cwd, cwd='C:\\')

    def remote_shell_exec(self, commands: str, cwd: str = None, description: str = "execute remote commands", is_log: bool = True, **kwargs):
        if cwd is None:
            cwd = self.remote_cwd

        _, stdout, stderr = self.ssh.exec_command(f'cd "{cwd}"; ' + commands)
        exit_status = stdout.channel.recv_exit_status()

        def parse_io(io):
            io_ls = io.readlines()
            return "".join(io_ls)

        return_dict = {
            'exit': exit_status,
            'stdout': parse_io(stdout),
            'stderr': parse_io(stderr)
        }

        if is_log:
            self.write_log(return_dict, description, **kwargs)

        return return_dict
    
    def local_shell_exec(self, commands: str, cwd: str = None, description: str = "execute local commands", is_log: bool = True, **kwargs):
        if cwd is None:
            cwd = self.local_cwd

        result = subprocess.run(commands, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_status = result.returncode

        return_dict = {
            'exit': exit_status,
            'stdout': result.stdout.decode(),
            'stderr': result.stderr.decode(),
        }

        if is_log:
            self.write_log(return_dict, description, **kwargs)

        return return_dict

    def remote_mkdir(self, folder: str, cwd: str = None, **kwargs):
        if self.remote_shell_exec(commands=f'cd {folder}', cwd=cwd, is_log=False)['exit'] == 0:
            self.write_log({'exit': 0}, f'remote folder "{folder}" already exists')

        else:
            self.remote_shell_exec(
                f'mkdir "{folder}"',
                description = f'create remote folder "{folder}"',
                cwd = cwd,
                **kwargs,
                )

    def local_mkdir(self, folder: str, cwd: str = None, **kwargs):
        if self.local_shell_exec(commands=f'cd {folder}', cwd=cwd, is_log=False)['exit'] == 0:
            self.write_log({'exit': 0}, f'local folder "{folder}" already exists')
            
        else:
            self.local_shell_exec(
                f'mkdir "{folder}"',
                description = f'create local folder "{folder}"',
                cwd = cwd,
                **kwargs,
                )

    def put_file(self, local_file_path: str, remote_file_folder: str, **kwargs):
        self.remote_mkdir(remote_file_folder)
        description = f'put file "{local_file_path}" to remote folder "{remote_file_folder}"'

        try:
            file_name = os.path.split(local_file_path)[-1]
            scp = self.ssh.open_sftp()
            scp.put(
                os.path.join(self.local_cwd, local_file_path),
                os.path.join(self.remote_cwd, remote_file_folder, file_name)
            )
            self.write_log({'exit': 0}, description, **kwargs)

        except:
            self.write_log({'exit': 1}, description, **kwargs)

    def get_file(self, remote_file_path: str, local_file_folder: str, **kwargs):
        self.local_mkdir(local_file_folder)
        description = f'get file "{remote_file_path}" to local folder "{local_file_folder}"'

        try:
            file_name = os.path.split(remote_file_path)[-1]
            scp = self.ssh.open_sftp()
            scp.get(
                os.path.join(self.remote_cwd, remote_file_path),
                os.path.join(self.local_cwd, local_file_folder, file_name)
            )
            self.write_log({'exit': 0}, description, **kwargs)

        except:
            self.write_log({'exit': 1}, description, **kwargs)

    def write_log(self, exec_return_dict: dict, description: str, print_stdout: bool = False, print_stderr: bool = False):
        current_time = time.strftime("%H:%M:%S")

        if exec_return_dict['exit'] == 0:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[32m{current_time} > successful > {description}\033[0m')

        else:
            print(f'{self.user}@{self.addr}:{self.session_name}\n\033[31m{current_time} > failed > {description}\033[0m')

        if print_stdout:
            print(exec_return_dict['stdout'])

        if print_stderr:
            print(exec_return_dict['stderr'])