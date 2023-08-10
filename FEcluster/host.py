import os
import time
import paramiko
import subprocess

class HostSession:
    def __init__(self, host_info: dict, host_name: str = 'host'):
        self.host_info = host_info
        self.host_name = host_name

    def setup(self, local_cwd: str, remote_cwd: str, session_name: str = 'session'):
        self.session_name = session_name
        self.local_cwd = local_cwd
        self.remote_cwd = remote_cwd
        self.log_path = os.path.join(self.local_cwd, "log.txt")
        
        # init ssh connection
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.host_info['addr'], username=self.host_info['user'], password=self.host_info['pwd'])

        # create local_cwd and remote_cwd if they don't exist
        self.local_mkdir(self.local_cwd, cwd='D:\\')
        self.remote_mkdir(self.remote_cwd, cwd='D:\\')
        
        # create log file
        with open(self.log_path, "w") as file:
            file.write(f"{self.host_info['user']}@{self.host_info['addr']}:{self.session_name}\n")
            file.write(f"local path: {self.local_cwd}\n")
            file.write(f"remote path: {self.remote_cwd}\n")
            file.write("-" * 50 + "\n")
        
        self.write_log({'exit': 0}, 'setup host session')

    def remote_shell_exec(self, commands: str, cwd: str = None, description: str = "execute remote commands", **kwargs) -> dict:
        if cwd is None:
            cwd = self.remote_cwd

        try:
            _, stdout, stderr = self.ssh.exec_command(f'cd "{cwd}"; ' + commands)
            exit_status = stdout.channel.recv_exit_status()

            def parse_io(io):
                io_ls = io.readlines()
                return "".join(io_ls)

            return_dict = {
                'exit': exit_status,
                'stdout': parse_io(stdout),
                'stderr': parse_io(stderr),
            }
        
        except:
            return_dict = {
                'exit': 1,
                'stdout': '',
                'stderr': '',
            }

        self.write_log(return_dict, description, **kwargs)

        return return_dict
    
    def local_shell_exec(self, commands: str, cwd: str = None, description: str = "execute local commands", **kwargs) -> dict:
        if cwd is None:
            cwd = self.local_cwd

        try:
            result = subprocess.run(commands, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_status = result.returncode

            return_dict = {
                'exit': exit_status,
                'stdout': result.stdout.decode(),
                'stderr': result.stderr.decode(),
            }

        except:
            return_dict = {
                'exit': 1,
                'stdout': '',
                'stderr': '',
            }

        self.write_log(return_dict, description, **kwargs)

        return return_dict

    def remote_mkdir(self, folder: str, cwd: str = None, **kwargs) -> dict:
        return_dict = self.remote_shell_exec(commands=f'cd "{folder}"', cwd=cwd, print_log=False)

        if return_dict['exit'] == 0:
            self.write_log(return_dict, f'remote folder "{folder}" already exists', **kwargs)

        else:
            return_dict = self.remote_shell_exec(
                f'mkdir "{folder}"',
                description = f'create remote folder "{folder}"',
                cwd = cwd,
                **kwargs,
                )
            
        return return_dict

    def local_mkdir(self, folder: str, cwd: str = None, **kwargs) -> dict:
        return_dict = self.local_shell_exec(commands=f'cd "{folder}"', cwd=cwd, print_log=False)

        if return_dict['exit'] == 0:
            self.write_log(return_dict, f'local folder "{folder}" already exists', **kwargs)
            
        else:
            return_dict = self.local_shell_exec(
                f'mkdir "{folder}"',
                description = f'create local folder "{folder}"',
                cwd = cwd,
                **kwargs,
                )
            
        return return_dict

    def put_file(self, local_file_path: str, remote_file_folder: str = './', **kwargs) -> dict:
        self.remote_mkdir(remote_file_folder, print_log=False)
        description = f'put file "{local_file_path}" to remote folder "{remote_file_folder}"'

        try:
            file_name = os.path.split(local_file_path)[-1]
            scp = self.ssh.open_sftp()
            scp.put(
                os.path.join(self.local_cwd, local_file_path),
                os.path.join(self.remote_cwd, remote_file_folder, file_name)
            )

            return_dict = {'exit': 0, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        except:
            return_dict = {'exit': 1, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        return return_dict

    def get_file(self, remote_file_path: str, local_file_folder: str = './', **kwargs) -> dict:
        self.local_mkdir(local_file_folder, print_log=False)
        description = f'get file "{remote_file_path}" to local folder "{local_file_folder}"'

        try:
            file_name = os.path.split(remote_file_path)[-1]
            scp = self.ssh.open_sftp()
            scp.get(
                os.path.join(self.remote_cwd, remote_file_path),
                os.path.join(self.local_cwd, local_file_folder, file_name)
            )
            return_dict = {'exit': 0, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        except:
            return_dict = {'exit': 1, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        return return_dict

    def get_all_files(self, remote_file_folder: str = './', local_file_folder: str = './', filter: str = '', **kwargs) -> dict:
        self.local_mkdir(local_file_folder, print_log=False)
        description = f'get all files from "{remote_file_folder}" to local folder "{local_file_folder}"'

        try:
            scp = self.ssh.open_sftp()
            files = scp.listdir(os.path.join(self.remote_cwd, remote_file_folder))
            
            for file in files:
                if filter in file:
                    self.get_file(
                        os.path.join(remote_file_folder, file),
                        local_file_folder,
                        )
            
            return_dict = {'exit': 0, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        except:
            return_dict = {'exit': 1, 'std_out': '', 'std_err': ''}
            self.write_log(return_dict, description, **kwargs)

        return return_dict

    def write_log(self, exec_return_dict: dict, description: str, print_log: bool = True, print_stdout: bool = False, print_stderr: bool = False):
        # print and write log
        if print_log:
            current_time = time.strftime("%H:%M:%S")
            host_str = f"{self.host_info['user']}@{self.host_info['addr']}:{self.session_name}"

            if exec_return_dict['exit'] == 0:
                log_str = f'{current_time} > successful > {description}'
                print(f'{host_str}\n\033[32m{log_str}\033[0m')

            else:
                log_str = f'{current_time} > failed > {description}'
                print(f'{host_str}\n\033[31m{log_str}\033[0m')

            with open(self.log_path, "a") as file:
                file.write(log_str + '\n')

        # print and write stdout
        if print_stdout:
            print(exec_return_dict['stdout'])

            with open(self.log_path, "a") as file:
                file.write('\n' + exec_return_dict['stdout'] + '\n')

        # print and write stderr
        if print_stderr:
            print(exec_return_dict['stderr'])

            with open(self.log_path, "a") as file:
                file.write('\n' + exec_return_dict['stderr'] + '\n')