#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# 生成命令

from db import get_members
from db import get_nick, get_member
from db import edit_member
from db import add_history
from pyxmpp.all import Message
from pyxmpp.all import JID
from pyxmpp.all import Presence
from fanyi import trans
from fanyi import isen
from settings import DEBUG



def http_helper(url, param):
    import urllib, urllib2
    data = urllib.urlencode(param)
    req =urllib2.Request(url,data)
    req.add_header("User-Agent", "Mozilla/5.0+(compatible;+Googlebot/2.1;++http://www.google.com/bot.html)")
    fd = urllib2.urlopen(req)
    result =  fd.read()
    return result



class CommandHandler():
    """
        生成命令
        命令对应着方法
        比如敲入 -list 则对应list方法
        命令具有统一接收stanza固定参数和变参**kargs,
        需要参数自行从kargs里提取
        所有命令须返回Message/Presence的实例
    """
    def list(self, stanza, *args):
        """列出所有成员"""
        members = get_members()
        body = []
        for m in members:
            r = '%s <%s>' % (m.get('nick'), m.get('email'))
            body.append(r)

        return self._send_cmd_result(stanza, '\n'.join(body))
        
    def trans(self, stanza, *args):
        """英汉翻译 e.g $trans en zh-CN hello/$trans zh-Cn en 你好"""
        return self._send_cmd_result(stanza,trans([x for x in args]))

    def msgto(self, stanza, *args):
        """单独给某用户发消息 eg $msgto nick hello(给nick发送hello) \n\t\t也可以使用@<nick> 消息"""
        if len(args) > 1:
            nick = args[0]
            receiver = get_member(nick = nick)
            body = ' '.join(args[1:])
            if not receiver:
                m  = self._send_cmd_result(stanza, "%s 用户不存在" % nick)
            else:
                m = send_to_msg(stanza, receiver, body)
        else:
            m = self.help(stanza, 'mgsto')

        return m


    def nick(self, stanza, *args):
        """更改昵称 eg. $nick yournewnickname"""
        if len(args) >= 1:
            nick = ' '.join(args[0:])
            frm = stanza.get_from()
            email = "%s@%s" % (frm.node, frm.domain)
            oldnick = get_nick(email)
            edit_member(email, nick = nick)
            body = "%s 更改昵称为 %s" % (oldnick, nick)
            m = send_all_msg(stanza, body)
        else:
            m = self.help(stanza, 'nick')


        return m

    def invite(self, stanza, *args):
        """邀请好友加入 eg. $invite <yourfirendemail>"""
        if len(args) >= 1:
            to = args[0]
            p1 = Presence(from_jid = stanza.get_to(),
                         to_jid = JID(to),
                         stanza_type = 'subscribe')
            #stanza.stream.send(p)
            p = Presence(from_jid = stanza.get_to(),
                         to_jid = JID(to),
                         stanza_type = 'subscribed')
            #m = stanza.stream.send(p)
            return [p,p1]
        else:
            return self.help(stanza, 'invite')

    def help(self, stanza, *args):
        """显示帮助"""
        if args:
            func = self._get_cmd(args[0])
            if func:
                body ="$%s : %s" % (args[0], func.__doc__)
            else:
                body = "$%s : command unknow" % args[0]
        else:
            body = []
            funcs = self._get_cmd()
            for f in funcs:
                r = "$%s  %s" % (f.get('name'), f.get('func').__doc__)
                body.append(r)
            body = '\n'.join(body)
        return self._send_cmd_result(stanza, body)

    def version(self, stanza, *args):
        """显示版本信息"""
        author = ['cold night(wh_linux@126.com)']
        body = "Version 0.1\n Author \n %s\n" % '\n'.join(author)
        return self._send_cmd_result(stanza, body)

    @classmethod
    def _send_cmd_result(cls, stanza, body):
        """返回命令结果"""
        frm = stanza.get_from()
        email = '%s@%s' % (frm.node, frm.domain)
        message = send_msg(stanza, email, body)
        #stanza.stream.send(message)
        return message


    @classmethod
    def _get_cmd(cls, name = None):
        if name:
            return cls.__dict__.get(name)
        else:
            r = [{'name':k, 'func':v} for k, v in cls.__dict__.items() if not k.startswith('_')]
            return r


    def __getattr__(self, name):
        return self.help

    @classmethod
    def _run_cmd(cls,cmd, stanza):
        """获取命令"""
        args = []
        c = ''
        for i, v in enumerate(cmd.split(' ')):
            if i == 0:
                c = v
            else:
                args.append(v)
        if DEBUG:
            m = cls.__dict__.get(c)(cls, stanza, *args)
        else:
            try:
                m = cls.__dict__.get(c)(cls, stanza, *args)
            except Exception as e:
                print 'Error', e.message
                m = cls.__dict__.get('help')(cls, stanza, c)

        return m


class AdminCMDHandle(CommandHandler):
    """管理员命令"""
    def log(self, stanza, *args):
        """查看日志"""

run_cmd = CommandHandler._run_cmd



def send_command(stanza, body):
    cmd = body[1:]
    m = run_cmd(cmd, stanza)
    return m


def send_msg(stanza, to_email, body):
    m=Message(
        to_jid=JID(to_email),
        #from_jid=stanza.get_to(),
        stanza_type=stanza.get_type(),
        body=body)
    #stanza.stream.send(m)
    return m

def send_all_msg(stanza, body):
    frm = stanza.get_from()
    email = '%s@%s' % (frm.node, frm.domain)
    nick = get_nick(email)
    add_history(email, 'all', body)
    tos = get_members(email)
    ms = []
    if '@' in body:
        import re
        r = re.findall(r'@<(.*?)>', body)
        mem = [get_member(nick=n) for n in r if get_member(nick = n)]
        if mem:
            if body.startswith('@'):
                b = re.sub(r'^@<.*?>', '', body)
                return send_to_msg(stanza, mem[0], b)
            b = '%s 提到了你说: %s' % (nick, body)
            ml = [send_to_msg(stanza, to, b) for to in mem]
            ms += ml
    body = "[%s] %s" % (nick, body)
    for to in tos:
        m = send_msg(stanza, to, body)
        ms.append(m)
    return ms


def send_to_msg(stanza, to, body):
    frm = stanza.get_from()
    email = '%s@%s' % (frm.node, frm.domain)
    nick = get_nick(email)
    add_history(email, to, body)
    body = "[%s 悄悄对你说] %s" % (nick, body)
    return send_msg(stanza, to, body)
