import logging


COMMON_PREFIX = "[%(asctime)s] - %(name)s - %(levelname)s - "
DATE_FMT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    red = "\x1b[31;20m"
    yellow = "\x1b[33m"
    grey = "\x1b[0;37m"
    light_blue = "\x1b[36m"
    blink_red = "\x1b[5m\x1b[1;31m"
    reset = "\x1b[0m"

    format = COMMON_PREFIX + ("%(message)s (%(filename)s:%(lineno)d)")

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: light_blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: blink_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=DATE_FMT)
        return formatter.format(record)
