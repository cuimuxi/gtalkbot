#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
# 设置
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

ADMINS = ['coldnight.linux@gmail.com']

USER = 'pythonerclub@gmail.com'

PASSWORD = ''

DEBUG = False

__version__ = '0.3'

PIDPATH = r'logs/clubot.pid'

LOGPATH = r'logs/clubot.log'


DB_NAME="group.db"

# DEBUG:10
# INFO : 20
# WARNING :30
# ERROR : 40
# CRITICAL: 50
LOGLEVEL = 10
