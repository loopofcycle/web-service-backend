# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import asyncio
import time
import json
import io
import locale

from service.file_utils import FileUtils
from service.ps_utils import ProcessUtils
from service.base import NameSpaceConfig, ProcessStatus


class RevitRunner(NameSpaceConfig):
    """Class for running Revit.exe application

    Args:
        runner_config (dict): configuration for runner
        revit_config (dict): configuration for Revit app
    """

    def __init__(self, runner_config: dict, revit_config: dict):

        self.setup_config_from_dict(runner_config)
        self.revit_config = revit_config
        self.command = "C:\Program Files\Autodesk\Revit 2024\Revit.exe /language RUS"
        self.command += f" /config {self.config.revit_config_path}"
        self.process = None
        self.proc_status = ProcessStatus.ONGOING
        self.return_code = None
        self.log("initiated")

    async def run_process(self) -> dict:
        # get path to file
        file_path = self.revit_config["TargetFilePath"]
        _, file_name = os.path.split(file_path)
        self.log(f'running export with "{file_name}"')

        # check if file exists
        if not os.path.isfile(file_path):
            return {
                "revit_result": None,
                "process_result": "file not found",
                "revit_app": self.revit_config["StartupApp"],
            }

        # set up revit app config
        self.log(f"set revit config {self.config.revit_config_path}:")
        with open(self.config.revit_config_path, "w", encoding="utf-8") as json_file:
            json.dump(self.revit_config, json_file, ensure_ascii=False, indent=4)

        # spawn process with cmd
        self.process = subprocess.Popen(
            self.command,
            start_new_session=True,
            stdout=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.log(f"starting cmd={self.command!r}, pid={self.process.pid}")

        # waiting for process and reading it's stdout
        await self.wait_for_process()

        # returning result
        return {
            "revit_result": self.log_message,
            "process_result": self.proc_status.value,
            "revit_app": self.revit_config["StartupApp"],
        }

    async def wait_for_process(self) -> str:

        async def coro_read_stdout() -> str:
            messages = {
                "[app_stoped]": ProcessStatus.FINISHED,
                "[app_finished]": ProcessStatus.FINISHED,
                "[failed_to_load_LIB_file]": ProcessStatus.FAILED,
                "[LIB_file_not_found]": ProcessStatus.FAILED,
                "[unsuccessful_upload_of_links]": ProcessStatus.FAILED,
                "[unexpected_dialogue]": ProcessStatus.FAILED,
                "[failed_to_open_file]": ProcessStatus.FAILED,
                "[pdf_creation_finished]": ProcessStatus.FINISHED,
                "[failed_to_open:wrong_user_exception]": ProcessStatus.FAILED,
            }

            # check for a reasons to stop the app
            self.log(f"waiting for app: [pid={self.process.pid}]")

            # reading process output
            preferred_encoding = locale.getpreferredencoding(False)
            for line in io.TextIOWrapper(
                self.process.stdout, encoding=preferred_encoding
            ):

                self.return_code = self.process.poll()
                if self.return_code is not None:
                    self.proc_status = ProcessStatus.FAILED
                    self.log_message = (
                        f"process was shut down, returncode {hex(self.return_code)}"
                    )
                    self.log(
                        f"msg: {self.log_message}, status: {self.proc_status}, code {hex(self.return_code)}"
                    )

                output = line.strip()
                self.log(f"[pid={self.process.pid}]: {output}")
                result_message = [msg for msg in messages if msg in output]
                if result_message:
                    self.log_message = output
                    self.proc_status = messages[result_message.pop()]

                if self.proc_status in [ProcessStatus.FINISHED, ProcessStatus.FAILED]:
                    break

            self.log("witing 10 sec to finish")
            await asyncio.sleep(10)
            self.return_code = self.process.poll()
            self.log(
                f"msg: {self.log_message}, result: {self.proc_status}, code{self.return_code}"
            )
            return self.log_message

        # waiting for process
        try:
            await asyncio.wait_for(coro_read_stdout(), timeout=self.config.timeout)

            if self.process.poll() is None:
                self.log(f"[pid={self.process.pid}] terminating ...")
                os.kill(self.process.pid, signal.SIGTERM)
                self.log(f"[pid={self.process.pid}] terminated: {self.log_message}")

        except asyncio.TimeoutError:
            self.log_message = f"exterminated due to timeout"

            if self.return_code is None:
                os.kill(self.process.pid, signal.SIGTERM)

            self.proc_status = ProcessStatus.FAILED
            self.log(f"process pid={self.process.pid} was terminated due to timeout")

        # wait for process to be done with file and move it
        await asyncio.sleep(5)
        return self.log_message

