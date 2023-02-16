import os
from typing import List
from pathlib import Path, PosixPath
from datetime import datetime
from utils.logger import (
    logger,
    log_obj,
)


class Renamer:
    @log_obj
    def __init__(
        self,
        date_tag: str = datetime.now(),
        base_dir: Path = (Path(os.getcwd()) / "bases"),
    ) -> None:
        """Переименовывает все .zip в фомрат DRW_ESS13_*date_tag*.zip
        для указания конкретной даты использовать так
        Renamer(date_tag="20230220")
        """
        self.date = self.strfdate(date_tag)
        self.base_dir = base_dir
        self.zip_file_name = self.get_zip_files(base_dir=self.base_dir)
        self.rename_all()
        logger.success(f"Rename archive in {self.zip_file_name}")

    @staticmethod
    def strfdate(date: datetime, format: str = "%Y%m%d") -> str:
        """Возвращает текущую дату в формату 20230101, если она не передана явно
        если date_tag=строке, возвращает эту строку в неизменном формате"""
        try:
            return date.strftime(format)
        except AttributeError:
            return date

    @staticmethod
    def get_zip_files(base_dir) -> List[PosixPath]:
        """Возвращает все абсолютные пути до .zip в текущей папке"""
        return [
            base_dir / file
            for file in os.listdir(base_dir)
            if str(file).endswith(".zip")
        ]

    def rename_all(self) -> None:
        for file in self.zip_file_name:
            new_name = f'{str(file).replace(".zip","")}_{self.date}.zip'
            self.rename(file, new_name)

    @staticmethod
    def rename(first_name, second_name):
        os.rename(first_name, second_name)
