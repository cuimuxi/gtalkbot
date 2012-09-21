#!/usr/bin/env python
#-*- coding:utf-8 -*-


import logging
from settings import LOGPATH
from settings import LOGLEVEL

def get_logger():
    logger = logging.getLogger()
    fdl = logging.FileHandler(LOGPATH)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fdl.setFormatter(fmt)
    logger.addHandler(fdl)
    logger.setLevel(LOGLEVEL)

    return logger
