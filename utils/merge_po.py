#-*- coding:utf-8 -*-

'''
Created on 2010-2-16

@author: windwiny
'''

import os,sys
import re

if __name__ == '__main__':
    ma = re.compile('''(.*?)(^msgid .*?)((^msgstr .*?)\n\n|(^msgstr .*))''', re.M|re.DOTALL)
    llen = len('\n\n')

    for i in range(len(sys.argv)-3):
        if sys.argv[i] == 'x':
            f1 = open(sys.argv[i+1], 'rb').read().replace('\r\n','\n')#.replace('\r','\n')
            f2 = open(sys.argv[i+2], 'rb').read().replace('\r\n','\n')#.replace('\r','\n')
            f3 = open(sys.argv[i+3] + '.po', 'wb')
            break
    else:
        print 'python  merge_po.py   Ori.pot  Old_Trans.po   NewPoFile'
        sys.exit(0)
    
    transdata = {}
    
    last = 0
    while last <= len(f2):
        m = ma.search(f2, last)
        if  m is None: break
        be,last = m.span()
        _1,_2,_3,_4,_5 = m.groups()
        if _4:
            transdata[_2[6:].strip() ] = _4
        else:
            transdata[_2[6:].strip() ] = _5
        last -= llen
    
    ix=0
    ix2 =0
    last = 0
    while last <= len(f1):
        m = ma.search(f1, last)
        if m is None: break
        be,last = m.span()
        _1,_2,_3,_4,_5 = m.groups()
        try:
            msgstr = transdata[_2[6:].strip()]
            ix2 += 1
        except Exception as ee:
            if _4:
                msgstr = _4
            else:
                msgstr = _5
        last -= llen
        
        f3.write(_1)
        f3.write(_2)
        f3.write(msgstr)
        ix += 1

    print ' from old po get :', len(transdata)
    print ' New po items:', ix, ' Trans:', ix2
    print 'end.'
        
        