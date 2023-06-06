import os
import ntpath
import hashlib
from pathlib import Path
from utils.renamer import Renamer
from utils.remover import Remover
from utils.logger import tglogger as logger
from utils.logger import log_obj


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
        """Создает хеши для всех .zip в папке  bases
        В случае если хэши уже имеются они будут удалены и пересчитаны занаво
        Для получения списка .zip используется функция из предыдущего
        класса Renamer"""
        self.base_dir = base_dir
        Remover(
            mask_list_for_remove=["*.md5"], mask_exception_list=[], base_dir=base_dir
        )
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
                path_to_md5_file=(file.parent / filename.replace(".zip", "")),
            )

    def write_hash_in_file(self, row_for_write: str, path_to_md5_file: Path):
        """Записать строку в файл"""
        with open(f"{path_to_md5_file}.md5", "w") as file:
            logger.success(f"Hash: {row_for_write}")
            file.write(row_for_write)

    def get_hash(self, path: Path):
        """Получаем md5 хэш для файла по его пути"""
        try:
            logger.info(f"Get hash for {path.name}")
            return hashlib.md5(file_as_bytes(open(path, "rb"))).hexdigest()
        except MemoryError as error:
            with open(path, "rb") as input_file:
                return self.hash_value_for_file(input_file)
            # logger.error(f"Error to try get hash. Memory error for {path.name}")
            # return "no hash"

    def hash_value_for_file(self, file, block_size=2**20):
        hash_function = hashlib.md5()
        while True:
            data = file.read(block_size)
            if not data:
                break
            hash_function.update(data)
        return hash_function.hexdigest()
