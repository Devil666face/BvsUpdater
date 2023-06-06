import os
import glob
import shutil
from pathlib import Path
from typing import List
from utils.logger import tglogger as logger
from utils.logger import log_obj


class Remover:
    @log_obj
    def __init__(
        self,
        mask_list_for_remove: List[str],
        mask_exception_list: List[str],
        base_dir: Path = Path(os.getcwd()),
    ):
        """Удаляет все директории и файлы по маске,
        для создания исключения из удаления использовать mask_exception_list
        в конце создает новую директорию bases для архивов"""
        self.base_dir = base_dir / "**"
        self.mask_list = mask_list_for_remove
        self.mask_exception_list = mask_exception_list
        self.path_list_to_remove = self.get_path_list_to_remove()
        self.remove()
        os.makedirs("bases", exist_ok=True)

    def get_path_list_to_remove(self) -> List[str]:
        """Получить список путей для выбранных масок"""
        path_to_remove = list()
        for mask in self.mask_list:
            mask_to_find = self.base_dir / mask
            logger.debug(f"Mask for remove {mask_to_find}")
            for path in glob.glob(str(mask_to_find), recursive=True):
                if Path(path).name in self.mask_exception_list:
                    logger.debug(
                        f"Dont add {path} to remove because it in exception list"
                    )
                    continue
                path_to_remove.append(path)
                logger.debug(f"Add folder to remove {path}")
        return path_to_remove

    @staticmethod
    def remove_path_or_dir(path: str) -> bool:
        """Удаляет файл если это файл, удаляет директорию,
        если это директория)))"""
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.success(f"Successfull remove file {path}")
                return True
            shutil.rmtree(path)
            logger.success(f"Successfull remove tree {path}")
            return True
        except Exception as error:
            logger.error(f"Error when try to remove {path} {error}")
            return False

    def remove(self):
        """Пройти по списку путей и удалить каждый"""
        for path in self.path_list_to_remove:
            self.remove_path_or_dir(path)
