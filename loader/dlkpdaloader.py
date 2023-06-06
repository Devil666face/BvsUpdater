import lxml
import requests
import os
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import (
    datetime,
    timedelta,
)
from utils.logger import tglogger as logger


session = requests.Session()


def get_token() -> str:
    """Get token for auth"""
    login_get = session.get("https://dl.kpda.ru/index.php/login?clear=1")
    soup = BeautifulSoup(login_get.text, "lxml")
    head = soup.find("head")
    token = head["data-requesttoken"]
    return token


def login(token: str, user: str, password: str):
    """POST request for auth return [200] if auth successfull"""
    login_response = session.post(
        "https://dl.kpda.ru/index.php/login",
        {
            "user": user,
            "password": password,
            "timezone": "Europe/Moscow",
            "timezone_offset": "3",
            "requesttoken": f"{token}",
        },
    )
    return login_response


def get_date_list():
    """Get list with three days before and after"""
    three_before = datetime.today() - timedelta(8)
    date_list = [three_before.strftime("%Y%m%d")]

    while three_before < datetime.today() + timedelta(2):
        three_before += timedelta(days=1)
        date_list.append(three_before.strftime("%Y%m%d"))
    return date_list


def get_file_name(url_to_download: str) -> str:
    """Get filename from url"""
    return url_to_download.split("/")[-1]


def download(url_for_download: str):
    """Download file from any url"""
    file_name = get_file_name(url_for_download)
    try:
        with (session.get(url_for_download)) as download_response:
            download_response.raise_for_status()
            with open(f"{file_name}", "wb") as file:
                file.write(download_response.content)
                return True
    except requests.exceptions.HTTPError as er:
        logger.debug(f"Not found files to this date {er}")
        return False


def try_to_download(date_list: list):
    """Try to download files for day in day list, if download successfull return with True"""
    for date in date_list:
        responce_status_for_arch = download(
            url_for_download=f"https://dl.kpda.ru/remote.php/webdav/%D0%91%D0%94%20%D0%9F%D0%9A%D0%92/kpda_avdb_{date}.tar.gz"
        )
        responce_status_for_sum = download(
            url_for_download=f"https://dl.kpda.ru/remote.php/webdav/%D0%91%D0%94%20%D0%9F%D0%9A%D0%92/kpda_avdb_{date}.tar.gz.cksum"
        )
        if responce_status_for_arch and responce_status_for_sum:
            logger.success(f"All files download for dl.kpda.ru")
            return True


def move():
    base_path = Path(os.getcwd())
    for path in os.listdir(base_path):
        if str(path).endswith(".tar.gz") or str(path).endswith(".tar.gz.cksum"):
            shutil.move(str(base_path / Path(path)), str(base_path / "bases"))


def load_dl_kpda(user: str, password: str):
    token = get_token()
    logger.debug(f"Token {token} for download dl.kpda.ru")
    login_response = login(token, user, password)
    logger.debug(f"Login status {login_response} when login in dl.kpda.ru")
    date_list = get_date_list()
    try_to_download(date_list)
    move()
