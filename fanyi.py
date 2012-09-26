#!/usr/bin/python
#coding=utf-8
import os
import urllib2

def trans(content,src=None,dst=None):
    if src == None:src='en'
    if dst == None:dst='zh-CN'
    if isinstance(content,list):content=' '.join(content)
    r = urllib2.Request('http://translate.google.cn/translate_a/t?client=t&text='+urllib2.quote(content)+'&hl=zh-CN&sl='+src+'&tl='+dst+'&multires=1&prev=btn&ssel=5&tsel=5&sc=1')
    r.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/17.0.963.79 Chrome/17.0.963.79 Safari/535.11')
    d = urllib2.urlopen(r).read()
    return ' '.join(d.split(',')).split(' ')[0].replace('[[[','').replace('"','')

#def tq(
def isen(x):
    for i in x:
        if ord(i) < 128:return True
        else:return False
