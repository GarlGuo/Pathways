import logging
from addr_info import *


class Logger:

    def __init__(self, name) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='%(levelname)s | %(asctime)s | %(message)s')
        fh = logging.FileHandler(pathways_log_addr)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    
    def log_info(self, info):
        self.logger.info(info)

    def log_warning(self, warning):
        self.logger.warn(warning)

    def log_exception(self, e):
        self.logger.exception(e)


pathways_system_logger = Logger("Pathways System Log")
