# -*- coding: utf-8 -*-
import os
import errno
import re
import shutil
from datetime import datetime
from pathlib import Path

# Revit autosave backups: name.0001.rvt / name.0002.rfa / name.1234.rfa
_REVIT_BACKUP_RE = re.compile(r'\.\d{4}\.(rvt|rfa)$', re.IGNORECASE)


class FileUtils:

    def __init__(self):
        pass

    @classmethod
    def is_revit_backup(cls, file_name: str) -> bool:
        """True for Revit backup copies like *.0001.rvt / *.0002.rfa."""
        return bool(_REVIT_BACKUP_RE.search(os.path.basename(file_name)))

    @classmethod
    def find_files(cls, path, extension='.rvt', as_dicts=False) -> list:
        files = []
        for file in os.listdir(path):

            fullpath = os.path.join(path, file)
            if not os.path.isfile(fullpath):
                continue

            if extension not in file:
                continue

            if cls.is_revit_backup(file):
                continue

            if as_dicts:
                files.append({'file': file.removesuffix('.rvt'),
                              'datetime': datetime.fromtimestamp(os.path.getmtime(fullpath))})
            else:
                files.append(os.path.join(path, file))

        return files

    @classmethod
    def move_file(cls, file_name, src, dst):
        if os.path.isdir(dst):
            shutil.move(src=str(os.path.join(src, file_name)),
                        dst=str(os.path.join(dst, file_name)))
            print(f'[{__name__}]: moved file {file_name} to folder: {dst}')

    @classmethod
    def silent_remove(cls, file_path):
        try:
            print(f'[{__name__}]: deleting file {file_path}')
            os.remove(file_path)
        except OSError as e:  # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occurred

    @classmethod
    def delete_files(cls, dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    @classmethod
    def clean_revit_backups(cls, directory_path):
        path = Path(directory_path)
        if not path.exists():
            print(f'[{__name__}]: storage path does not exist: {path}')
            return

        print(path)
        for file in path.rglob('*'):
            if not file.is_file():
                continue
            if not cls.is_revit_backup(file.name):
                continue
            print(file)
            try:
                file.unlink()
            except Exception:
                pass


if __name__ == '__main__':
    FileUtils.clean_revit_backups(os.environ.get(
        'SERVER_STORAGE_PATH',
        r'C:\Users\loopo\YandexDisk\_revit_library',
    ))
