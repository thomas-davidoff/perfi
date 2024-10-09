import logging
from config import CustomFormatter


def get_logger(logger_name: str = "APP_LOGGER", log_level="DEBUG"):

    # Configure loggers
    logging.basicConfig(level=log_level)

    # Apply custom formatter
    for handler in logging.root.handlers:
        handler.setFormatter(CustomFormatter())

    return logging.getLogger(logger_name)
