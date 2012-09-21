#!/usr/bin/env python
#-*- coding:utf-8 -*_
"""
    群插件
    author  : cold night
    email   : wh_linux@126.com
"""

from settings import PLUGINS
from common import get_logger



ALLPLUGINS = {
    'list':'list_all_user',
    'help':'display_help',
    'search':'search',
    'wiki':'wiki'
}


def list_all_user():
    pass

def display_help():
    pass

def search():
    pass

def wike():
    pass


def get_plugins():
    """
        获取有效插件
    """
    logger = get_logger()
    result = {}
    for p in PLUGINS:
        ft = ALLPLUGINS.get(p)
        if not ft:
            logger.warning('plugin %s not exists, skip', p)
            continue
        try:
            func = eval(ft)
        except Exception as e:
            logger.warning('plugin %s not exists handler', p)
            continue

        result[p] = func

    return result
