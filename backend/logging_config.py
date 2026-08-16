import logging
from .config import LOG_FILE

logger = logging.getLogger("pyguard_v2")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

app_logger = logger
