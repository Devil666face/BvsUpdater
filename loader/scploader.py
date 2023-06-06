import os
import subprocess
import shutil
from loader.smbloader import SMBLoader
from utils.renamer import Renamer
from pathlib import Path
from datetime import datetime
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class SCPLoader(SMBLoader):
    @log_obj
    def __init__(
        self,
        username: str,
        password: str,
        server_ip: str,
        base_name: str = "DRW_ESS6_MSVS",
        path_to_source: str = "repository",
        path_to_bases_dir: str = "/var/opt/drwcs/repository/10-drwbases",
        base_dir: Path = Path(os.getcwd()) / "repository" / "10-drwbases",
        date_tag: str = datetime.now(),
        IGNORE_DATE: bool = False,
    ):
        date_tag = datetime.now()
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.base_name = base_name
        self.path_to_bases_dir = path_to_bases_dir
        self.path_to_source = path_to_source
        self.base_dir = base_dir
        self.date_tag = Renamer.strfdate(date_tag)
        os.makedirs(self.base_dir)
        logger.info(f"Start to load {base_name}")
        if self.load_base():
            logger.success(f"Successfull load {base_name}")
        else:
            logger.warning(f"Error when load {base_name}")
        if self.validation_date_base() or IGNORE_DATE:
            logger.success(f"Date for bases of {self.base_name} is actual")
            self.make_finally_zip_archive(zip_name=base_name)

        self.umount_dir()
        shutil.rmtree(self.base_dir.parent)

    def load_base(self) -> bool:
        return exec_command(self.scp_command)

    def umount_dir(self) -> bool:
        return exec_command(self.umount_command)

    def validation_date_base(self) -> bool:
        result = subprocess.run(
            self.date_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
        date_from_base = result.stdout
        if self.date_tag.strip() == date_from_base.strip():
            return True
        logger.warning(
            f"Date of {self.base_name}={date_from_base.strip()} is now now date {self.date_tag}"
        )
        return False

    @property
    def date_command(self):
        return f"date +%Y%m%d -d @`cat {self.base_dir /'.id'}`"

    @property
    def umount_command(self):
        return f"umount {self.base_dir}"

    @property
    def scp_command(self):
        return f"echo '{self.password}' | sshfs {self.base_dir} {self.username}@{self.server_ip}:{self.path_to_bases_dir} -o password_stdin"
