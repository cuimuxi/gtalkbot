#!/usr/bin/python -u
#-*- coding:utf-8 -*-
#
# Author : cold night
# Email  : wh_linux@126.com
#
# 守护进程
#
# 2012-10-08 17:00
#    + 创建守护进程


import os, sys, time
import subprocess
from pyxmpp.all import JID
from pyxmpp.jabber.client import JabberClient
from pyxmpp.interface import implements
from pyxmpp.interfaces import *
from pyxmpp.streamtls import TLSSettings
from settings import USER
from settings import PIDPATH, DAEMONACCOUNT
from db import logger


#--- Daemon account client Handler ----------------------------------------------
class  DaemonHandler(object):

    implements(IPresenceHandlersProvider)

    def __init__(self, client):
        self.client = client


    def get_presence_handlers(self):
        return [
            (None, self.presence),
            ("unavailable", self.presence),
            ]

    def presence(self,stanza):
        frm = stanza.get_from()
        email = '%s@%s' % (frm.node, frm.domain)
        t=stanza.get_type()
        if t=="unavailable":
            info[email] = False
        else:
            info[email] = True


class Client(JabberClient):

    def __init__(self, jid, password):
        if not jid.resource:
            jid=JID(jid.node, jid.domain, "Bot")

        tls_settings = TLSSettings(require = True, verify_peer = False)

        JabberClient.__init__(self, jid, password, auth_methods=['sasl:PLAIN'],
                disco_name="Pythoner Club", disco_type="bot",
                tls_settings = tls_settings)
        self.interface_providers = [
            DaemonHandler(self),
        ]

    def roster_updated(self, item = None):
        nodes = []
        if not item:
            for item in self.roster.get_items():
                jid = item.jid
                nodes.append(jid.node)
        else:
            jid = item.jid
            nodes.append(jid.node)
        ujid = JID(USER)
        if ujid.node not in nodes:
            p = Presence(
                to_jid = ujid,
                stanza_type = 'subscribe')
            self.stream.send(p)
        logger.info(nodes)

    def idle(self):
        self.disconnect()


#--- Fork Daemon Process ----------------------------------------------
try:
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
except OSError, e:
    logger.error("Fork #1 failed: %d (%s)", e.errno, e.strerror)
    sys.exit(1)

os.setsid()
os.umask(0)

try:
    pid = os.fork()
    if pid > 0:
        logger.info("Daemon PID %d" , pid)
        pf = open(PIDPATH, 'w')
        pf.write(str(pid))
        pf.close()
        sys.exit(0)
except OSError, e:
    logger.error("Daemon started failed: %d (%s)", e.errno, e.strerror)
    os.exit(1)

#--- Define Daemon ----------------------------------------------
class Daemon():
    PID = 0
    def __init__(self):
        pass

    def run(self):
        logger.debug("check...")
        try:
            logger.debug("Daemon account connect")
            c=Client(JID(DAEMONACCOUNT[0]+'/daemon'), DAEMONACCOUNT[1])
            c.connect()
            c.loop(1)
        except Exception, e:
            logger.waring('Daemon connect failed')
            c.disconnect()

        logger.debug("Daemon account connect done")
        status = info.get(USER, False)
        if status:
            logger.debug("Bot is online")
            time.sleep(30)
        else:
            subprocess.Popen("kill -9 `ps aux | grep 'python bot.py' | grep -v 'grep'| awk '{print $2}'`", stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            logger.info('starting bot...')
            r = subprocess.Popen("python bot.py", stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            err = r.stderr.read()
            if  err:
                logger.warning('Start bot error: %s', err)
            else:
                logger.info('done')
                logger.info('bot started with pid %d' % r.pid)
                self.PID = r.pid
            time.sleep(30)

    def __del__(self):
        if self.PID > 0:
            logger.info("Stop Bot..")
            os.kill(self.PID, 9)
            logger.info("Done")
        logger.info("Stop Bot Daemon")

########## Run Daemon ###############################
logger.info('checked started')
d = Daemon()
while 1:
    info = {}
    d.run()
