import subprocess
import os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError


scheduler = BackgroundScheduler()


def drw_ess10_log_check(path_to_folder: Path, log_name: str = "drwreploader.log"):
    """Запускает в бекграунде задачу каждые 2 секунды делающую tail log файла DRW_ESS10"""
    scheduler.add_job(
        tail_drw_ess10_log,
        "interval",
        args=[scheduler, path_to_folder, log_name],
        seconds=2,
        id="drw_ess10_log_check",
    )
    try:
        scheduler.start()
    except SchedulerAlreadyRunningError:
        pass


def find_line(line: str, string_for_find: str) -> bool:
    """Поиск строки в построке"""
    if line.find(string_for_find) != -1:
        return True
    return False


def tail_drw_ess10_log(scheduler, path_to_folder: Path, log_name: str) -> None:
    """Выполяет tail для файла и чтение его содержимого
    в случае если в строке лога найдена строка updated successfully
    1. Завершает wineserver -k
    2. Отключает переодический чек лога"""
    command = f"tail {str(path_to_folder)}/{log_name}"
    result = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="UTF-8",
    )
    if successfull_load_check(result, string_for_find="updated successfully"):
        os.system("/usr/bin/wineserver -k")
        scheduler.remove_job("drw_ess10_log_check")


def successfull_load_check(result, string_for_find) -> bool:
    """Проверка на наличие строки в выводе команды tail"""
    for line in result.stdout:
        if find_line(line=line.strip(), string_for_find=string_for_find):
            return True
    return False
