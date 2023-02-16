import os
import ntpath
import hashlib
from pathlib import Path
from utils.renamer import Renamer
from utils.logger import (
    logger,
    log_obj,
)


def file_as_bytes(file):
    """Прочитать файл и вернуть бинарный вид"""
    with file:
        return file.read()


class HashMaker:
    @log_obj
    def __init__(
        self,
        base_dir: Path = (Path(os.getcwd()) / "bases"),
    ) -> None:
        """Для получения списка .zip используется функция из предыдущего
        класса Renamer"""
        self.base_dir = base_dir
        self.zip_file_name = Renamer.get_zip_files(base_dir=self.base_dir)
        self.make_hash_files()

    def make_hash_files(self):
        """Создаем хэши для всех .zip файлов
        формируется для записи строка вида
        row_for_write = f"{hash} {filename}\n"
        """
        for file in self.zip_file_name:
            path_to_parent, filename = ntpath.split(file)
            hash = self.get_hash(path=file)
            row_for_write = f"{hash} {filename}\n"
            self.write_hash_in_file(
                row_for_write=row_for_write,
                path_to_md5_file=(self.base_dir / filename.replace(".zip", "")),
            )
            logger.success(f"Hash: {row_for_write}")

    def write_hash_in_file(self, row_for_write: str, path_to_md5_file: Path):
        """Записать строку в файл"""
        with open(f"{path_to_md5_file}.md5", "w") as file:
            file.write(row_for_write)

    def get_hash(self, path: Path):
        """Получаем md5 хэш для файла по его пути"""
        try:
            return hashlib.md5(file_as_bytes(open(path, "rb"))).hexdigest()
        except MemoryError as error:
            logger.error("Error to try get hash. Memory error")
            return "no hash"
