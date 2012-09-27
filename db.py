#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#
# Author : cold night
# email  : wh_linux@126.com
# 2012-09-27 13:00
#   + 增加一张表,为status表
#   + 增加对状态操作的函数

import os
import sqlite3
from datetime import datetime
from xmpp import JID

DB_NAME="group.db"

NOW = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _init_table():
    """
    初始化数据库
    """
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        conn.isolation_level = None
        cursor = conn.cursor()
        """
        创建成员数据库 members
        key       type         default
        id     INTEGER PRIMARY KEY AUTO_INCREMENT  null
        email  VARCHAR          null       
        name   VARCHAR          null
        nick   VARCHAR          null 
        last   timestamp         // 最后发言
        lastchange timestamp     // 最后修改
        isonline   INT           // 是否在线(0否, 1 是)
        date timestamp           // 加入时间
        """
        cursor.execute("""
                       create table members(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       email VARCHAR,
                       name  VARCHAR,
                       nick VARCHAR,
                       last TIMESTAMP,
                       lastchange TIMESTAMP,
                       isonline INTEGER DEFAULT 1,
                       date TIMESTAMP
                       )
                      """)

        """
        创建聊天记录表 history
        key              type              default
        id         INTEGER PRIMARY KEY AUTO_INCREMNT null
        frmemail        VARCHAR       null
        content    TEXT          null
        toemail     VARCHAR       null             // all代表所有,其余对应相应的email
        date       TIMESTAMP     (datetime('now', 'localtime'))
        """
        conn.commit()
        cursor.execute("""
            create table history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                frmemail VARCHAR,
                toemail VARCHAR DEFAULT "all",
                content TEXT,
                date TIMESTAMP
                )""")
        conn.commit()

        """
        状态表 status
        `key`               `type`              `default`
        email      VARCHAR                       null
        resource   VARCHAR                      null
        status     INTEGER                       1 // 1在线,0不在线
        statustext VARCHAR                      null
        """
        cursor.execute("""
                       create table status(
                       email VARCHAR,
                       resource VARCHAR,
                       status INTEGER DEFAULT 1,
                       statustext VARCHAR)
                       """
                      )
        conn.commit()
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.isolation_level = None
        cursor = conn.cursor()

    return cursor, conn

def get_cursor():
    """
    获取数据库游标
    """
    return _init_table()


def get_status(email, resource = None):
    if resource:
        sql = 'select status,statustext from status where email=? and resource=?'
        param = (email, resource)
    else:
        sql = 'select status, statustext from status where email=?'
        param = (email,)

    cursor, conn = get_cursor()
    cursor.execute(sql, param)
    r = cursor.fetchall()
    cursor.close()
    conn.close()
    return r


def change_status(frm, status, statustext):
    """改变用户状态"""
    email = "%s@%s" % (frm.node, frm.domain)
    resource = frm.resource
    stat = get_status(email, resource)
    if stat:
        sql = 'update status set status=?,statustext=? where email=? and resource=?'
    else:
        sql = 'insert into status(status, statustext,email, resource) VALUES(?,?,?,?)'
    print type(status)
    param = (status, statustext, email, resource)
    cursor, conn = get_cursor()
    cursor.execute(sql, param)
    conn.commit()
    cursor.close()
    conn.close()


def is_online(email):
    sql = 'select status from status where email=? and status=1'
    cursor, conn = get_cursor()
    cursor.execute(sql,(email,))
    r = True if cursor.fetchall() else False
    return r

now = datetime.now()
def add_member(frm):
    cursor, conn = get_cursor()
    name = frm.node
    email = "%s@%s" % (name, frm.domain)
    if get_member(email = email):return
    sql = 'insert into members(email, name, nick, last, lastchange, date) VALUES(?,?,?,?,?,?)'
    cursor.execute(sql, (email, name, name, now, now, now))
    conn.commit()
    cursor.close()
    conn.close()


def del_member(frm):
    cursor, conn = get_cursor()
    email = "%s@%s" % (frm.node, frm.domain)
    sql = 'delete from members where email=?'
    cursor.execute(sql, (email,))
    conn.commit()
    cursor.close()
    conn.close()


def edit_member(email, nick = None, last=None):
    cursor, conn = get_cursor()
    if nick:
        sql = 'update members set nick=?,lastchange=? where email=?'
        param = (nick, now, email)
    else:
        sql = 'update members set last=? where email=?'
        param = (now, email)

    cursor.execute(sql, param)
    conn.commit()
    cursor.close()
    conn.close()


def get_member(email = None, uid = None, nick = None):
    """
    提供email返回id
    提供uid返回email
    提供nick返回email
    """
    cursor, conn = get_cursor()
    if uid:
        sql = 'select email from members where id=?'
        param = (int(uid),)
    elif email:
        sql = 'select id from members where email=?'
        param = (email, )
    elif nick:
        sql = 'select email from members where nick=?'
        param = (nick, )

    cursor.execute(sql, param)
    r = cursor.fetchall()
    result = r[0][0] if len(r) == 1 else None
    cursor.close()
    conn.close()

    return result


def get_members(email = None):
    """
    获取所有成员
    """
    cursor, conn = get_cursor()
    if email:
        sql = 'select email from members where email !=?'
        param = (email, )
        cursor.execute(sql, param)
        r = cursor.fetchall()
        result = [x[0] for x in r]
    else:
        sql = 'select nick, email from members'
        cursor.execute(sql)
        r = cursor.fetchall()
        result = [dict(nick=v[0], email = v[1]) for v in r]
    cursor.close()
    conn.close()
    return result


def get_nick(email = None, uid = None):
    cursor, conn = get_cursor()
    print email
    if email:
        sql = 'select nick from members where email =?'
        param = (email,)
    elif uid:
        sql = 'select nick from members where id=?'
        param = (uid,)

    cursor.execute(sql, param)
    r = cursor.fetchall()
    result = r[0][0] if len(r) == 1 else email.split('@')[1]
    cursor.close()
    conn.close()
    return result


def add_history(frm, to, content):
    cursor, conn = get_cursor()
    sql = 'insert into history(frmemail, toemail, content, date) VALUES(?,?,?,?)'
    param = (frm, to, content, now)
    cursor.execute(sql, param)
    conn.commit()
    cursor.close()
    conn.close()
