# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

import logging
import os
import time
from logging import handlers

PATH = os.getcwd()
LOG_FOLDER = os.path.join(PATH, 'Log')
DATEFMT = '%Y-%m-%d %H:%M:%S'

MAPPING = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0,
}


def makedir(abspath):

    if not os.path.exists(abspath):
        os.makedirs(abspath)
    return


class Logger(object):
    """configure for logger"""
    def __init__(self, log_name, file_level, size=1024*1024, count=10):
        """init for logger"""
        self.logger = logging.getLogger(log_name)
        self.log_name = '{}.log'.format(log_name)
        self.log_file = os.path.join(LOG_FOLDER, self.log_name)
        makedir(LOG_FOLDER)
        self.config(self.log_file, file_level, size, count)

    def config(self, log_file, file_level, size, count):
        """set config for logger"""
        self.logger.setLevel(MAPPING[file_level])
        if not self.logger.handlers:
            self.fh = handlers.RotatingFileHandler(log_file, mode='a+',
                                                   maxBytes=size, backupCount=count, encoding='utf-8')
            self.fh.setLevel(MAPPING[file_level])


            formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", datefmt=DATEFMT)

            self.fh.setFormatter(formatter)

            self.logger.addHandler(self.fh)

    def debug(self, msg):
        if type(msg) == str:
            try:
                msg = msg.decode('utf8')
            except Exception as e:
                print msg
                print e
        if msg is not None:
            self.logger.debug(msg)

    def info(self, msg):
        if type(msg) == str:
            try:
                msg = msg.decode('utf8')
            except Exception as e:
                print msg
                print e
        if msg is not None:
            self.logger.info(msg)

    def warning(self, msg):
        if type(msg) == str:
            try:
                msg = msg.decode('utf8')
            except Exception as e:
                print msg
                print e
        if msg is not None:
            self.logger.warning(msg)

    def error(self, msg):
        if type(msg) == str:
            try:
                msg = msg.decode('utf8')
            except Exception as e:
                print msg
                print e
        if msg is not None:
            self.logger.error(msg)

    def critical(self, msg):
        if type(msg) == str:
            try:
                msg = msg.decode('utf8')
            except Exception as e:
                print msg
                print e
        if msg is not None:
            self.logger.critical(msg)

    def traceback(self):
        """Log exception traceback to logger"""
        import sys
        import traceback
        info = sys.exc_info()
        lines = traceback.format_exception(info[0], info[1], info[2])
        for line in lines:
            elines = line.splitlines()
            for eline in elines:
                eline.strip()
                self.logger.critical('----{}'.format(eline.strip()))

if __name__ == "__main__":
    """Test code"""

    logger = Logger('crawler', 'INFO')
    for i in range(10):
        logger.info('error {}'.format(i))
        logger.warning('warning {}'.format(i))
    time.sleep(2)
    try:
        1/0
    except Exception, e:
        logger.traceback()
    logger.critical('die!!!!!!')




