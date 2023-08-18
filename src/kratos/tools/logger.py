import logging
from decouple import config
import os
from pathlib import Path


class Logger():
    formatter = logging.Formatter('%(asctime)s | %(name)s - [%(levelname)s] | %(message)s \n')

    def __init__(self, file_log=True):
        self.file_log = file_log
        self.logger = self.__init_logger()

    def debug(self, message, item=None):
        self.logger.debug(message)

    def info(self, message, item=None):
        self.logger.info(message)

    def warning(self, message, item=None):
        self.logger.warning(message)

    def error(self, message, item=None):
        self.logger.error(message)

    def __init_logger(self):
        logger = logging.getLogger('KRATOS ')
        logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(self.formatter)
        logger.addHandler(sh)

        if self.file_log:
            Path(config('LOG_DIR')).mkdir(exist_ok=True)
            if not os.path.exists(config('LOG_DIR')+ "/" + config('LOG_FILE')):
                fh = logging.FileHandler(filename=config('LOG_DIR')+ "/" + config('LOG_FILE'), mode='w', encoding='utf-8')
            else:
                fh = logging.FileHandler(filename=config('LOG_DIR')+ "/" + config('LOG_FILE'), mode='a', encoding='utf-8')

            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.formatter)
            logger.addHandler(fh)

        return logger