import os
import shutil
import smbclient
import smbclient.shutil
from pathlib import Path
from smbclient import scandir
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class SMBLoader:
    @log_obj
    def __init__(
        self,
        username: str,
        password: str,
        server_ip: str,
        base_name: str = "DRW_ESS6",
        path_to_source: str = "repository",
        path_to_bases_dir: str = r"\c$\Program Files\DrWeb Enterprise Server\var\repository\10-drwbases",
        base_dir: Path = Path(os.getcwd()) / "repository" / "10-drwbases",
    ):
        """Cоздает smb подключение к папке принимает на вход username: str, - имя пользователя включая домен в формате ДОМЕН\юзер
        password: str,
        server_ip: str,
        base_name: str = "DRW_ESS6", - имя для ахрива который будет создаваться
        path_to_source: str = "repository", - имя локальной папки в которой будут лежать скопированные файлы
        path_to_bases_dir: str = r"\c$\Program Files\DrWeb Enterprise Server\var\repository\10-drwbases",
        base_dir: Path = Path(os.getcwd()) / "repository" / "10-drwbases",
        """
        self.path_to_bases_dir = r"\\" + server_ip + path_to_bases_dir
        self.server_ip = server_ip
        self.base_dir = base_dir
        self.path_to_source = path_to_source
        os.makedirs(self.base_dir)
        smbclient.ClientConfig(username=username, password=password)
        try:
            smbclient.register_session(server_ip, username, password)
            self.file_list = self.get_file_list(path_to_folder=self.path_to_bases_dir)
            if self.make_finally_zip_archive(zip_name=base_name):
                logger.info(f"Start to load {base_name}")
            else:
                logger.warning(f"Error when load {base_name}")
            shutil.rmtree(self.base_dir.parent)
        except ValueError as error:
            logger.exception(error)

    def get_file_list(self, path_to_folder) -> None:
        """Рекурсивная функция получает список директорий в smb share папке
        проходит по элементу списка, если это директория, создает такую же директорию
        относительно self.base_dir, если это файл вызывает функцию для загрузки файла из share"""
        for file_info in scandir(path_to_folder):
            file_name = path_to_folder + "\\" + file_info.name
            path_to_local = file_name.replace(self.path_to_bases_dir, "").replace(
                "\\", "/"
            )
            abs_path = Path(str(self.base_dir) + path_to_local)
            logger.debug(f"Copy from {file_name} to {abs_path}")
            if file_info.is_file():
                self.copy_file(src=file_name, dst=abs_path)
            elif file_info.is_dir():
                os.makedirs(abs_path)
                self.get_file_list(file_name)
            else:
                logger.error(f"{file_name} is not a directory or file")

    def copy_file(self, src, dst) -> None:
        """Скопировать файл из src в dst"""
        smbclient.shutil.copyfile(
            src=src,
            dst=dst,
        )
        logger.debug(f"Copy file from {src} to {dst}")

    def make_finally_zip_archive(self, zip_name: str) -> bool:
        """Создает финальный архив с базами
        и перемещает его в директорию bases"""
        logger.info(f"Start to make archive {zip_name}")
        zip_command = f"zip -rq9 {zip_name}.zip ./{self.path_to_source} && "
        mv_command = f"mv {zip_name}.zip bases/"
        return exec_command(command=(zip_command + mv_command))
