#!/usr/bin/python
#coding=utf-8
import os
import urllib2

import sys 
def trans(content,src=None,dst=None):
    result=""
    def fanyi(a,b,c):

        """ a == src language; b == dst language; c == content """ 
        
        r = urllib2.Request('http://translate.google.cn/translate_a/t?client=t&text='+urllib2.quote(c.encode('utf-8'))+'&hl=zh-CN&sl='+a+'&tl='+b+'&multires=1&prev=btn&ssel=5&tsel=5&sc=1')
        r.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/17.0.963.79 Chrome/17.0.963.79 Safari/535.11')

        d = urllib2.urlopen(r).read()
        return ' '.join(d.split(',')).split(' ')[0].replace('[[[','').replace('"','')

    
    if isinstance(content,list): # if content include zh-en,ja-zh,zh-ja
        if content[0] in ['zh-en','ja-zh','zh-ja']: # content means : ['zh-en','hello']
            src = content[0].split('-')[0]
            dst = content[0].split('-')[1]
            content = ' '.join(content[1:])
            result = fanyi(src,dst,content)
        elif src == None and dst == None:
            src='en'
            dst='zh'
            content = ' '.join(content)
            result = fanyi(src,dst,content)
    return result


def isen(x):
    for i in x:
        if ord(i) < 128:return True
        else:return False

