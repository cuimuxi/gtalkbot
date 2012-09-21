#!/usr/bin/env python
#-*- coding:utf-8
"""
    gtalk机器人,用于支持群组
    author : cold night
    email  : wh_linux@126.com
"""

import xmpp
import subprocess
from settings import USER
from settings import PASSWORD
from settings import DEBUG
from settings import ADMINS
from common import get_logger
from db import add_member, del_member, edit_member, get_member
from db import get_members, get_nick


logger = get_logger()

def send_all_msg(cl,frm ,  message):
    m = "[%s]: %s" % (get_nick(frm.getStripped()) , message)
    tos = get_members(frm)
    for to in tos:
        cl.send(xmpp.Message(xmpp.JID(to), m))
    



def messageHandle(cl, message_node):
    """
    """
    frm = message_node.getFrom()
    from_user = frm.getStripped()
    edit_member(from_user)
    cmd =message_node.getBody()
    if not cmd : return
    cmd = str(cmd)
    if cmd.startswith('-'):
        cmd = cmd[1:0]
        if from_user in ADMINS:
            process = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            message = process.stdout.read()
            if message == "":
                message = process.stderr.read()
            else:
                message = "Access denied!\n"
    

            cl.send(xmpp.Message(message_node.getFrom(), message))
    else:
        send_all_msg(cl, frm, cmd)


def presenceHandle(cl, presence):
    typ = presence.getType()
    frm_user = presence.getFrom()
    if typ == 'subscribe' or typ == 'subscribed':
        cl.send(xmpp.Presence(to = frm_user, typ='subscribe'))
        cl.send(xmpp.Presence(to = frm_user, typ='subscribed'))
        if not get_member(frm_user.getStripped()):
            add_member(frm_user)
            logger.info('%s add in the group', frm_user.getStripped())
    elif typ == 'unsubscribe' or typ == 'unsubscribed':
        cl.send(xmpp.Presence(to = frm_user, typ='unsubscribe'))
        cl.send(xmpp.Presence(to = frm_user, typ='unsubscribed'))
        del_member(frm_user)
        logger.info('%s leave the group', frm_user.getStripped())
    else:
        logger.warning('%s type is not support', typ)


jid = xmpp.JID(USER)

cl = xmpp.Client(jid.getDomain(), debug = DEBUG)
cl.connect()
r = cl.auth(jid.getNode(), PASSWORD, 'BOT')
if r != 'sasl':
    logger.fatal("Login Fatal")
cl.RegisterHandler('message', messageHandle)
cl.RegisterHandler('presence', presenceHandle)

status = xmpp.Presence(status="Pythoner 俱乐部")
cl.sendInitPresence()
cl.send(status)
logger.info('Online with user %s', USER)
while cl.Process(1):
    pass
