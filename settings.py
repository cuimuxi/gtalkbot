#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
# 设置
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

ADMINS = ['coldnight.linux@gmail.com']

USER = 'example@gmail.com'

PASSWORD = 'examplepassword'

DEBUG = False

__version__  = '0.5'

LOGPATH = 'group.log'

PIDPATH = r'pybot.pid'

DAEMONACCOUNT = ('daemon@gmail.com', 'daemonpasswd')

###### 下面设置不生效 #################

PLUGINS = []


# DEBUG:10
# INFO : 20
# WARNING :30
# ERROR : 40
# CRITICAL: 50
LOGLEVEL = 10
