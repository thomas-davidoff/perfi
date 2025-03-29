from config.initializers.logger import init_logging
import logging


def initialize_all():
    """Initialize all application components in the correct order"""
    init_logging()

    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message")
    logger.info("Hello")
    logger.warning("Hello")
    logger.error("Hello")
    logger.critical("Hello")

    # init_database()
