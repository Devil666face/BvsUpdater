import os
from dotenv import load_dotenv
from utils.logger import logger


load_dotenv()


def load_env(env_name: str) -> str:
    __env = os.getenv(env_name)
    if not __env:
        logger.error(f"Not found {env_name} in .env file")
        return ""
    return __env


"""Получаем все переменные окружения из .env файла, формат файла:
cat .env ->
KPDA_USER=user123
KPDA_PASSWORD=Qwerty123"""
KPDA_USER = load_env("KPDA_USER")
KPDA_PASSWORD = load_env("KPDA_PASSWORD")
ESS6_USERNAME = load_env("ESS6_USERNAME")
ESS6_PASSWORD = load_env("ESS6_PASSWORD")
ESS6_IP = load_env("ESS6_IP")
ESS6_MSVS_USERNAME = load_env("ESS6_MSVS_USERNAME")
ESS6_MSVS_PASSWORD = load_env("ESS6_MSVS_PASSWORD")
ESS6_MSVS_IP = load_env("ESS6_MSVS_IP")
FSB_LOGIN = load_env("FSB_LOGIN")
FSB_PASSWORD = load_env("FSB_PASSWORD")
BOT_TOKEN = load_env("BOT_TOKEN")
CHAT_ID = load_env("CHAT_ID")
