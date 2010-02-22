#-*- coding:utf-8 -*-

import os, sys
import gettext
gettext.install('dbtool', 'locale', True)

if len(sys.argv)>1:
    fn=sys.argv[1]
else:
    import wx
    app=wx.PySimpleApp(False)
    dlg = wx.TextEntryDialog(None,'input file:','?','dbM.py',style=wx.OK)
    dlg.ShowModal()
    fn = dlg.GetValue()
    dlg.Destroy()
f = open(fn, 'r').readlines()

ks = set()
for  j in range(len(f)):
    for i in range(len(f[j])):
        if ord(f[j][i]) > 127:
            ks.add((j + 1, i + 1, f[j][i], ord(f[j][i])))

if ks:
    print 'File',fn,'Line count:', len(f), 'Lines: ', ks
    #for i in ks:
    #    print f[i[0]]
else:
    print 'no Not Ascii char'

    
