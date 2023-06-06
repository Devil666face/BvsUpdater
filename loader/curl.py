import shutil
import os
from pathlib import Path
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class Curl:
    @log_obj
    def __init__(
        self,
        url: str,
        path_to_bases: Path = Path(os.getcwd()) / "bases",
    ):
        self.url = url
        self.path_to_bases = path_to_bases
        self.file_name = os.path.basename(self.url)
        self.path_to_file = self.path_to_bases.parent / self.file_name
        if self.load():
            logger.success(f"Successfull load {self.file_name}")
            self.move()
        else:
            logger.error(f"{self.file_name} not load")

    def load(self) -> bool:
        curl_command = f"curl -sO {self.url}"
        logger.info(f"Start load {self.file_name} {curl_command}")
        return exec_command(command=curl_command)

    def move(self):
        shutil.move(str(self.path_to_file), str(self.path_to_bases))
