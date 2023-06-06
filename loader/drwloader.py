import os
import subprocess
from pathlib import Path
from loader.scheduler import drw_ess10_log_check
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class DRWLoader:
    @log_obj
    def __init__(
        self,
        path_to_folder: str,
        base_dir: Path = Path(os.getcwd()) / "drw",
        load_script_name: str = "start.sh",
        path_to_bases: Path = Path(os.getcwd()) / "bases",
    ) -> None:
        """Выполняет запуск start.sh и создание архива
        base_dir=путь к текущей директории в которой исполняется скрипт
        self.command выполняет сначало переход в директорию со стартовым скриптом
        и только потом запуск скрипта"""
        self.base_dir = base_dir
        self.path_to_bases = path_to_bases
        self.path_to_folder = self.base_dir / path_to_folder
        self.load_script_name = load_script_name
        self.cmd_to_load = self.path_to_folder / self.load_script_name
        self.command = f"cd {str(self.path_to_folder)} && {self.cmd}"
        self.restart_wine_server()
        logger.info(f"Start download {path_to_folder}")
        if self.load():
            logger.success(f"{path_to_folder} successfull load")
            if self.make_finally_zip_archive(zip_name=path_to_folder):
                logger.success(f"{path_to_folder} archive make successfull")
            else:
                logger.error(f"{path_to_folder} error make archive")
        else:
            logger.error(f"{path_to_folder} not load")

    def make_finally_zip_archive(self, zip_name: str) -> bool:
        """Перемещает архив DRW_ESS**.zip в папку bases, архив создается самим загрузчиком
        см. параметр в drwreploader.conf
        Разархивирует архив в папку repository.zip (будет необходима для создания Linux баз)
        """
        logger.info(f"Start to make archive {zip_name}")
        path_to_source = self.path_to_folder / "repository.zip"
        path_to_zip = self.path_to_folder / f"{zip_name}.zip"
        # path_to_source = self.path_to_folder
        # cd_command = f"cd {path_to_source} && "
        cd_command = f"cd {self.path_to_folder} && "
        # zip_command = f"zip -rq9 {zip_name}.zip * && "
        mv_command = f"mv {zip_name}.zip {self.path_to_bases}"
        unzip_command_for_linux = f"unzip -q {path_to_zip} -d {path_to_source}"
        exec_command(unzip_command_for_linux)
        return exec_command(command=(cd_command + mv_command))
        # return exec_command(command=(cd_command + zip_command + mv_command))

    def load(self) -> bool:
        logger.debug(f"Command for start download {self.command}")
        result = subprocess.run(
            self.command,
            shell=True,
            encoding="UTF-8",
        )
        return True

    def restart_wine_server(self):
        os.system("/usr/bin/wineserver -k")

    @property
    def cmd(self) -> str:
        """Возвращает абсолютный путь к файлу DRW_ESS13/start.sh,
        если имя load_script_name не переопределено
        """
        return str(self.cmd_to_load)


class DRWLoaderESS10(DRWLoader):
    """Класс для загрузки DRWLoaderESS10, сделан отдельно, потому что после запуска
    бинарника через wine по заверщению загрузки скрипт зависает, способ решить проблему
    описан в schduler.py После скачивания баз во временную директорию, drwreploader повиснет.
    Убиваем процесс когда видим строку успешной загрузки в логах и запускаем loader еще раз,
    для создания архивы с базами (подписанным loaderом)
    """

    def load(self) -> bool:
        logger.debug(f"Command for start download {self.command}")
        load_drw_ess10 = subprocess.Popen(
            self.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
        drw_ess10_log_check(self.path_to_folder)
        returncode = load_drw_ess10.wait()
        make_zip = subprocess.Popen(
            self.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
        returncode = make_zip.wait()
        return True

    def make_finally_zip_archive(self, zip_name: str) -> bool:
        logger.info(f"Start to make archive {zip_name}")
        path_to_source = self.path_to_folder / "repository.zip"
        path_to_zip = self.path_to_folder / f"{zip_name}.zip"
        cd_command = f"cd {self.path_to_folder} && "
        mv_command = f"mv {zip_name}.zip {self.path_to_bases}"
        unzip_command_for_linux = f"7z x {path_to_zip} -o{path_to_source}"
        exec_command(unzip_command_for_linux)
        return exec_command(command=(cd_command + mv_command))

    # def make_finally_zip_archive(self, zip_name: str) -> bool:
    #     """Переопределяет функцию у DRWLoader, zip_command, вместо * ./10-drwbases
    #     т.к. в папке находится еще reploader.tmp и он тоже попадает в архив
    #     """
    #     logger.info(f"Start to make archive {zip_name}")
    #     path_to_source = self.path_to_folder / "repository.zip"
    #     cd_command = f"cd {path_to_source} && "
    #     zip_command = f"zip -rq9 {zip_name}.zip ./10-drwbases && "
    #     mv_command = f"mv {zip_name}.zip {self.path_to_bases}"
    #     return exec_command(command=(cd_command + zip_command + mv_command))


class DRWLoaderSS(DRWLoader):
    """Переопределяет стандартную функцию для создание архива конкретно для баз SS,
    из-за особенностей состава репозитория,
    path_to_source = self.path_to_folder / "repo"
    берется папка repo
    """

    def make_finally_zip_archive(self, zip_name: str) -> bool:
        """Создает финальный архив с базами на директорию выше чем base_dir т.е. рядом с DRW_ESS*"""
        logger.info(f"Start to make archive {zip_name}")
        # path_to_source = self.path_to_folder / "repo"
        path_to_source = self.path_to_folder
        cd_command = f"cd {path_to_source} && "
        zip_command = f"zip -rq9 {zip_name}.zip ./repo && "
        mv_command = f"mv {zip_name}.zip {self.path_to_bases}"
        return exec_command(command=(cd_command + zip_command + mv_command))
