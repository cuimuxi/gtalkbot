#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# 生成命令
#
# Author : cold night
# email  : wh_linux@126.com
# 2012-09-27 13:38
#   + 增加$list 时用户是否在线
#   + 增加@功能
#   + 增加@<>为首发私信
#   + 增加查看命令历史
#   + 增加贴代码
#   + 命令增加缓存功能
# 2012-09-28 08:52
#   + 命令生成增加缓存操作


import re
import time
from db import get_members
from db import get_nick, get_member
from db import edit_member
from db import add_history
from db import is_online
from db import get_history
from pyxmpp.all import Message
from pyxmpp.all import JID
from pyxmpp.all import Presence
from fanyi import Complex
from settings import DEBUG
from settings import __version__
from settings import USER



get_email = lambda frm:"%s@%s" % (frm.node, frm.domain)


def http_helper(url, param = None, callback=None):
    import urllib, urllib2
    if param:
        data = urllib.urlencode(param)
        req =urllib2.Request(url,data)
    else:
        req = urllib2.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1")
    res = urllib2.urlopen(req)
    
    if callback:
        result = callback(res)
    else:
        result =  res.read()
    return result


def _get_code_types():
    """获取贴代码支持的类型"""
    purl = "http://paste.ubuntu.org.cn/"
    def handle(res):
        r = re.compile(r'<option\s+value="(.*?)".*?>(.*?)</option>')
        result = []
        for line in res.readlines():
            if '<option' in line:
                t = {}
                t['key'], t['value'] = r.findall(line)[0]
                result.append(t)
        return result
    result = http_helper(purl, callback=handle)
    import string
    t = string.Template("""$key : $value  """)
    r = [t.substitute(v) for v in result]
    result = '\n'.join(r)
    return result


def paste_code(poster, typ, codes):
    param = {'class':typ}
    param.update(poster=poster, code2 = codes, paste="发送")
    purl = "http://paste.ubuntu.org.cn/"

    get_url = lambda res:res.url
    url = http_helper(purl, param, get_url)
    if url == purl:
        return False
    else:
        return url


def _add_commends(codes, typ, nick):
    commends = {"actionscript": "// ", "actionscript-french" : "// ",
                "ada" : "-- ","apache" : "# ","applescript" : "- ",
                "asm" : "; ","asp" : "// ",  "autoit" : "; ","bash" : "# ",
                "blitzbasic" : "' ","c ":"// ","c_mac" : "// ",
                "cpp" :" // ","csharp" : "// ","css" : ["/* ", " */"],
                "freebasic" : "' ","html4strict" : ["<!-- ", " -->"],
                "java" : "//  ","java5" : "//  ","javascript" : "//  ",
                "lisp" : ";; ","lua" : "--  ","mysql" : "--  ",
                "objc" : "// ","perl" : "# ","php" : "// ",
                "php-brief" : "//  ","python" : "# ","qbasic" : "' ",
                "robots" : "# ","ruby" : "#","sql" : "--  ",
                "tsql" : "-- ","vb" : "'  ","vbnet" : "//  ", "xml":["<!--", "-->"]}
    codes  = list(codes)
    if codes[0].startswith('#!'):
        symbol = commends.get(typ, '# ')
        if isinstance(symbol, list):
            c = "%s\n%s 由Pythoner Club 的 %s 提交\n 欢迎加入我们讨论技术: \
                \n\t使用gtalk添加%s %s\n" % (codes[0],symbol[0], nick, USER, symbol[1])
        else:
            c = "%s\n%s 由Pythoner Club 的 %s 提交\n%s 欢迎加入我们讨论技术: \
                \n%s\t使用gtalk添加%s\n" % (codes[0],symbol, nick, symbol, symbol, USER)
        codes[0] = c
    else:
        symbol = commends.get(typ, '// ')
        if isinstance(symbol, list):
            c = "%s 由Pythoner Club 的 %s 提交\n 欢迎加入我们讨论技术: \
                \n\t使用gtalk添加%s %s\n" % (symbol[0], nick, USER, symbol[1])
        else:
            c = "%s 由Pythoner Club 的 %s 提交\n%s 欢迎加入我们讨论技术: \
                \n%s\t使用gtalk添加%s\n" % (symbol, nick, symbol, symbol, USER)
        codes.insert(0, c)

    return codes



class CommandHandler():
    """
        生成命令
        命令对应着方法
        比如敲入 -list 则对应list方法
        命令具有统一接收stanza固定参数和变参*args,
        需要参数自行从kargs里提取
        所有命令须返回Message/Presence的实例或实例列表
    """
    _cache = {}
    def list(self, stanza, *args):
        """列出所有成员"""
        frm = stanza.get_from()
        femail = "%s@%s" % (frm.node, frm.domain)
        members = get_members()
        body = []
        for m in members:
            email = m.get('email')
            r = '%s <%s>' % (m.get('nick'), m.get('email'))
            if email == femail:
                r = '** ' + r
            elif is_online(email):
                r = ' * ' + r
            else:
                r = '  ' + r
            body.append(r)
        body = sorted(body, key = lambda k:k[1], reverse=True)
        body.insert(0, 'Pythoner Club 所有成员(** 表示你自己, * 表示在线):')
        return self._send_cmd_result(stanza, '\n'.join(body))

    def trans(self, stanza, *args):
        """中日英翻译,默认英-汉翻译,eg $trans zh-en 中文,$trans ja-zh 死ぬ行く"""
        trans = Complex()
        return self._send_cmd_result(stanza, trans.trans([x for x in args]))

    def tq(self, stanza, *args):
        """指定城市获取天气, eg. $tq 广州"""
        tq = Complex()
        return self._send_cmd_result(stanza, tq.tq(''.join([x for x in args])))

    def msgto(self, stanza, *args):
        """单独给某用户发消息 eg $msgto nick hello(给nick发送hello) 也可以使用@<nick> 消息"""
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
            r = edit_member(email, nick = nick)
            if r:
                body = "%s 更改昵称为 %s" % (oldnick, nick)
                m = send_all_msg(stanza, body)
            else:
                m = self._send_cmd_result(stanza, '昵称已存在')
        else:
            m = self.help(stanza, 'nick')


        return m


    def code(self, stanza, *args):
        """<type> <code> 贴代码,可以使用$codetype查看允许的代码类型"""
        if len(args) > 1:
            email = get_email(stanza.get_from())
            nick = get_nick(email)
            typ = args[0]
            codes = _add_commends(args[1:], typ, nick)
            codes = ''.join(codes[0:2]) + ' '.join(codes[2:])
            poster = "Pythoner Club: %s" % nick
            r = paste_code(poster,typ, codes)
            if r:
                m = send_all_msg(stanza, r)
                mc = self._send_cmd_result(stanza, r)
                m.append(mc)
            else:
                m = self._send_cmd_result(stanza, 'something wrong')
        else:
            m = self.help(stanza, 'code')
        return m




    def codetypes(self, stanza, *args):
        """返回有效的贴代码的类型"""
        if self._cache.get('typs'):
            body = self._cache.get('typs')
        else:
            body = _get_code_types()
            self._cache.update(typs = body)
        return self._send_cmd_result(stanza, body)


    def invite(self, stanza, *args):
        """邀请好友加入 eg. $invite <yourfirendemail>"""
        if len(args) >= 1:
            to = args[0]
            p1 = Presence(from_jid = stanza.get_to(),
                         to_jid = JID(to),
                         stanza_type = 'subscribe')
            p = Presence(from_jid = stanza.get_to(),
                         to_jid = JID(to),
                         stanza_type = 'subscribed')
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
            body = sorted(body, key=lambda k:k[1])
            body = '\n'.join(body)
        return self._send_cmd_result(stanza, body)


    def history(self, stanza, *args):
        """<from> <index> <size> 显示聊天历史"""
        email = get_email(stanza.get_from())
        if args:
            return self._send_cmd_result(stanza, get_history(email, *args))
        else:
            return self._send_cmd_result(stanza, get_history(email))


    def version(self, stanza, *args):
        """显示版本信息"""
        author = [
                    'cold night(wh_linux@126.com)',
                    'eleven.i386(eleven.i386@gmail.com)',
                 ]
        body = "Version %s\nAuthors\n\t%s\n" % (__version__, '\n\t'.join(author))
        return self._send_cmd_result(stanza, body)


    def _set_cache(self, key, data, expires = None):
        """设置缓存 expires(秒) 设置过期时间None为永不过期"""
        if expires:
            self._cache[key] = {}
            self._cache[key]['data'] = data
            self._cache[key]['expires'] = expires
            self._cache[key]['time'] = time.time()
        else:
            self._cache[key]['data'] = data



    def _get_cache(self, key):
        """获取缓存"""
        if not self._cache.has_key(key): return None
        if self._cache[key].has_key('expires'):
            expires = self._cache[key]['expires']
            time = self._cache[key]['time']
            if (time.time() - time) > expires:
                return None
            else:
                return self._cache[key].get('data')
        else:
            return self._cache[key].get('data')



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
        splitbody = cmd.split('\n')
        if len(splitbody) >= 2:
            cmdline = splitbody[0]
            body = '\n'.join(splitbody[1:])
        else:
            if len(splitbody) == 1:
                cmdline = splitbody[0]
                body = None
            else:
                cmdline,body = splitbody

        for i, v in enumerate(cmdline.split(' ')):
            if i == 0:
                c = v
            else:
                args.append(v)
        if body:args.append(body)
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
        r = re.findall(r'@<(.*?)>', body)
        mem = [get_member(nick=n) for n in r if get_member(nick = n)]
        if mem:
            if body.startswith('@<'):
                b = re.sub(r'^@<.*?>', '', body)
                return send_to_msg(stanza, mem[0], b)
            b = '%s 提到了你说: %s' % (nick, body)
            ml = [send_to_msg(stanza, to, b) for to in mem]
            ms += ml
    elif body.strip() == 'help':
        return run_cmd('help', stanza)
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
