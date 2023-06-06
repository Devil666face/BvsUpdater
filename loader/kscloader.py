import os
from pathlib import Path
from loader.drwloader import DRWLoader
from utils.drwlinuxpacker import DRWLinuxPacker
from utils.logger import tglogger as logger
from utils.logger import log_obj

exec_command = DRWLinuxPacker.exec_command


class KscLoader(DRWLoader):
    @log_obj
    def __init__(
        self,
        path_to_folder: str,
        base_dir: Path = Path(os.getcwd()) / "ksc",
        load_script_name: str = "start.sh",
        path_to_bases: Path = Path(os.getcwd()) / "bases",
    ) -> None:
        super().__init__(
            path_to_folder,
            base_dir,
            load_script_name,
            path_to_bases,
        )

    def make_finally_zip_archive(self, zip_name: str) -> bool:
        logger.info(f"Start to make archive {zip_name}")
        path_to_source = self.path_to_folder
        cd_command = f"cd {path_to_source} && "
        zip_command = f"zip -rq9 {zip_name}.zip ./Updates && "
        mv_command = f"mv {zip_name}.zip {self.path_to_bases}"
        return exec_command(command=(cd_command + zip_command + mv_command))
