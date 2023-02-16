import os
from datetime import datetime
from typing import List
from utils.renamer import Renamer
from utils.drwlinuxpacker import DRWLinuxPacker
from pathlib import Path
from utils.logger import (
    logger,
    log_obj,
)

exec_command = DRWLinuxPacker.exec_command


class TotalArchive:
    """Создает общий архив для всех файлов в bases,
    переименовывает папку bases в 20230101(текущую дату), если она
    не передана явно в том случае если TotalArchive(date_tag='20230101')
    переименую в указанную"""

    @log_obj
    def __init__(
        self,
        date_tag: str = datetime.now(),
        path_to_bases_folder: Path = (Path(os.getcwd()) / "bases"),
    ):
        self.date = Renamer.strfdate(date_tag)
        self.path_to_bases_folder = path_to_bases_folder
        self.file_list: List[str] = self.get_all_files_in_folder(
            folder=path_to_bases_folder
        )
        if self.make_finally_zip_archive():
            logger.success(f"Total zip archive make successfull")
            self.rename_base_dir()
        else:
            logger.error(f"Error for make total archive")

    def get_all_files_in_folder(self, folder: Path) -> List[str]:
        """Возвращает все абсолютные пути до .zip в текущей папке"""
        return [str(file) for file in os.listdir(folder)]

    def make_finally_zip_archive(self) -> bool:
        logger.info(f"Start to make total archive updates_{self.date}.zip")
        cd_command = f"cd {self.path_to_bases_folder} && "
        zip_command = f"zip -r updates_{self.date}.zip {self.file_list_string}"
        return exec_command(command=(cd_command + zip_command))

    def rename_base_dir(self) -> bool:
        new_name = self.path_to_bases_folder.parent / f"{self.date}"
        os.rename(self.path_to_bases_folder, new_name)

    @property
    def file_list_string(self) -> str:
        return " ".join(self.file_list)
