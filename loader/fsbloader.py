import requests
from urllib3 import disable_warnings
from urllib.parse import urlparse
from typing import List
import os
import shutil
from pathlib import Path
from datetime import (
    datetime,
    timedelta,
)
from utils.logger import tglogger as logger
from utils.logger import log_obj
from utils.drwlinuxpacker import DRWLinuxPacker

exec_command = DRWLinuxPacker.exec_command


class FSBLoader:
    @log_obj
    def __init__(
        self,
        url_list_for_load: List[str],
        user: str,
        password: str,
        path_to_bases: Path = Path(os.getcwd()) / "bases",
    ):
        disable_warnings()
        self.session = requests.Session()
        self.url_list = url_list_for_load
        self.path_to_bases = path_to_bases
        for download_url in self.url_list:
            if self.login(user, password, download_url):
                logger.success(f"Login on {download_url} successfull")
                self.file_list: List[Path] = self.load_bases()
                self.make_finally_zip_archive()
            else:
                logger.error(f"Some error when login in {download_url}")

    def login(self, user: str, password: str, url: str):
        url = self.get_base_login_url(url)
        login_response = self.session.get(url, auth=(user, password), verify=False)
        if login_response.status_code == 200:
            return True
        return False

    def load_bases(self) -> List[Path]:
        return [
            (Path(self.path_to_bases.parent) / os.path.basename(url))
            for url in self.url_list
            if self.download(url)
        ]

    def get_base_login_url(self, url: str) -> str:
        url_parse = urlparse(url)
        return url.replace(url_parse.path, "")

    def download(self, url: str):
        try:
            logger.info(f"Start to download {url}")
            with self.session.get(
                url, headers={"Range": "bytes=0-"}, stream=True, verify=False
            ) as file_pesponce:
                file_pesponce.raise_for_status()
                with open(f"{os.path.basename(url)}", "wb") as file:
                    shutil.copyfileobj(file_pesponce.raw, file)
        except requests.exceptions.HTTPError as error:
            logger.error(f"Error when load {url}:{error}")
        else:
            logger.success(f"File {os.path.basename(url)} successfull load")
            return True
        return False

    def make_finally_zip_archive(self) -> bool:
        logger.info(f"Start to make archive FSB.zip")
        zip_command = f"zip -r FSB.zip {self.file_list_string} && "
        mv_command = f"mv FSB.zip {self.path_to_bases}/ && "
        rm_command = f"rm {self.file_list_string}"
        return exec_command(command=(zip_command + mv_command + rm_command))

    @property
    def file_list_string(self):
        return " ".join([str(path_to_file.name) for path_to_file in self.file_list])
