import logging
import logging.config
from config.settings import settings
import yaml
from pathlib import Path
from jinja2 import Template

from config.environment import ENVIRONMENT


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to console logs"""

    # ANSI color codes
    grey = "\x1b[0;37m"
    light_blue = "\x1b[36m"
    yellow = "\x1b[33m"
    red = "\x1b[31;20m"
    blink_red = "\x1b[5m\x1b[1;31m"
    reset = "\x1b[0m"

    format_str = "[%(asctime)s] - %(name)s (%(filename)s:%(lineno)d) - %(levelname)s - %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: light_blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: blink_red + format_str + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_fmt)
        return formatter.format(record)


class DisableLogFilter(logging.Filter):
    """Filter that allows disabling specific loggers"""

    def filter(self, record):
        return False


def setup_logging():
    """
    Setup logging configuration by loading from YAML file.
    This should be called before any app imports.
    """

    conf = Path(__file__).parent / "logging.j2"
    log_file = Path(__file__).parents[1] / "logs/development.log"

    # create logging dir
    try:
        log_file.parent.mkdir(0o700, parents=False, exist_ok=False)
    except FileExistsError:
        pass
    else:
        print(f"Created logs directory @ {log_file.parent.absolute()}")

    # touch log file even if exists
    log_file.touch(mode=0o700, exist_ok=True)

    log_level = settings.LOG_LEVEL

    with open(conf, "r") as f:
        template = Template(f.read())
        config_str = template.render(LOG_LEVEL=log_level, LOG_FILE=log_file)
        config = yaml.safe_load(config_str)

    logging.config.dictConfig(config)

    logging.getLogger(__name__).info(
        f"Logging configured from {conf} for environment: {ENVIRONMENT.value}"
    )
