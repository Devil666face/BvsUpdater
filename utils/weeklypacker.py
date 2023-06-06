import os
import glob
import re
import subprocess
import shutil
from typing import (
    List,
    Tuple,
)
from datetime import (
    datetime,
    timedelta,
)
from pathlib import (
    Path,
    PosixPath,
)
from utils.renamer import Renamer
from utils.logger import tglogger as logger
from utils.logger import log_obj
from utils.drwlinuxpacker import DRWLinuxPacker

exec_command = DRWLinuxPacker.exec_command


class WeeklyPacker(Renamer):
    @log_obj
    def __init__(
        self,
        path_to_base_dir_new: Path = (Path(os.getcwd()) / "bases"),
        date_tag_now: datetime = datetime.now(),
        exclude_list: List[str] = [
            "updates",
            "FSB.zip",
            "DRW_ESS10.zip",
            "DRW_ESS11.zip",
            "DRW_ESS11.00.0,2",
            "DRW_ESS13.zip",
        ],
        date_tag_old=None,
        days_ago=7,
        week_day="wednesday",
    ):
        """Определяет директорию со старыми архивами, получает содержимое old и new архивов
        запускает сравнение для каждого из архивов.
        По стандарту используется имя папки в формате 20230101 (ГГГГММДД), которое получается путем поиска
        последней среды (eсли не передан другой день недели) относительного сегодня.
        Если дата передана в явном виде, то будет искаться
        папка с этой датой. Так же если передано в явном виде количество дней назад относительно сегодня
        не равное 7, будет найдена папка с именем сегодня - колво дней назад.
        Пример: сегодня 20230304
        1.WeeklyPacker() - последняя среда - 20230301
        2.WeeklyPacker(week_day='monday') - последний понедельник - 20230227
        3.WeeklyPacker(date_tag_old='20230303') - указано явно - 20230303
        4.WeeklyPacker(days_ago=5) - 5 дней назад относительно сегодня = 20230304 - days(5) = 20230227
        Eсли папка со старыми архивами не находится, то сравнение пропускается"""
        date_tag_now = datetime.now()
        self.exclude_list = exclude_list
        self.path_to_base_dir_new = path_to_base_dir_new
        if date_tag_old is not None:
            self.date_old = date_tag_old
        elif days_ago != 7:
            self.date_old = self.strfdate(
                date=self.get_old_date(
                    now_date=date_tag_now,
                    days_ago=days_ago,
                )
            )
        else:
            self.date_old = self.strfdate(self.get_last_week_day(week_day))
        logger.info(f"Find folder with name {self.date_old}")
        self.date_now = self.strfdate(date_tag_now)
        self.path_to_base_dir_old = Path(os.getcwd()) / self.date_old
        self.zip_file_list_new = self.get_zip_files(base_dir=self.path_to_base_dir_new)
        self.zip_file_list_old = self.get_zip_files_recursive(
            base_dir=self.path_to_base_dir_old
        )
        if self.zip_file_list_old and self.zip_file_list_new:
            self.compair_weekle_archives()
        else:
            logger.error("Skip to make weekly archives")

    def get_last_week_day(self, week_day: str) -> datetime:
        """
        Возвращает дату последней среды (по стандарту), если день недели не передан явно,
        в том случае если день недели передан явно - вернет его дату на предыдущей неделе,
        если в названии дня недели допущена ошибка вернет последную среду
        """
        week_day_dict = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        today = datetime.today()
        weekday_days_ago = today.weekday() - week_day_dict.get(week_day, 2)
        if weekday_days_ago <= 0:
            weekday_days_ago = weekday_days_ago + 7
        return today - timedelta(days=weekday_days_ago)

    def get_old_date(self, now_date: datetime, days_ago: int) -> datetime:
        """Получить дату days_ago дней назад относительно now_date"""
        return now_date - timedelta(days=days_ago)

    def get_zip_files(self, base_dir) -> List[PosixPath] | bool:
        """Получает все .zip в base_dir=path_to_base_dir,
        проверяет на наличие имен файлов с списке исключений,
        возвращает список без исключений"""
        try:
            zip_file_list = Renamer.get_zip_files(base_dir)
        except FileNotFoundError as error:
            logger.error(f"Not found old directory with bases {base_dir}")
            return False
        return [
            file for file in zip_file_list if not self.is_exclude(file_name=file.name)
        ]

    def get_zip_files_recursive(self, base_dir) -> List[PosixPath] | bool:
        """Получает рекурсивно все .zip в base_dir=path_to_base_dir,
        проверяет на наличие имен файлов с списке исключений,
        возвращает список без исключений,
        если папка не найдена выходит и пропускает создание недельных баз"""
        if not os.path.exists(base_dir):
            logger.error(f"Not found old directory with bases {base_dir}")
            return False
        base_dir = base_dir / "**" / "*.zip"
        zip_file_list = [
            Path(file) for file in glob.glob(str(base_dir), recursive=True)
        ]
        return [
            file for file in zip_file_list if not self.is_exclude(file_name=file.name)
        ]

    def is_exclude(self, file_name: str) -> bool:
        """Ищет в имени файла один из тэго в exclude_list"""
        for file_tag in self.exclude_list:
            if file_name.find(file_tag) != -1:
                return True
        return False

    def is_name_equal(self, new_name: str, old_name: str):
        """Проверяет совпедение имен для начала сравнения недельных баз
        old_product_name получается из DRW_ESS11_20230101.zip путем отбразывания части
        _20230101.zip
        new_product_name получается путем замены в DRW_ESS11.zip .zip на пустоту
        в момент запуска этой функции состояние проекта выглядит как
        -bases/ (директория с только, что скаченными базами)
            |-DRW_ESS13.zip
            |-...
        20230101/ (директория со старыми базами)
            |-DRW_ESS13_20230101.zip
            |-...
        """
        if re.findall(r"weekly", old_name) or re.findall(r"weekly", new_name):
            """Если в старом или новом имени есть weekly отбрасываем"""
            return False
        old_product_name = re.split(r"_\d{8}", old_name)[0]
        new_product_name = re.sub(r".zip", "", new_name)
        if re.findall(r"\d{8}", new_name):
            """Если сравнение запущено повторно и новый архив уже DRW_ESS13_20230308.zip
            Ищем старый weekly архив (если есть) и удаляем его, для избежания дальнейших
            конфликтов при сортировке по папкам"""
            new_product_name = re.split(r"_\d{8}", new_name)[0]
            base_dir = (
                self.path_to_base_dir_new / "**" / f"{new_product_name}*weekly*.zip"
            )
            for file in glob.glob(str(base_dir), recursive=True):
                logger.debug(f"Remove old weekly archive {file} in current new folder")
                os.remove(str(file))

        logger.debug(f"Compare base name old:{old_product_name} new:{new_product_name}")
        if new_product_name == old_product_name:
            logger.success(
                f"Start to comapare archives whith equal names old:{old_name} new:{new_name}"
            )
            return True
        return False

    def compair_weekle_archives(self):
        """Запускает цикл в цикле для всех .zip из старой и новой директории
        в том случае если у баз одно имя is_name_equal, вызывает WeeklyCompair
        """
        for new_archive_name in self.zip_file_list_new:
            for old_archive_name in self.zip_file_list_old:
                if self.is_name_equal(
                    new_name=new_archive_name.name, old_name=old_archive_name.name
                ):
                    WeeklyCompair(
                        old_archive_name=old_archive_name,
                        new_archive_name=new_archive_name,
                        date_now=self.date_now,
                    )


class WeeklyCompair(WeeklyPacker):
    @log_obj
    def __init__(
        self,
        old_archive_name: Path,
        new_archive_name: Path,
        date_now: str,
    ):
        self.old_archive_name = old_archive_name
        self.new_archive_name = new_archive_name
        self.date_now = date_now
        self.base_dir = self.new_archive_name.parent
        self.old_dir_for_unpack = self.base_dir / "tmp_old"
        self.new_dir_for_unpack = self.base_dir / "tmp_new"
        self.diff_dir_for_unpack = self.base_dir / "tmp_diff"
        self.diff_file = self.base_dir / "diff"
        self.zip_name = self.get_zip_name(path_to_arhc=self.new_archive_name)
        self.make_temp_dirs()
        self.unzip(zip_name=self.new_archive_name, dir_name=self.new_dir_for_unpack)
        self.unzip(zip_name=self.old_archive_name, dir_name=self.old_dir_for_unpack)
        self.rsync()
        if self.is_unique():
            logger.success(
                f"Archives {self.new_archive_name} and {self.old_archive_name} is unique"
            )
            (
                self.unique_dir_list,
                self.unique_file_list,
            ) = self.get_unqiue_file_dir_list_form_rsync_file()
            self.create_dir_for_unique_dir_list(dir_list=self.unique_dir_list)
            self.copy_unique_file(
                file_list=self.unique_file_list,
                left_prefix=self.new_dir_for_unpack,
                right_prefix=self.diff_dir_for_unpack,
            )
            self.make_finally_zip_archive(
                zip_name=self.zip_name,
                dir_name=self.diff_dir_for_unpack,
            )
        else:
            logger.error(
                f"Archives is equal {self.new_archive_name} {self.old_archive_name}"
            )
        self.remove_temp_dirs()

    def get_zip_name(self, path_to_arhc: Path) -> str:
        """Получает из формата DRW_ESS13.zip -> DRW_ESS13
        и возвращает DRW_ESS13_weekly.zip"""
        base_name = re.sub(r".zip", "", path_to_arhc.name)
        return f"{base_name}_weekly.zip"

    def create_dir_for_unique_dir_list(self, dir_list: List[PosixPath]) -> None:
        """Созадает директории для Path из списка директори в файле rsynca"""
        for dir_path in dir_list:
            os.makedirs(dir_path, exist_ok=True)

    def copy_unique_file(
        self,
        file_list: List[PosixPath],
        left_prefix: PosixPath,
        right_prefix: PosixPath,
    ) -> None:
        """Копирует файлы из src в dst для списка файлов
        в списке файлов находит относительный путь к файлу
        left_prefix = tmp_new
        right_prefix = tmd_diff"""

        def make_dir_before_file_copy(src: Path, dst: Path):
            os.makedirs(dst.parent, exist_ok=True)
            shutil.copy(src, dst)

        for file_path in file_list:
            src = left_prefix / file_path
            dst = right_prefix / file_path
            make_dir_before_file_copy(src, dst)

    def get_unqiue_file_dir_list_form_rsync_file(
        self,
    ) -> Tuple[List[PosixPath], List[PosixPath]]:
        """Читает содержимое файла diff полученного в результате выполения
        команды rsync возвращает два списка с дельта файлами в новом архиве
        1. Список с директориями
        2. Список с файлами (непосредственно дельта)
        Нельзя вернуть список только с файлами, потому что при копированиии файла,
        необходимо наличие всех его родительских директорий
        Заполнение списков происходит путем построчного чтения файла diff
        * если файл начинается со строки cd - добавляем в список директорий
        * если файл начинается с >f - добавляет в список файлов
        все остальные варианты попадают в else"""
        dir_list: List[PosixPath] = list()
        file_list: List[PosixPath] = list()
        logger.debug(f"Rsync file for {self.zip_name}")
        with open(self.diff_file, "r") as diff_file:
            for line in diff_file:
                logger.debug(line)
                if re.match(r"[c][d]", line):
                    dir_list.append(
                        self.get_path_from_rsync_line(
                            line=line,
                            prefix_before_path=self.diff_dir_for_unpack,
                        )
                    )
                # elif re.match(r"[c][f]", line) or re.match(r"[>][f]", line):
                elif re.match(r"[>][f]", line):
                    file_list.append(
                        self.get_path_from_rsync_line(
                            line=line,
                            # prefix_before_path=self.new_dir_for_unpack,
                        )
                    )
                else:
                    pass
        return dir_list, file_list

    def get_path_from_rsync_line(
        self, line: str, prefix_before_path: PosixPath = None
    ) -> PosixPath:
        """Выполняет split по пробельнмому символу строки из rsycn файла
        с помощью регулярки возвращает путь с преписко перед ним, если она была передана,
        если не передана, возвращает просто путь"""
        path = re.split(r"\s", line)[1]
        if prefix_before_path is not None:
            return prefix_before_path / path
        return Path(path)

    def is_unique(self) -> bool:
        """Выполняет grep символа > для поиска в файле diff
        если returncode выполения команды не равен 0 значит > не найден
        и функция возвращает False т.е. в файлах идентичны"""
        command = f"cat {self.diff_file} | grep -q '>'"
        result = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
        returncode = result.wait()
        if returncode != 0:
            return False
        return True

    def make_temp_dirs(self):
        """Создает temp директории для промежуточных распаковок
        при это сначала удалет эти директории, если они есть"""
        self.remove_temp_dirs()
        os.makedirs(self.old_dir_for_unpack, exist_ok=True)
        os.makedirs(self.new_dir_for_unpack, exist_ok=True)
        os.makedirs(self.diff_dir_for_unpack, exist_ok=True)
        self.diff_file.touch()

    def remove_temp_dirs(self):
        """Удаляет промежуточные директории и файл сравения rsync"""
        shutil.rmtree(self.old_dir_for_unpack, ignore_errors=True)
        shutil.rmtree(self.new_dir_for_unpack, ignore_errors=True)
        shutil.rmtree(self.diff_dir_for_unpack, ignore_errors=True)
        if os.path.exists(self.diff_file):
            os.remove(self.diff_file)

    def make_finally_zip_archive(self, zip_name: str, dir_name: Path) -> bool:
        """Создает архив с недельными базами и перемещает его в папку bases
        т.к. он находится по пути ./bases/diff_temp/
        В том случае если запущено повторно поверх уже созданных баз
        убираем 20230308 в названии нового архива"""
        zip_name = re.sub("_\d{8}", "", zip_name)
        cd_command = f"cd {dir_name} && "
        zip_command = f"zip -rq9 {zip_name} * && "
        mv_command = f"mv {zip_name} {self.base_dir}"
        if exec_command(cd_command + zip_command + mv_command):
            logger.success(f"Successfull make zip {zip_name}")
        else:
            logger.error(f"Error when zip {zip_name}")

    def unzip(self, zip_name: Path, dir_name: Path):
        """Распаковать архив в выбранную директорию"""
        logger.info(f"Unpack {zip_name}")
        command = f"unzip -q {zip_name} -d {dir_name}"
        if exec_command(command):
            logger.success(f"Successfull unpack {zip_name}")
        else:
            logger.error(f"Error when unpack {zip_name}")

    def rsync(self):
        """Запускает команду rsync"""
        logger.info(f"Make rsync")
        command = f"rsync -acvin --no-times --no-perms --no-owner --no-group --checksum --compare-dest={self.old_dir_for_unpack} {self.new_dir_for_unpack}/ {self.diff_dir_for_unpack} > {self.diff_file}"
        if exec_command(command):
            logger.success(f"Successfull make rsync")
        else:
            logger.error(f"Error when make rsync")
