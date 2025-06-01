from config.initializers.logger import init_logging
from config.initializers.session_manager import init_db_manager


def initialize_all():
    """Initialize all application components in the correct order"""
    init_logging()
    init_db_manager()

    # init_database()
