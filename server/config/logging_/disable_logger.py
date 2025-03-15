import logging


class DisableLogFilter(logging.Filter):
    def filter(self, record):
        return False
