from db.session_manager import db_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


def init_db_manager():
    logger.debug("Initializing DB session manager")
    db_manager.init(settings.db.url)
