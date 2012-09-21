#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
数据库连接
author: cold night
email : wh_linux@126.com
"""

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
        date timestamp           // 加入时间
        """
        cursor.execute("""
                       create table members(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       email VARCHAR,
                       name  VARCHAR,
                       nick VARCHAR,
                       last TIMESTAMP,
                       date TIMESTAMP
                       )
                      """)
        
        """
        创建聊天记录表 history
        key              type              default
        id         INTEGER PRIMARY KEY AUTO_INCREMNT null
        uid        INTEGER       null
        content    TEXT          null
        touid         INTEGER       null             // 0代表所有,其余对应相应的id
        date       TIMESTAMP     (datetime('now', 'localtime'))
        """
        conn.commit()
        cursor.execute("""
            create table history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,
                touid INTEGER DEFAULT 0,
                content TEXT,
                date TIMESTAMP
                )""")
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


now = datetime.now()
def add_member(frm):
    cursor, conn = get_cursor()
    name = frm.getNode()
    email = frm.getStripped()
    sql = 'insert into members(email, name, nick, last, date) VALUES(?,?,?,?,?)'
    cursor.execute(sql, (email, name, name, now, now))
    conn.commit()
    cursor.close()
    conn.close()


def del_member(frm):
    cursor, conn = get_cursor()
    sql = 'delete from members where email=?'
    cursor.execute(sql, (frm.getStripped(),))
    conn.commit()
    cursor.close()
    conn.close()


def edit_member(email, nick = None, last=None):
    cursor, conn = get_cursor()
    if nick:
        sql = 'update members set nick=? where email=?'
        param = (nick, email)
    else:
        sql = 'update members set last=? where email=?'
        param = (now, email)

    cursor.execute(sql, param)
    conn.commit()
    cursor.close()
    conn.close()


def get_member(email = None, uid = None):
    """
    提供email返回id
    提供uid返回email
    """
    cursor, conn = get_cursor()
    if uid:
        sql = 'select email from members where id=?'
        param = (int(uid),)
    elif email:
        sql = 'select id from members where email=?'
        param = (email, )

    cursor.execute(sql, param)
    r = cursor.fetchall()
    result = r[0][0] if len(r) == 1 else None
    cursor.close()
    conn.close()

    return result


def get_members(frm):
    """
    获取所有成员
    """
    cursor, conn = get_cursor()
    email = frm.getStripped()
    sql = 'select email from members where email !=?'
    param = (email, )
    cursor.execute(sql, param)
    r = cursor.fetchall()
    result = [x[0] for x in r]
    cursor.close()
    conn.close()
    return result


def get_nick(email = None, uid = None):
    cursor, conn = get_cursor()
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

    
