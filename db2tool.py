#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Boa:App:BoaApp

import os, sys
sys.path.append( sys.path[0] + os.path.sep + 'configd.sqlite3' )
import wx
print 'wx.version():', wx.version()

import dbm

modules ={u'dbm': [1, 'Main frame of Application', u'dbm.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = dbm.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
