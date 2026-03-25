# -*- coding: utf-8 -*-
import os
import errno
import shutil
from datetime import datetime
from pathlib import Path


class FileUtils:

    def __init__(self):
        pass

    @classmethod
    def find_files(cls, path, extension='.rvt', as_dicts=False) -> list:
        files = []
        for file in os.listdir(path):

            fullpath = os.path.join(path, file)
            if not os.path.isfile(fullpath):
                continue

            if extension not in file:
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
        print(path)
        
        # Ищем файлы, которые заканчиваются на .####.rvt (4 цифры)
        # rglob делает поиск рекурсивным (включая подпапки)
        for file in path.rglob("*.00[0-9][0-9].rfa"):
            print(file)
            try:
                file.unlink() # Удаление файла
                # print(f"Удален: {file.name}") # Раскомментируйте для логов
            except Exception:
                pass # Игнорируем ошибки (например, файл занят Revit)

if __name__ == '__main__':
    from pprint import pprint
    _path = r'C:\Users\Eliseev.I\PycharmProjects\revit-specifications-export\buffer\excel_files'
    # excel_files = FileUtils.find_files(_path, extension='.xlsx', as_dicts=True)
    # corresponding_revit_files = [
    #     {'file': note['file'].replace(
    #         '.xlsx', '.rvt'), 'datetime': note['datetime']}
    #     for note in excel_files
    # ]

    FileUtils.clean_revit_backups(r'C:\Users\eliseev_i\Yandex.Disk\_revit_library')

