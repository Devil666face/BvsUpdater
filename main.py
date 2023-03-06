#!./venv/bin/python
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
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
from utils.env import (
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
from utils.logger import logger


def remove():
    """Удаляет все найденные в директории файлы по заданной маске
    директории ESS содержат в себе папки bases (появляются после создания DRWLinux),
    поэтому в конце этого класса дописана команда на создания bases в директории проекта.
    Для добавления файлов в исключение использовать mask_exception_list
    """

    remover = Remover(
        mask_list_for_remove=[
            "*.log",
            "bases",
            "Updates",
            "Temp",
            "report.txt",
            "repo",
            "repository",
            "repository.zip",
            "temp",
            "drw11_base.zip",
            "drw11_base.zip.ecp",
            # "*.md5",
            # "*.zip",
            # "*.tar.gz",
            # "*.tar.gz.cksum",
        ],
        mask_exception_list=[
            "updater.log",
        ],
    )


def make_linux_drw_base():
    """Распаковывает .lzma и создает базы из скаченных DRW_ESS репозиториев"""
    drw_linux113_obj = DRWLinuxPacker(
        base_name="DRW_ESS13",
        output_zip_name="DRW_Linux11.3",
    )
    drw_linux11_obj = DRWLinuxPacker(
        base_name="DRW_ESS11.00.0,2",
        output_zip_name="DRW_Linux11",
    )
    drw_linux10_obj = DRWLinuxPacker(
        base_name="DRW_ESS10",
        output_zip_name="DRW_Linux10",
    )


def load_ess6():
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


def load_ess6_msvs():
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


def load_drw():
    """Запускает бинарники для загрузки баз из интернета
    существует 3 типа классов
    DRWLoader, - для ESS11, ESS11002, ESS13
    DRWLoaderSS, - для всех SS
    DRWLoaderESS10, - для DRW_ESS_10
    """
    load_ess6()
    load_ess6_msvs()
    drw_ess10_obj = DRWLoaderESS10(path_to_folder="DRW_ESS10")
    drw_ss9_obj = DRWLoaderSS(path_to_folder="DRW_SS9")
    drw_ss10_obj = DRWLoaderSS(path_to_folder="DRW_SS10")
    drw_ss11_obj = DRWLoaderSS(path_to_folder="DRW_SS11")
    drw_ss115_obj = DRWLoaderSS(path_to_folder="DRW_SS11.5")
    drw_ess13_obj = DRWLoader(path_to_folder="DRW_ESS13")
    drw_ess11002_obj = DRWLoader(path_to_folder="DRW_ESS11.00.0,2")
    drw_ess11_obj = DRWLoader(path_to_folder="DRW_ESS11")

    # drw_ss_obj = DRWLoader(path_to_folder="DRW_SS")


def load_ksc():
    """Скачивает все обновления kaspersky"""
    ksc_all_obj = KscLoader(path_to_folder="KSC_all")
    kav_old_obj = KscLoader(path_to_folder="KAV_old")
    kes_11_obj = KscLoader(path_to_folder="KES_11")
    kesl_11 = KscLoader(path_to_folder="KESL_11")
    kesl_10_elbrus_obj = KscLoader(path_to_folder="KESL_10.1.2_Elbrus")


def load_other():
    """Запускает загрузку других баз:
    1. dl.kpda.ru
    2. krd.iso
    3. drweb-livedisk-900-cd.iso
    4. FSB
    """
    load_dl_kpda(user=KPDA_USER, password=KPDA_PASSWORD)
    FSBLoader(
        url_list_for_load=[
            "https://www.avz-center.ru/avs_update/drweb/11/win/drw11_base.zip",
            "https://www.avz-center.ru/avs_update/drweb/11/win/drw11_base.zip.ecp",
        ],
        user=FSB_LOGIN,
        password=FSB_PASSWORD,
    )
    Curl(url="https://rescuedisk.s.kaspersky-labs.com/latest/krd.iso")
    Curl(
        url="https://download.geo.drweb.com/pub/drweb/livedisk/drweb-livedisk-900-cd.iso"
    )


def main(scheduler=None):
    """Для добавление в конце .zip даты отличной от текущей используется
    Renamer(date_tag="20230131")
    Для отслеживания процесса загрузки можно использовать
    watch du -ah --max-depth=1 bases/ drw/ ksc/
    """
    if scheduler is not None:
        for job in scheduler.get_jobs():
            logger.debug(f"{job}")
    try:
        remove()
        load_other()
        load_drw()
        make_linux_drw_base()
        load_ksc()
        WeeklyPacker()
        Renamer()
        HashMaker()
        TotalArchive()
    except Exception as error:
        logger.exception(error)


if __name__ == "__main__":
    """Точка входа в приложение при запуске через ./main
    Запуск этого скрипта через какие-то кастомные bash выполнять
    cd *path_to_this_file* && ./main.py
    """
    main()
    scheduler = BlockingScheduler()
    scheduler.add_job(main, "cron", hour=2, args=[scheduler])  # , minute=31
    # scheduler.add_job(main, "interval", seconds=3, args=[scheduler])
    scheduler.start()
