import os
import re
import glob
from typing import List
from pathlib import Path, PosixPath
from datetime import datetime
from utils.logger import tglogger as logger
from utils.logger import log_obj


class Renamer:
    @log_obj
    def __init__(
        self,
        date_tag=None,
        base_dir: Path = (Path(os.getcwd()) / "bases"),
    ) -> None:
        """Переименовывает все .zip в фомрат DRW_ESS13_*date_tag*.zip
        для указания конкретной даты использовать так
        Renamer(date_tag="20230220")
        В том случае если файлы уже переименованы или имею некорректные даты
        повторный запуск исправит даты на текущие или указанные в date_tag
        Переименование файлов требует запуска HashMaker
        """
        if date_tag is None:
            date_tag = datetime.now()
        self.date = self.strfdate(date_tag)
        self.base_dir = base_dir
        self.zip_file_name = self.get_zip_files(base_dir=self.base_dir)
        self.rename_all()
        logger.success(f"Rename archive in {self.base_dir}")

    @staticmethod
    def strfdate(date: datetime, format: str = "%Y%m%d") -> str:
        """Возвращает текущую дату в формату 20230101, если она не передана явно
        если date_tag=строке, возвращает эту строку в неизменном формате"""
        try:
            return date.strftime(format)
        except AttributeError:
            return date

    @staticmethod
    def get_zip_files(base_dir) -> List[Path]:
        """Возвращает все абсолютные пути до .zip в текущей папке"""
        base_dir = base_dir / "**" / "*.zip"
        return [Path(file) for file in glob.glob(str(base_dir), recursive=True)]
        # return [
        #     base_dir / file
        #     for file in os.listdir(base_dir)
        #     if str(file).endswith(".zip")
        # ]

    def rename_all(self) -> None:
        """Получает новое имя для архива в формате DRW_ESS11_20230318.zip
        если имя архима уже изменено или содержит _20230318 или любые другие
        сочетания _*8цифр* заменяет их на date_tag"""
        for file in self.zip_file_name:
            # file_name_wtithout_zip = str(file).replace(".zip", "")
            dates_in_file_name = re.findall(r"_\d{8}", file.name)
            regex_file_name = file
            if dates_in_file_name:
                file_name = re.sub(r"_\d{8}", "", file.name)
                regex_file_name = file.parent / file_name
            new_name = f'{str(regex_file_name).replace(".zip","")}_{self.date}.zip'
            self.rename(file, new_name)

    @staticmethod
    def rename(first_name, second_name):
        os.rename(first_name, second_name)
