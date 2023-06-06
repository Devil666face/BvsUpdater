import os
import subprocess
import shutil
from pathlib import Path
from utils.logger import tglogger as logger
from utils.logger import log_obj


class DRWLinuxPacker:
    @log_obj
    def __init__(
        self,
        base_name: str,
        output_zip_name: str,
        base_dir: Path = Path(os.getcwd()) / "drw",
        folder_with_bases_name: str = "repository.zip/10-drwbases",
        next_prefix_dir: str = "common",
        path_to_bases: Path = Path(os.getcwd()) / "bases",
    ) -> None:
        """
        self.path_to_lzma_dir = ./DRW_ESS13/
        self.path_to_folder_with_base = ./DRW_ESS13/repository.zip
        self.base_dir = ./
        self.full_path_to_bases = repositiry.zip/10-drwbases/*dir*/common
        """
        self.path_to_lzma_dir = base_dir / base_name
        self.path_to_folder_with_base = base_dir / base_name / folder_with_bases_name
        self.base_dir = base_dir
        self.path_to_bases = path_to_bases
        self.full_path_to_bases = self.get_temp_dir(next_prefix_dir=next_prefix_dir)
        if self.full_path_to_bases:
            logger.info(f"Start to make {output_zip_name}")
            self.make_dir_for_lzma()
            self.unpack_lzma_files()
            self.make_finally_zip_archive(
                path_to_zip=(base_dir / output_zip_name),
                path_to_source=self.path_to_lzma_dir,
            )
        else:
            logger.warning(f"Skip to wake linux archive for {output_zip_name}")

    def get_temp_dir(self, next_prefix_dir: str) -> Path | bool:
        """Получает промежуточную директорию по пути repository.zip/10-drwbases/*dir*/common"""
        try:
            temp_dir = os.listdir(self.path_to_folder_with_base)[0]
            full_path = self.path_to_folder_with_base / temp_dir / next_prefix_dir
            return full_path
        except FileNotFoundError as error:
            logger.error(
                f"Dir with source files not found {self.path_to_folder_with_base}"
            )
            return False

    def make_dir_for_lzma(self, temp_dir_name: str = "bases") -> None:
        """Создает временную директорию bases,
        которая будет использована для распоковки туда файлов"""
        self.path_to_lzma_dir = self.path_to_lzma_dir / temp_dir_name
        try:
            os.mkdir(str(self.path_to_lzma_dir))
        except FileExistsError:
            shutil.rmtree(self.path_to_lzma_dir)
            os.mkdir(str(self.path_to_lzma_dir))

    def unpack_lzma_files(self) -> None:
        """Распковать все lzma файлы в директорию bases,
        получает список файлов lzma в директории,
        выполянет функцию для каждого файла по его распоковке"""
        lzma_file_list = [
            self.full_path_to_bases / file
            for file in os.listdir(self.full_path_to_bases)
            if str(file).endswith(".lzma")
        ]
        for file in lzma_file_list:
            if not self.unpack_file(file):
                logger.error(f"Some error when unpacking file {file}")

    def unpack_file(self, path_to_file: str) -> bool:
        """Распоковывает файл lzma в директорию bases"""
        command = f"7z e {path_to_file} -o{self.path_to_lzma_dir}"
        return DRWLinuxPacker.exec_command(command)

    def make_finally_zip_archive(self, path_to_zip: str, path_to_source: str) -> bool:
        """Создает финальный архив с базами для Linux на директорию выше чем base_dir
        т.е. рядом с DRW_ESS*"""
        logger.info(f"Packing archive {path_to_zip}.zip")
        cd_command = f"cd {Path(path_to_source).parent} && "
        zip_command = f"zip -rq9 {path_to_zip}.zip ./bases && "
        mv_command = f"mv {path_to_zip}.zip {self.path_to_bases}"
        return self.exec_command(command=(cd_command + zip_command + mv_command))

    @staticmethod
    def exec_command(command: str) -> bool:
        """Выполянет команду с учетом shell, если команда успешно выполнена
        вернет True в остыльных возвращает False"""
        result = subprocess.Popen(
            command,
            shell=True,
        )
        result.wait()
        if result.returncode == 0:
            logger.debug(f"Successfull exec command {command}")
            return True
        logger.error(f"Error when exec command {command}")
        return False
