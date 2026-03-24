import psutil
from pprint import pprint


class ProcessUtils:

    processes = {}

    @classmethod
    def get_process_info(cls, pid=None):
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # Access process details as a dictionary
                info = proc.as_dict(attrs=['pid', 'name'])
                cls.processes[info['pid']] = info['name']

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Handle exceptions for processes that may have terminated or are inaccessible
                pass

        return cls.processes[pid] if pid else cls.processes
