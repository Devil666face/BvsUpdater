from loguru import logger
from functools import wraps

logger.add(
    "updater.log",
    retention="7 days",
    colorize=True,
    backtrace=True,
    diagnose=True,
    enqueue=True,
)


def log_obj(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        message = "; ".join([f"{key}:{self.__dict__[key]}" for key in self.__dict__])
        logger.debug(message)
        return result

    return wrapper
