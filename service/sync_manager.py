import os
from enum import Enum
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from app.core.config import settings
from app.db.models import *
from adapters.vitro_client import VitroClient
from service.file_utils import FileUtils as fu
from service.base import NameSpaceConfig
from service.revit_file_name import RevitFileName


class FileStatus(Enum):
    PENDING = 'pending'
    MISSING = 'missing'
    UPDATED = 'updated'


class SyncManager(NameSpaceConfig):
    db_df: DataFrame
    pdm_df: DataFrame
    new_files_df: DataFrame
    subparts: list
    stages: list

    def __init__(self, config_path: str, run_pdm=True):
        self.setup_config_from_json(config_path)

        _subparts = {}
        for s in self.config.apps:
            _subparts.update(dict.fromkeys(s.subparts))
        self.subparts = list(_subparts)

        _stages = {}
        for s in self.config.apps:
            _stages.update(dict.fromkeys(s.stages))
        self.stages = list(_stages)

        self.log(f'collecting files from pdm {self.subparts}, {self.stages}')

        if run_pdm:
            self.pdm_client = VitroClient(
                credentials={'pdm_login': self.config.pdm_login,
                             'pdm_password': self.config.pdm_password},
                urls={'pdm_get_list_url': self.config.pdm_get_list_url,
                      'pdm_get_file_url': self.config.pdm_get_file_url},
                period=self.config.pdm_period_years)
            self.pdm_client.filter_pdm_files(
                projects=list(vars(self.config.projects_names).keys()),
                subparts=self.subparts,
                stages=self.stages)
            self.pdm_df = self.pdm_client.get_actual_df()

    def find_new_files_in_pdm(self):
        def compare_files_df(pdm_df: pd.DataFrame, db_df: pd.DataFrame) -> pd.DataFrame:
            self.log(f'pdm files {pdm_df.shape[0]}, db files {db_df.shape[0]}')

            result_df = pd.DataFrame()
            for f_name in pdm_df['file'].values:
                status = FileStatus.PENDING

                # skip if name is incorrect, for purpose of changing it in pdm
                file_name = RevitFileName(f_name)
                if file_name.incorrect:
                    self.log(f'incorrect file name {f_name}, skipping')
                    continue

                # define if file needed to be uploaded
                correct_name = f"{file_name.title}.rvt"
                if correct_name in db_df['file'].values:
                    pdm_dt = pdm_df[pdm_df.file ==
                                    correct_name]['datetime'].item()
                    db_dt = db_df[db_df.file ==
                                  correct_name]['datetime'].item()
                    if pdm_dt > db_dt:
                        status = FileStatus.UPDATED
                        # self.log(f'"{f_name}" {status.value} pdm: {pdm_dt} vs db: {db_dt}')

                else:
                    status = FileStatus.MISSING
                    # self.log(f'"{f_name}" {status.value}')

                if status == FileStatus.MISSING or status == FileStatus.UPDATED:
                    if correct_name != f_name:
                        self.log(
                            f'pdm file:"{f_name}" is not correct name: "{correct_name}"')

                    _id = pdm_df.loc[pdm_df.file == f_name, 'id'].item()
                    _dt = pdm_df.loc[pdm_df.file == f_name, 'datetime'].item()
                    file_df = pd.DataFrame([{'file': correct_name,
                                             'datetime': _dt,
                                             'id': _id,
                                             'status': status.value}])
                    result_df = pd.concat(
                        [result_df, file_df], ignore_index=True)

            self.log(f'pdm have {result_df.shape[0]} new (or updated) files')
            return result_df

        self.new_files_df = compare_files_df(
            pdm_df=self.pdm_df, db_df=self.db_df)

    async def download_file_from_pdm(self, file_name, path: str = None) -> tuple[str, str]:

        if self.pdm_df.empty:
            msg = 'no files in pdm'
            self.log(msg)
            return ("", msg)

        if file_name not in self.pdm_df['file'].values:
            msg = 'file not in pdm'
            self.log(msg)
            return ("", msg)

        save_to_path = path if path is not None else settings.BUFFER_FOLDER
        file_df = self.pdm_df.loc[self.pdm_df['file'] == file_name]
        file_id = file_df['id'].values[0]
        self.log(f'preparing download')

        is_downloaded = await self.pdm_client.download_file(
            file_id=file_id,
            file_name=file_name,
            save_to_path=save_to_path
        )

        msg = 'file was not downloaded' if is_downloaded else None

        return (os.path.join(save_to_path, file_name), msg)

    def define_revit_apps(self, file_name: str) -> list:
        _apps = []

        parsed_name = RevitFileName(file_name)
        for rvt_app in self.config.apps:
            if not any([sp in parsed_name.subpart for sp in rvt_app.subparts]):
                continue

            if not any([st in parsed_name.stage for st in rvt_app.stages]):
                continue

            _apps.append(rvt_app.startup_app)

        return _apps

    def define_revit_config(self, startup_app: str):
        for rvt_app in self.config.apps:
            if startup_app == rvt_app.startup_app:
                result_path = rvt_app.config_path

        return result_path
