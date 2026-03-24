
import logging
from types import SimpleNamespace
from enum import Enum
import json


class ProcessStatus(Enum):
    WAITING = 'waiting'
    ONGOING = 'ongoing'
    FAILED = 'failed'
    FINISHED = 'finished'


class NameSpaceConfig:
    proc_status: ProcessStatus
    command = None
    config = None
    log_message = None

    def __init__(self):
        pass

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format="{levelname}:{asctime}:{message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S")

    def setup_config_from_json(self, config_path):
        self.setup_logger()
        with open(file=config_path, encoding='utf-8') as f:
            self.config = json.load(
                f, object_hook=lambda d: SimpleNamespace(**d))
            self.log(f'received config from json {config_path}')

    def setup_config_from_dict(self, config_dict):
        self.setup_logger()
        self.config = SimpleNamespace(config_dict)
        self.log(f'received config from dict {config_dict}')

    def log(self, msg):
        logging.info(f'{__name__}:{msg}')


if __name__ == "__main__":
    from pprint import pprint
    _path = r"C:\Users\Eliseev.I\projects\revit_manager_app\backend\service\configs\dev_config.json"
    nsc = NameSpaceConfig()
    nsc.setup_config_from_json(_path)
    pprint(nsc.config)

    _subparts = {}
    for s in nsc.config.apps:
        _subparts.update(dict.fromkeys(s.subparts))
    subparts = list(_subparts)
    print(subparts)
