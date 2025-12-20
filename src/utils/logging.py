import logging
import sys

from src.models.config import Config


class CustomFormatter(logging.Formatter):
    blue = "\x1b[34m"
    grey = "\x1b[38;5;250m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[91;1;4m"
    reset = "\x1b[0m"
    FORMATS = None

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None):
        self._set_formats(fmt)
        self.style = style
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults)

    def _set_formats(self, fmt):
        if self.FORMATS is None:
            self.FORMATS = {
                logging.DEBUG: self.blue + fmt + self.reset,
                logging.INFO: self.grey + fmt + self.reset,
                logging.WARNING: self.yellow + fmt + self.reset,
                logging.ERROR: self.red + fmt + self.reset,
                logging.CRITICAL: self.bold_red + fmt + self.reset,
            }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=self.datefmt, style=self.style)
        return formatter.format(record)


class Logger:
    _instance = None
    FORMAT = "{levelname:<8}: {asctime}.{msecs:03g} -> {message}"

    def __init__(self) -> None:
        self.logger = logging.getLogger("Wordsworth")
        self.logger.setLevel(Config.LOG_LEVEL)
        self.log_format = CustomFormatter(fmt=self.FORMAT, datefmt="%H:%M:%S", style="{")
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(self.log_format)
        self.logger.addHandler(console)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls):
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warn(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def crit(self, msg: str) -> None:
        self.logger.critical(msg)
