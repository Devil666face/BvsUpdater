import os
import glob
import shutil
from datetime import datetime
from pathlib import Path
from typing import (
    List,
    Tuple,
)
from utils.renamer import Renamer
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class TotalArchive:
    """Создает общий архив для всех файлов в bases,
    переименовывает папку bases в 20230101(текущую дату), если она
    не передана явно в том случае если TotalArchive(date_tag='20230101')
    переименую в указанную"""

    @log_obj
    def __init__(
        self,
        folder_ierarchy=None,
        date_tag=None,
        path_to_bases_folder: Path = (Path(os.getcwd()) / "bases"),
    ):
        if date_tag is None:
            date_tag = datetime.now()
        """Слева - маска для поиска файлов
        Справо - иерархия директорий относительно базовой (./bases)
        более частные правила должны распологаться выше общих
        т.е. weekly выще чем все остальные
        Последние 2 пути необходимы в случае если перемещение просиходит
        для уже созданной иерархии директорий (после переделывания weekly архива)"""
        self.FOLDER_IERARCHY = {
            "DRW*weekly*": ["DrWeb", "weekly"],
            "K*weekly*": ["Kaspersky", "weekly"],
            "DRW*": ["DrWeb", "full"],
            "K*": ["Kaspersky", "full"],
            "*.iso": ["LiveCD"],
            "kpda_avdb*": ["KPDA"],
            "*/full/DRW*weekly*": ["DrWeb", "weekly"],
            "*/full/K*weekly*": ["Kaspersky", "weekly"],
        }
        if folder_ierarchy != None:
            self.FOLDER_IERARCHY = folder_ierarchy
        self.date = Renamer.strfdate(date_tag)
        self.path_to_bases_folder = path_to_bases_folder
        self.make_folder_ierarchy()
        self.move_for_mask()
        self.file_list: List[str] = self.get_all_files_in_folder(
            folder=path_to_bases_folder
        )
        if self.make_finally_zip_archive():
            logger.success(f"Total zip archive make successfull")
            logger.table_size(self.get_size_file_list())
            self.rename_base_dir()

        else:
            logger.error(f"Error for make total archive")
            import shutil

            _, _, free = shutil.disk_usage("/")
            logger.info("Free: %d GiB" % (free // (2**30)))

    def get_size_file_list(self) -> List[Tuple[str, str]]:
        size_file_list = list()
        for file in self.__get_all_file_recursive():
            size_file_list.append((file.name, self.__get_size(file)))
        return size_file_list

    def __get_size(self, file):
        def convert_bytes(size):
            """Convert bytes to KB, or MB or GB"""
            for x in ["bytes", "KB", "MB", "GB", "TB"]:
                if size < 1024.0:
                    return "%3.1f %s" % (size, x)
                size /= 1024.0

        file_size = file.stat().st_size
        return convert_bytes(file_size)

    def make_folder_ierarchy(self):
        for folder_list in self.FOLDER_IERARCHY.values():
            os.makedirs(Path(self.path_to_bases_folder, *folder_list), exist_ok=True)

    def move_for_mask(self):
        for mask in self.FOLDER_IERARCHY.keys():
            file_list_for_mask = [
                Path(file)
                for file in glob.glob(
                    str(self.path_to_bases_folder / mask), recursive=True
                )
                if os.path.isfile(file)
            ]
            self.move_file_list(file_list_for_mask, dir_list=self.FOLDER_IERARCHY[mask])

    def move_file_list(self, file_list_for_mask: List[Path], dir_list: List[str]):
        for file_path in file_list_for_mask:
            new_path = Path(self.path_to_bases_folder, *dir_list) / file_path.name
            logger.debug(f"Move {file_path} to {new_path}")
            shutil.move(src=file_path, dst=new_path)

    def get_all_files_in_folder(self, folder: Path) -> List[str]:
        """Возвращает все абсолютные пути до .zip в текущей папке"""
        return [str(file) for file in os.listdir(folder)]

    def make_finally_zip_archive(self) -> bool:
        logger.info(f"Start to make total archive updates_{self.date}.zip")
        cd_command = f"cd {self.path_to_bases_folder} && "
        zip_command = f"zip -r updates_{self.date}.zip {self.file_list_string}"
        return exec_command(command=(cd_command + zip_command))

    def rename_base_dir(self) -> None:
        new_name = self.path_to_bases_folder.parent / f"{self.date}"
        try:
            os.rename(self.path_to_bases_folder, new_name)
        except OSError as error:
            logger.error(error)

    def __get_all_file_recursive(self):
        base_dir = self.path_to_bases_folder / "**" / "*.*"
        return [Path(file) for file in glob.glob(str(base_dir), recursive=True)]

    @property
    def file_list_string(self) -> str:
        return " ".join(self.file_list)
