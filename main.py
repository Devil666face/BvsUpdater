#!./venv/bin/python
import datetime
from typing import List
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from loader.drwloader import (
    DRWLoader,
    DRWLoaderSS,
    DRWLoaderESS10,
)
from loader.smbloader import SMBLoader
from loader.dlkpdaloader import load_dl_kpda
from loader.kscloader import KscLoader
from loader.scploader import SCPLoader
from loader.fsbloader import FSBLoader
from loader.curl import Curl
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.remover import Remover
from utils.renamer import Renamer
from utils.hash import HashMaker
from utils.totalarchive import TotalArchive
from utils.weeklypacker import WeeklyPacker
from handler.env import (
    KPDA_USER,
    KPDA_PASSWORD,
    ESS6_USERNAME,
    ESS6_PASSWORD,
    ESS6_IP,
    ESS6_MSVS_USERNAME,
    ESS6_MSVS_PASSWORD,
    ESS6_MSVS_IP,
    FSB_LOGIN,
    FSB_PASSWORD,
)
from utils.logger import tglogger as logger
from utils.logger import string_week_day
from handler.cli import args
from handler.config import Config
from functools import wraps

exec_command = DRWLinuxPacker.exec_command


def main(config_file_path: str = "updater.yaml") -> None:
    try:
        config = Config(config_file_path)
        process = Process(config)
    except KeyboardInterrupt:
        logger.debug("Exit from keyboard")


class Process:
    def __init__(self, config: Config):
        self.config = config
        for task in self.config.task:
            self.__exec_func_for_attr(task)

    def __exec_func_for_attr(self, task_name):
        """Вызывает функцию с таким же названием как парамерт
        в разделе task конфига updater.yaml, если параметр True
        Если = False, то функция не будет вызвана
        """
        if not self.config.task[task_name]:
            logger.debug(f"Task:{task_name} will not be exec")
            return
        exec_func = getattr(self, task_name)
        self.__exec(exec_func)

    def __exec(self, func):
        """Запускает переданную функцию, func не имя функции,
        а сам экземпляр функции"""
        try:
            logger.debug(f"Start task:{func.__name__}")
            func()
        except Exception as error:
            logger.exception(error)

    def remove(self):
        """Удаляет все найденные в директории файлы по заданной маске
        директории ESS содержат в себе папки bases (появляются после создания DRWLinux),
        поэтому в конце этого класса дописана команда на создания bases в директории проекта.
        Для добавления файлов в исключение использовать mask_exception_list
        """
        remover = Remover(
            mask_list_for_remove=self.config.remove_list,
            mask_exception_list=self.config.remove_exclude_list,
        )

    def other(self):
        """Запускает загрузку других баз:
        1. dl.kpda.ru
        2. krd.iso
        3. drweb-livedisk-900-cd.iso
        4. FSB
        """
        if self.config.kpda:
            load_dl_kpda(user=KPDA_USER, password=KPDA_PASSWORD)
        if self.config.fsb:
            FSBLoader(
                url_list_for_load=self.config.fsb,
                user=FSB_LOGIN,
                password=FSB_PASSWORD,
            )
        if self.config.curl:
            for url in self.config.curl:
                Curl(url)

    def drw_local(self):
        if self.config.DRW_ESS6:
            """Класс для подлючения к виндовому серверу с ESS6 по smb и получения файлов
            из стандартной директории для баз:
            \c$\Program Files\DrWeb Enterprise Server\var\repository\10-drwbases
            для переопределения директории использовать
            SMBLoader(
                username=ESS6_USERNAME,
                password=ESS6_PASSWORD,
                server_ip=ESS6_IP,
                path_to_bases_dir=r"\c$\Your\directory"
            )
            осталные параметры см в описании класса loader/smbloader.py
            Обращаю внимание что строка задается через r-строку
            и путь начинается с обратного слэша \r
            """
            SMBLoader(
                username=ESS6_USERNAME,
                password=ESS6_PASSWORD,
                server_ip=ESS6_IP,
            )

        if self.config.DRW_ESS6_MSVS:
            """Класс для подключения к серверу с ESS6_MSVS по ssh и получения файлов
            из стандартной директории для баз:
            path_to_bases_dir: str = "/var/opt/drwcs/repository/10-drwbases",
            при этом проверяется содержимое файла .id (где указана дата баз, при несовпадении
            скачивание не происходит), для игнорирования этого параметра, добаить в вызове
            IGNORE_DATE=True,
            """
            SCPLoader(
                username=ESS6_MSVS_USERNAME,
                password=ESS6_MSVS_PASSWORD,
                server_ip=ESS6_MSVS_IP,
                IGNORE_DATE=True,
            )

    def drw(self):
        """Запускает бинарники для загрузки баз из интернета
        существует 3 типа классов
        DRWLoader, - для ESS11, ESS11002, ESS13
        DRWLoaderSS, - для всех SS
        DRWLoaderESS10, - для DRW_ESS_10
        """
        if self.config.DRW_ESS10:
            DRWLoaderESS10(path_to_folder="DRW_ESS10")
        if self.config.DRW_SS:
            for drw_ss_name in self.config.DRW_SS:
                DRWLoaderSS(path_to_folder=drw_ss_name)
        if self.config.DRW_ESS:
            for drw_ess_name in self.config.DRW_ESS:
                DRWLoader(path_to_folder=drw_ess_name)

    def drw_linux(self):
        """Распаковывает .lzma и создает базы из скаченных DRW_ESS репозиториев"""
        if self.config.drw_linux_dict:
            for drw_linux_name, drw_ess_source_name in zip(
                self.config.drw_linux_dict, self.config.drw_linux_dict.values()
            ):
                drw_linux113_obj = DRWLinuxPacker(
                    base_name=drw_ess_source_name,
                    output_zip_name=drw_linux_name,
                )

    def ksc(self):
        """Скачивает все обновления kaspersky"""
        if self.config.ksc_list:
            for ksc_name in self.config.ksc_list:
                KscLoader(path_to_folder=ksc_name)

    def weekly_pack(self):
        if self.config.weekly_date_tag_old:
            WeeklyPacker(
                exclude_list=self.config.weekly_exclude_list,
                date_tag_old=self.config.weekly_date_tag_old,
            )
        elif self.config.weekly_week_day:
            WeeklyPacker(
                exclude_list=self.config.weekly_exclude_list,
                week_day=self.config.weekly_week_day,
            )
        elif self.config.weekly_days_ago:
            WeeklyPacker(
                exclude_list=self.config.weekly_exclude_list,
                days_ago=self.config.weekly_days_ago,
            )
        else:
            WeeklyPacker(exclude_list=self.config.weekly_exclude_list)

    def rename(self):
        if self.config.rename_date_tag:
            Renamer(date_tag=self.config.rename_date_tag)
        else:
            Renamer()

    def hash(self):
        HashMaker()

    def pre_total_script(self):
        self.__exec_script_list(self.config.pre_total_script_list)

    def total_archive(self):
        if self.config.total_archive_date_tag:
            TotalArchive(
                self.config.folder_ierarchy, date_tag=self.config.total_archive_date_tag
            )
        else:
            TotalArchive(self.config.folder_ierarchy)

    def post_total_script(self):
        self.__exec_script_list(self.config.post_total_script_list)

    def __exec_script_list(self, script_list: List[str] | bool):
        if not script_list:
            return
        for script in script_list:
            exec_command(script)


def create_task_for_config(
    scheduler: BlockingScheduler | BackgroundScheduler,
    config_file_path: str = "updater.yaml",
) -> None:
    config = Config(config_file_path)
    if config.day_of_week is not False:
        logger.info(
            f"Update start at weekday:{string_week_day(config.day_of_week)} hour:{config.hour} minute:{config.minute}"
        )
        scheduler.add_job(
            main,
            "cron",
            hour=int(config.hour),
            minute=int(config.minute),
            day_of_week=int(config.day_of_week),
            args=[config_file_path],
        )
    else:
        logger.info(
            f"Update start at weekday:everyday hour:{config.hour} minute:{config.minute}"
        )
        scheduler.add_job(
            main,
            "cron",
            hour=int(config.hour),
            minute=int(config.minute),
            args=[config_file_path],
        )
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.debug("Exit from keyboard")


if __name__ == "__main__":
    """Точка входа в приложение при запуске через ./main
    Запуск этого скрипта через какие-то кастомные bash выполнять
    cd *path_to_this_file* && ./main.py
    """
    if args.daemon:
        logger.info("Exec in daemon mode")
        # scheduler = BlockingScheduler()
        create_task_for_config(BackgroundScheduler(), config_file_path="daily.yaml")
        create_task_for_config(BlockingScheduler(), config_file_path="updater.yaml")
    elif args.now:
        logger.info("Exec in download mode for weekly bases")
        main()
    elif args.today:
        logger.info("Exec in download mode for daily bases")
        main(config_file_path="daily.yaml")
    else:
        logger.info("Use -h/--help for get help message")
