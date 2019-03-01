import sys
import logging
from port_knocker.config.config import Config

sec_logger = logging.getLogger("security")
sec_logger.setLevel(logging.INFO)
if not sec_logger.handlers:
    formatter = logging.Formatter(fmt="[%(asctime)s %(levelname)s]: %(message)s")
    file_handler = logging.FileHandler(Config.LOGGER_FNAME)
    file_handler.setFormatter(formatter)
    sec_logger.addHandler(file_handler)
