import requests
import urllib3
from typing import (
    Tuple,
    List,
)
from loguru import logger
from handler.env import (
    BOT_TOKEN,
    CHAT_ID,
)
from functools import wraps


logger.add(
    "updater.log",
    retention="7 days",
    format="{time:DD.MM HH:mm:ss}|{level}|{message}",
    # colorize=True,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    encoding="utf-8",
)

REPLACE = {
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "ERROR": "❗️",
    "WARNING": "⚠️",
    "DEBUG": "🤖",
}


def string_week_day(day_of_week: int) -> str:
    days = [
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    ]
    return days[day_of_week]


class CustomLogger:
    def __init__(self, logfile_name="updater.log"):
        self.logfile_name = logfile_name
        pass

    def send_message(self, message):
        try:
            requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
            )
        except requests.exceptions.ConnectionError as error:
            logger.exception(error)
        except urllib3.exceptions.MaxRetryError as error:
            logger.exception(error)
        except requests.exceptions.ProxyError as error:
            logger.exception("Telegram proxy error")

    def __get_message(self) -> str:
        with open(self.logfile_name) as file:
            try:
                return file.readlines()[-1]
            except IndexError as error:
                pass

    def __replace_log_level(self, message: str) -> str:
        message_temp = message
        for key in REPLACE:
            message_temp = message_temp.replace(key, REPLACE[key])
        return self.__markdown_in_message(message_temp)

    def __markdown_in_message(self, message: str) -> str:
        splited_message = message.split("|")
        if len(splited_message) >= 3:
            return f"{splited_message[1]} ***{splited_message[0]}***\n`{splited_message[2]}`"
        return message

    def __exception(self, message):
        return f"❌ ***Exception***\n`{message}`"

    def telegram_handler(func):
        @wraps(func)
        def telegram_message(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            log_message = self.__get_message()
            if func.__name__ == "exception":
                self.send_message(message=self.__exception(log_message))
            else:
                self.send_message(message=self.__replace_log_level(log_message))
            return result

        return telegram_message

    @telegram_handler
    def info(self, message):
        logger.info(message)

    @telegram_handler
    def warning(self, message):
        logger.warning(message)

    @telegram_handler
    def exception(self, message):
        logger.exception(message)

    @telegram_handler
    def success(self, message):
        logger.success(message)

    @telegram_handler
    def error(self, message):
        logger.error(message)

    def table_size(self, size_file_list=List[Tuple[str, str]]):
        message_for_join = [f"`{line[0]} -> {line[1]}`" for line in size_file_list]
        self.send_message(message="\n".join(message_for_join))

    def debug(self, message):
        logger.debug(message)


tglogger = CustomLogger()


def log_obj(func):
    @wraps(func)
    def log(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        message = "; ".join([f"{key}:{self.__dict__[key]}" for key in self.__dict__])
        logger.debug(message)
        return result

    return log
