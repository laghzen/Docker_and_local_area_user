import docker
import threading
import tarfile
import time
from io import BytesIO


class Timer(threading.Thread):
    def __init__(self, env, file_name, time_slow):
        super().__init__()
        self.time_slow = time_slow
        self.stop_err = False

        self.container = env.container
        self.file_name = file_name

    def stop(self):
        self.stop_err = True

    def run(self):
        start = time.time()
        while time.time() - start < self.time_slow:
            if self.stop_err: break
        if not self.stop_err:
            self.container.exec_run(f'pkill -9 -f {self.file_name}', demux=True)
            print("Скрипт слишком медленный!")
        else:
            print('Все ок!')


def import_to_container(container, file_in_host, path_in_container, name_file_in_container):
    with open(file_in_host) as file_user:
        src_code = file_user.read()

    pw_tarstream = BytesIO()

    with tarfile.TarFile(fileobj=pw_tarstream, mode='w') as pw_tar:
        file_data = src_code.encode('utf8')

        tarinfo = tarfile.TarInfo(name=name_file_in_container)
        tarinfo.size = len(file_data)
        tarinfo.mtime = time.time()

        pw_tar.addfile(tarinfo, BytesIO(file_data))

    pw_tarstream.seek(0)

    print('Complete load:', container.put_archive(path_in_container, pw_tarstream))


def export_from_container(container, file_in_container, path_in_host, name_file_in_host):
    data, tarinfo = container.get_archive(file_in_container)

    pw_tarstream = BytesIO(b''.join(i for i in data))

    with tarfile.TarFile(fileobj=pw_tarstream, mode='r') as pw_tar:
        file_name = pw_tar.getmembers()[0].name
        file_data_bytes = pw_tar.extractfile(file_name)
        file_data = file_data_bytes.read().decode('utf-8')

    if name_file_in_host is None: name_file_in_host = file_name
    with open(f'{path_in_host}{name_file_in_host}', 'w') as file_user:
        file_user.write(file_data)


class StartContainer:
    def __init__(self, mode_get, name, image='base_sandbox'):
        self.client = docker.from_env()

        self.timer = Timer
        self.import_to_container = import_to_container
        self.export_from_container = export_from_container

        self.create = lambda name, image: self.client.containers.create(image, name=name, tty=True)
        self.get = lambda name: self.client.containers.get(name)
        self.kill = lambda: self.container.kill()
        self.remove = lambda: self.container.remove(force=True)

        if mode_get == 'create':
            self.container = self.create(name, image)
        elif mode_get == 'get':
            self.container = self.get(name)
        self.container.start()

    def load_file(self, file_in_host, path_in_container, name_file_in_container=None):
        if name_file_in_container is None:
            name_file_in_container = file_in_host

        self.import_to_container(self.container, file_in_host, path_in_container, name_file_in_container)

    def download_file(self, file_in_container, path_in_host, name_file_in_host=None):
        self.export_from_container(self.container, file_in_container, path_in_host, name_file_in_host)

    def exec_command(self, command):
        exit_code, output = self.container.exec_run(command, demux=True)
        self.print_output(exit_code, output)

    def print_output(self, exit_code, output):
        stdout, stderr = [data if data is None else data.decode('UTF-8') for data in output]
        print('exit_code:', exit_code)
        print('Вывод пользователя:\n\t{}'.format(stdout if stdout is None else stdout.replace('\n', '\n\t')))
        print('Ошибки пользователя:\n\t{}'.format(stderr if stderr is None else stderr.replace('\n', '\n\t')))
        return exit_code

    def time_break(func):
        def wrapper(self, *args, **kwargs):
            th = self.timer(self, *args, kwargs.get('time_to_slow', 3))
            th.start()
            result = func(self, *args, **kwargs)
            th.stop()
            return result
        return wrapper

    @time_break
    def run_user_code(self, file_name, **kwargs):
        exit_code, output = self.container.exec_run(f'python {file_name}', demux=True)
        self.print_output(exit_code, output)


team2 = StartContainer('create', 'TEAM2')
team2.exec_command('ls')
team2.remove()
