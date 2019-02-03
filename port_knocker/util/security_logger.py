import sys
import logging

sec_logger = logging.getLogger("security")
sec_logger.setLevel(logging.INFO)
# Remove default handlers
if not sec_logger.handlers:
    formatter = logging.Formatter(fmt="[%(asctime)s %(levelname)s]: %(message)s")
    file_handler = logging.FileHandler('security.log')
    file_handler.setFormatter(formatter)
    sec_logger.addHandler(file_handler)
