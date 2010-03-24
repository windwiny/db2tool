#-*- coding:utf-8 -*-
'''
Created on 2010-3-24

@author: windwiny
'''

import StringIO

def cprint(sql, data, desc, NL='\n'):
    ds = StringIO.StringIO()
    ds.write(sql)
    ds.write(NL)
    for i in desc:
        ds.write(str(i[0]))
        ds.write('\t')
    ds.write(NL)
    ds.write('--' * 40)
    ds.write(NL)
    for dd in data:
        for i in dd:
            ds.write(str(i))
            ds.write('\t')
        ds.write(NL)
    ds.write(NL)
    return ds.getvalue()

if __name__ == '__main__':
    pass
