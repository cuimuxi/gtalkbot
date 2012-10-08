#!/usr/bin/python -u
#-*- coding:utf-8 -*-

import os,sys, time
import subprocess
from pyxmpp.all import JID
from pyxmpp.jabber.client import JabberClient
from pyxmpp.interface import implements
from pyxmpp.interfaces import *
from pyxmpp.streamtls import TLSSettings
from settings import USER
from db import logger



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

    def idle(self):
        self.disconnect()




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
        sys.exit(0)
except OSError, e:
    logger.error("Daemon started failed: %d (%s)", e.errno, e.strerror)
    os.exit(1)

while 1:
    info = {}
    c=Client(JID('cnpytoner@gmail.com/daemon'), 'daemonis$ESZ')
    c.connect()
    try:
        c.loop(1)
    except KeyboardInterrupt:
        c.disconnect()

    status = info.get(USER, False)
    if status:
        time.sleep(10)
    else:
        subprocess.Popen("kill `ps aux | grep 'python bot.py' | grep -v 'grep'| awk '{print $2}'`", stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        subprocess.Popen("python bot.py", stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
