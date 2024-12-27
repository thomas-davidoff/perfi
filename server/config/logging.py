import logging
from colorama import Fore, Style


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    # TODO: Fix pathname to filename, but from root of project, not system.
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(pathname)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: Fore.CYAN + format + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + format + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
