#Boa:Frame:mainframe
#-*- coding:utf-8 -*-

#
# python source file coding : utf-8
#  gettext.install : unicode
# wxpython control text , label, message: unicode
# log file : system locale
# sql, table, schema, etc : system locale
#


import os, sys
import locale
import sqlite3
import tempfile
import re
import time
import threading
import random
import subprocess
import StringIO
import base64
import zlib
import gettext
import config2
import sqld
import sqlformatter

try:
    import wx
    import wx.grid
    import wx.stc
    import wx.lib.pubsub
    import wx.lib.wordwrap
except:
    print '''  Not import wx '''
    sys.exit(2)

import stc2

try:
    import DB2
except:
    print '''  Not import PyDB2, python setup.py install -c mingw32'''
    sys.exit(3)

import images   # my images
pgname = 'db2tool'

def create(parent):
    return dbM(parent)

[wxID_DBM, wxID_DBMBTNCALLPROC, wxID_DBMBTNCODERELOAD, wxID_DBMBTNCODESAVE, 
 wxID_DBMBTNCOMMIT, wxID_DBMBTNCOMPARE, wxID_DBMBTNDB2HELP, 
 wxID_DBMBTNDISCONNECTALL, wxID_DBMBTNEXECPYTHON, wxID_DBMBTNEXECSQLS, 
 wxID_DBMBTNEXECSQLSINGLE, wxID_DBMBTNEXPORTDDL, wxID_DBMBTNFONT, 
 wxID_DBMBTNFORMATSPACE, wxID_DBMBTNLISTPROCS, wxID_DBMBTNPYTHONRELOAD, 
 wxID_DBMBTNPYTHONSAVE, wxID_DBMBTNREFRESHDB, wxID_DBMBTNREFRESHDBS, 
 wxID_DBMBTNROLLBACK, wxID_DBMBTNSAVEDBS, wxID_DBMBTNSQLRELOAD, 
 wxID_DBMBTNSQLSAVE, wxID_DBMBUTTON4, wxID_DBMCHKLINK, wxID_DBMCHKLOGSQLS, 
 wxID_DBMCHKSHOWSQLSRES, wxID_DBMCHOICECONNECTEDDBNAMES, wxID_DBMCHOICEDB1, 
 wxID_DBMCHOICEDB2, wxID_DBMCHOICESCHEMA1, wxID_DBMCHOICESCHEMA2, 
 wxID_DBMCHOICETYPE, wxID_DBMGRIDDBS, wxID_DBMGRIDM11, wxID_DBMGRIDM12, 
 wxID_DBMGRIDM13, wxID_DBMGRIDM21, wxID_DBMGRIDM22, wxID_DBMGRIDM23, 
 wxID_DBMLSTPROCEDURES, wxID_DBMLSTT1, wxID_DBMLSTT2, wxID_DBMNBDBS, 
 wxID_DBMNBM1, wxID_DBMNBM2, wxID_DBMNBMAINFRAME, wxID_DBMNBRESULT, 
 wxID_DBMPANELM1, wxID_DBMPANELM2, wxID_DBMPCODESNIPPET, wxID_DBMPCONNECT, 
 wxID_DBMPEXECUTE, wxID_DBMPOBJECTS, wxID_DBMPPROCEDURES, wxID_DBMPPYTHON, 
 wxID_DBMPWELCOME, wxID_DBMSPLITTERWINDOWCODESNIPPET, 
 wxID_DBMSPLITTERWINDOWEXEC, wxID_DBMSPLITTERWINDOWEXEC1, 
 wxID_DBMSPLITTERWINDOWOBJECT, wxID_DBMSPLITTERWINDOWOBJECT1, 
 wxID_DBMSPLITTERWINDOWOBJECT2, wxID_DBMSPLITTERWINDOWPROCEDURES, 
 wxID_DBMSPLITTERWINDOWPYTHON, wxID_DBMSPLITTERWINDOWPYTHON1, 
 wxID_DBMSTATICBITMAP1, wxID_DBMSTATICTEXT1, wxID_DBMSTATICTEXT3, 
 wxID_DBMSTATICTEXT4, wxID_DBMSTATICTEXT7, wxID_DBMSTATICTEXT_MSG, 
 wxID_DBMSTATUSBAR_EXEC, wxID_DBMSTATUSBAR_OBJECT, wxID_DBMTEXTACTSQL, 
 wxID_DBMTEXTCODESNIPPET, wxID_DBMTEXTCONNMSG, wxID_DBMTEXTPROCEDURES, 
 wxID_DBMTREECODESNIPPET, wxID_DBMTREEPYTHON, wxID_DBMTREESQLS, 
 wxID_DBMTXTACTTIME, wxID_DBMTXTI1, wxID_DBMTXTI2, wxID_DBMTXTSPLITCHAR, 
 wxID_DBMTXTTIMEOUT, 
] = [wx.NewId() for _init_ctrls in range(86)]

[wxID_DBMTIME_CHANGECTRLPOS, wxID_DBMTIME_KEEPACTIVE, 
 wxID_DBMTIME_SETEDITFOCUS, 
] = [wx.NewId() for _init_utils in range(3)]

[wxID_DBMTOOLBAR_EXECEXECUTE_SELECTED_SQL, wxID_DBMTOOLBAR_EXECEXECUTE_SQL,
 wxID_DBMTOOLBAR_EXECTOOLS2, wxID_DBMTOOLBAR_EXECTOOLS3,
] = [wx.NewId() for _init_coll_toolBar_Exec_Tools in range(4)]

[wxID_DBMTOOLBAR_QUERYTOOLS0, wxID_DBMTOOLBAR_QUERYTOOLS1,
 wxID_DBMTOOLBAR_QUERYTOOLS2, wxID_DBMTOOLBAR_QUERYTOOLS3,
 wxID_DBMTOOLBAR_QUERYTOOLS4, wxID_DBMTOOLBAR_QUERYTOOLS5,
] = [wx.NewId() for _init_coll_toolBar_query_Tools in range(6)]

class mylock22():
    def __init__(self):
        self.lock = threading.Lock()
    def acquire(self):
        print ' lock.acq',
        return self.lock.acquire()
    def release(self):
        print ' lock.rel'
        return self.lock.release()
        
class dbGridTable(wx.grid.PyGridTableBase):
    def __init__(self, data, description2, str_encode, nullstr=''):
        self.str_encode = str_encode
        wx.grid.PyGridTableBase.__init__(self)
        self.nullstr = nullstr
        self.row = 1
        self.col = 1
        try:
            self.row = len(data)
            if self.row == 0:
                self.col = len(description2)
            else:
                self.col = len(data[0])
        except Exception as _ee:
            pass
        self.data = data
        self.data_change_pos = []
        if len(description2) >0 and type(description2[0]) == type(()):
            self.desc = [i[0] for i in description2]
        else:
            self.desc = description2
    def GetNumberRows(self):
        return self.row
    def GetNumberCols(self):
        return self.col
    def IsEmptyCell(self, row, col):
        #print'IsEmptyCel', row, col
        if self.data:
            return self.data[row][col] is None
    def GetValue(self, row, col):
        #print 'get value ', row, col
        if self.data:
            if self.data[row][col] is None:
                return self.nullstr
            else:
                dd = self.data[row][col]
                try: dd = unicode(self.data[row][col], self.str_encode)
                except:
                    pass
                return dd
    def SetValue(self, row, col, value):
        self.data_change_pos.append((row, col))
        if type(self.data[row]) != type([]):
            self.data[row] = [i for i in self.data[row]]
        self.data[row][col] = value
        self.GetView().SetCellBackgroundColour(row, col, wx.Color(188, 0, 0))
    def GetColLabelValue(self, col):
        try:
            return unicode(self.desc[col], self.str_encode) #[0]
        except Exception as _ee:
            return '_??_'


class Db2db():
    def __init__(self):
        self.node = ''
        self.ip = ''
        self.dbname = ''
        self.dbuser = ''
        self.password = ''
        self.db = None
        self.id_db = ''
        self.cs = None
        self.info = ''
        self.ischange = False
        self.color = wx.Color(255, 255, 255)

class Db2_connected():
    def __init__(self, *args):
        pass
        self.db = args[0]
        self.cs = args[1]
        self.node = args[2]
        self.dbname = args[3]
        self.dbuser = args[4]
        self.password = args[5]
        self.comment = args[6]


[wxID_DBMMENUEXECITEMS_EXEC_SINGLE, wxID_DBMMENUEXECITEMS_EXEC_SQLS, 
 wxID_DBMMENUEXECITEMS_FORMAT_SQL, wxID_DBMMENUEXECITEMS_EXEC_SQLS11, wxID_DBMMENUEXECITEMS_EXEC_SQLS12, 
] = [wx.NewId() for _init_coll_menuExec_Items in range(5)]

[wxID_DBMMENUFILEITEMS_RELOAD, wxID_DBMMENUFILEITEMS_SAVE, 
 wxID_DBMMENUFILEITEM_EXIT, 
] = [wx.NewId() for _init_coll_menuFile_Items in range(3)]

[wxID_DBMMENUEDITITEMS_FIND, wxID_DBMMENUEDITITEMS_REPLACE, 
] = [wx.NewId() for _init_coll_menuEdit_Items in range(2)]

[wxID_DBMMENUWINDOWITEMS_H, wxID_DBMMENUWINDOWITEMS_V, 
] = [wx.NewId() for _init_coll_menuWindow_Items in range(2)]

[wxID_DBMMENUHELPITEMS_HELP_ABOUT] = [wx.NewId() for _init_coll_menuHelp_Items in range(1)]

class dbM(wx.Frame):
    def _init_coll_menuWindow_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_DBMMENUWINDOWITEMS_H,
              kind=wx.ITEM_NORMAL, text=_(u'split H'))
        parent.Append(help='', id=wxID_DBMMENUWINDOWITEMS_V,
              kind=wx.ITEM_NORMAL, text=_(u'split V'))

    def _init_coll_menuEdit_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_DBMMENUEDITITEMS_FIND,
              kind=wx.ITEM_NORMAL, text=_(u'&Find...\tCtrl-F'))
        parent.Append(help='', id=wxID_DBMMENUEDITITEMS_REPLACE,
              kind=wx.ITEM_NORMAL, text=_(u'&Replace...\tCtrl-H'))
        self.Bind(wx.EVT_MENU, self.OnMenuEditItems_findMenu,
              id=wxID_DBMMENUEDITITEMS_FIND)
        self.Bind(wx.EVT_MENU, self.OnMenuEditItems_replaceMenu,
              id=wxID_DBMMENUEDITITEMS_REPLACE)

    def _init_coll_menuHelp_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_DBMMENUHELPITEMS_HELP_ABOUT,
              kind=wx.ITEM_NORMAL, text=_(u'&About ...'))
        self.Bind(wx.EVT_MENU, self.OnMenuHelpItems_help_aboutMenu,
              id=wxID_DBMMENUHELPITEMS_HELP_ABOUT)

    def _init_coll_menuFile_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_DBMMENUFILEITEMS_SAVE,
              kind=wx.ITEM_NORMAL, text=_(u'&Save Selected Text\tCtrl-S'))
        parent.Append(help='', id=wxID_DBMMENUFILEITEMS_RELOAD,
              kind=wx.ITEM_NORMAL, text=_(u'&Reload from config\tCtrl-R'))
        parent.Append(help='', id=wxID_DBMMENUFILEITEM_EXIT,
              kind=wx.ITEM_NORMAL, text=_(u'E&xit'))
        self.Bind(wx.EVT_MENU, self.OnMenuFileItems_saveMenu,
              id=wxID_DBMMENUFILEITEMS_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuFileItems_reloadMenu,
              id=wxID_DBMMENUFILEITEMS_RELOAD)
        self.Bind(wx.EVT_MENU, self.OnMenuFileItem_exitMenu,
              id=wxID_DBMMENUFILEITEM_EXIT)

    def _init_coll_menuExec_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_DBMMENUEXECITEMS_EXEC_SQLS,
              kind=wx.ITEM_NORMAL,
              text=_(u'execute selected SQLs\tCtrl-Return'))
        parent.Append(help='', id=wxID_DBMMENUEXECITEMS_EXEC_SINGLE,
              kind=wx.ITEM_NORMAL,
              text=_(u'execute selected single\tCtrl-Shift-Return'))
        parent.Append(help='', id=wxID_DBMMENUEXECITEMS_FORMAT_SQL,
              kind=wx.ITEM_NORMAL,
              text=_(u'format selected SQL\tCtrl-Shift-F'))
        parent.Append(help='', id=wxID_DBMMENUEXECITEMS_EXEC_SQLS11,
              kind=wx.ITEM_NORMAL,
              text=_(u'execute 11 unicode'))
        parent.Append(help='', id=wxID_DBMMENUEXECITEMS_EXEC_SQLS12,
              kind=wx.ITEM_NORMAL,
              text=_(u'execute 12 str'))
        self.Bind(wx.EVT_MENU, self.OnMenuExecItems_exec_sqlsMenu,
              id=wxID_DBMMENUEXECITEMS_EXEC_SQLS)
        self.Bind(wx.EVT_MENU, self.x11,
              id=wxID_DBMMENUEXECITEMS_EXEC_SQLS11)
        self.Bind(wx.EVT_MENU, self.x12,
              id=wxID_DBMMENUEXECITEMS_EXEC_SQLS12)
        self.Bind(wx.EVT_MENU, self.OnMenuExecItems_exec_singleMenu,
              id=wxID_DBMMENUEXECITEMS_EXEC_SINGLE)
        self.Bind(wx.EVT_MENU, self.OnMenuExecItems_format_sqlMenu,
              id=wxID_DBMMENUEXECITEMS_FORMAT_SQL)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenuExec,
              id=wxID_DBMMENUEXECITEMS_EXEC_SINGLE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenuExec,
              id=wxID_DBMMENUEXECITEMS_EXEC_SQLS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenuFormatSql,
              id=wxID_DBMMENUEXECITEMS_FORMAT_SQL)

    def _init_coll_nbM2_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.gridM21, select=True,
              text=_(u'column'))
        parent.AddPage(imageId=-1, page=self.gridM22, select=False,
              text=_(u'data'))
        parent.AddPage(imageId=-1, page=self.gridM23, select=False,
              text=_(u'count'))

    def _init_coll_nbM1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.gridM11, select=True,
              text=_(u'column'))
        parent.AddPage(imageId=-1, page=self.gridM12, select=False,
              text=_(u'data'))
        parent.AddPage(imageId=-1, page=self.gridM13, select=False,
              text=_(u'count'))

    def _init_coll_nbMainFrame_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.Pwelcome, select=True,
              text=_(u'&1.Welcome'))
        parent.AddPage(imageId=-1, page=self.Pconnect, select=False,
              text=_(u'&2.Connect'))
        parent.AddPage(imageId=-1, page=self.Pcodesnippet, select=False,
              text=_(u'&C.ode Snippet'))
        parent.AddPage(imageId=-1, page=self.Pprocedures, select=False,
              text=_(u'&P.rocedures'))
        parent.AddPage(imageId=-1, page=self.Pobjects, select=False,
              text=_(u'&O.bjects'))
        parent.AddPage(imageId=-1, page=self.Pexecute, select=False,
              text=_(u'&E.xecute sqls'))
        parent.AddPage(imageId=-1, page=self.Ppython, select=False,
              text=_(u'P.&ython'))

    def _init_coll_nbDbs_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.gridDbs, select=True,
              text=_(u'DBALIAS'))
        parent.AddPage(imageId=-1, page=self.textConnMsg, select=False,
              text=_(u'Log'))

    def _init_utils(self):
        # generated method, don't edit
        self.time_keepactive = wx.Timer(id=wxID_DBMTIME_KEEPACTIVE, owner=self)
        self.Bind(wx.EVT_TIMER, self.OnTime_KeepActive,
              id=wxID_DBMTIME_KEEPACTIVE)

        self.time_changectrlpos = wx.Timer(id=wxID_DBMTIME_CHANGECTRLPOS,
              owner=self)
        self.Bind(wx.EVT_TIMER, self.OnTime_ChangeCtrlPos,
              id=wxID_DBMTIME_CHANGECTRLPOS)

        self.time_seteditfocus = wx.Timer(id=wxID_DBMTIME_SETEDITFOCUS,
              owner=self)
        self.Bind(wx.EVT_TIMER, self.OnTime_SetEditFocus,
              id=wxID_DBMTIME_SETEDITFOCUS)

        self.menuMainMenuBar = wx.MenuBar()

        self.menuFile = wx.Menu(title='')

        self.menuEdit = wx.Menu(title='')

        self.menuExec = wx.Menu(title='')

        self.menuHelp = wx.Menu(title='')

        self.menuWindow = wx.Menu(title='')

        self._init_coll_menuFile_Items(self.menuFile)
        self._init_coll_menuEdit_Items(self.menuEdit)
        self._init_coll_menuExec_Items(self.menuExec)
        self._init_coll_menuHelp_Items(self.menuHelp)
        self._init_coll_menuWindow_Items(self.menuWindow)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_DBM, name=u'dbM', parent=prnt,
              pos=wx.Point(211, 45), size=wx.Size(1024, 666),
              style=wx.DEFAULT_FRAME_STYLE, title=_(u'dbtool'))
        self._init_utils()
        self.SetClientSize(wx.Size(1016, 638))
        self.Bind(wx.EVT_CLOSE, self.OnDbMClose)
        self.Bind(wx.EVT_SIZE, self.OnDbMSize)

        self.nbMainFrame = wx.Notebook(id=wxID_DBMNBMAINFRAME,
              name='nbMainFrame', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(1016, 638), style=wx.NB_FIXEDWIDTH)
        self.nbMainFrame.SetLabel(_(u'234\n234234234'))
        self.nbMainFrame.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnNbMainFrameNotebookPageChanged, id=wxID_DBMNBMAINFRAME)

        self.Pwelcome = wx.Panel(id=wxID_DBMPWELCOME, name=u'Pwelcome',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.NullBitmap,
              id=wxID_DBMSTATICBITMAP1, name='staticBitmap1',
              parent=self.Pwelcome, pos=wx.Point(40, 32), size=wx.Size(104, 88),
              style=0)

        self.staticText1 = wx.StaticText(id=wxID_DBMSTATICTEXT1,
              label=_(u'Db2'), name='staticText1', parent=self.Pwelcome,
              pos=wx.Point(176, 32), size=wx.Size(584, 24), style=2)

        self.staticText3 = wx.StaticText(id=wxID_DBMSTATICTEXT3,
              label=_(u'# features\nkeep active\nshow table,view,procedures..\ndiff 2 db objects\ndata copy,export\nchange program run status(python)\n\n# development\npython\nPyDB2\nwxPython\nBoa Constructor\nEclipse + pyDev\n'),
              name='staticText3', parent=self.Pwelcome, pos=wx.Point(176, 64),
              size=wx.Size(584, 344), style=2)

        self.Pconnect = wx.Panel(id=wxID_DBMPCONNECT, name=u'Pconnect',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.staticText4 = wx.StaticText(id=wxID_DBMSTATICTEXT4,
              label=_(u'connect setting'), name='staticText4',
              parent=self.Pconnect, pos=wx.Point(8, 8), size=wx.Size(87, 14),
              style=2)

        self.txtActtime = wx.TextCtrl(id=wxID_DBMTXTACTTIME, name=u'txtActtime',
              parent=self.Pconnect, pos=wx.Point(144, 32), size=wx.Size(48, 22),
              style=0, value=u'180')

        self.textActsql = wx.TextCtrl(id=wxID_DBMTEXTACTSQL, name=u'textActsql',
              parent=self.Pconnect, pos=wx.Point(192, 32), size=wx.Size(640,
              24), style=0,
              value=u'select current timestamp from syscat.tables fetch first 1 rows only')

        self.btnFont = wx.Button(id=wxID_DBMBTNFONT, label=_(u'Change Fonts'),
              name=u'btnFont', parent=self.Pconnect, pos=wx.Point(848, 32),
              size=wx.Size(88, 24), style=0)
        self.btnFont.Bind(wx.EVT_BUTTON, self.OnBtnFontButton,
              id=wxID_DBMBTNFONT)

        self.btnRefreshDb = wx.Button(id=wxID_DBMBTNREFRESHDB,
              label=_(u'&Refresh'), name=u'btnRefreshDb', parent=self.Pconnect,
              pos=wx.Point(192, 120), size=wx.Size(75, 24), style=0)
        self.btnRefreshDb.Bind(wx.EVT_BUTTON, self.OnBtnRefreshDbButton,
              id=wxID_DBMBTNREFRESHDB)

        self.btnSaveDbs = wx.Button(id=wxID_DBMBTNSAVEDBS, label=_(u'&Save'),
              name=u'btnSaveDbs', parent=self.Pconnect, pos=wx.Point(296, 120),
              size=wx.Size(75, 24), style=0)
        self.btnSaveDbs.Bind(wx.EVT_BUTTON, self.OnBtnSaveDbsButton,
              id=wxID_DBMBTNSAVEDBS)

        self.btnRefreshDbs = wx.Button(id=wxID_DBMBTNREFRESHDBS,
              label=_(u'Rescan catalog'), name=u'btnRefreshDbs',
              parent=self.Pconnect, pos=wx.Point(528, 120), size=wx.Size(96,
              24), style=0)
        self.btnRefreshDbs.SetToolTipString(_(u'Re scan node,db catalog, use few time.'))
        self.btnRefreshDbs.Bind(wx.EVT_BUTTON, self.OnBtnRefreshDbsButton,
              id=wxID_DBMBTNREFRESHDBS)

        self.btnDisconnectAll = wx.Button(id=wxID_DBMBTNDISCONNECTALL,
              label=_(u'Disconnect All'), name=u'btnDisconnectAll',
              parent=self.Pconnect, pos=wx.Point(664, 120), size=wx.Size(136,
              24), style=0)
        self.btnDisconnectAll.Bind(wx.EVT_BUTTON, self.OnBtnDisconnectAllButton,
              id=wxID_DBMBTNDISCONNECTALL)

        self.staticText7 = wx.StaticText(id=wxID_DBMSTATICTEXT7,
              label=_(u'Keep Active second: '), name='staticText7',
              parent=self.Pconnect, pos=wx.Point(8, 32), size=wx.Size(120, 22),
              style=0)

        self.nbDbs = wx.Notebook(id=wxID_DBMNBDBS, name=u'nbDbs',
              parent=self.Pconnect, pos=wx.Point(0, 144), size=wx.Size(936,
              416), style=0)

        self.gridDbs = wx.grid.Grid(id=wxID_DBMGRIDDBS, name=u'gridDbs',
              parent=self.nbDbs, pos=wx.Point(0, 0), size=wx.Size(928, 389),
              style=0)
        self.gridDbs.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
              self.OnGridDbsGridCellRightClick)
        self.gridDbs.Bind(wx.grid.EVT_GRID_CELL_CHANGE,
              self.OnGridDbsGridCellChange)

        self.textConnMsg = wx.TextCtrl(id=wxID_DBMTEXTCONNMSG,
              name=u'textConnMsg', parent=self.nbDbs, pos=wx.Point(0, 0),
              size=wx.Size(928, 389),
              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.HSCROLL,
              value=u'')
        self.textConnMsg.Bind(wx.EVT_LEFT_DCLICK, self.OnTextConnMsgLeftDclick)
        self.textConnMsg.Bind(wx.EVT_TEXT_MAXLEN, self.OnTextConnMsgTextMaxlen,
              id=wxID_DBMTEXTCONNMSG)

        self.Pcodesnippet = wx.Panel(id=wxID_DBMPCODESNIPPET,
              name=u'Pcodesnippet', parent=self.nbMainFrame, pos=wx.Point(0, 0),
              size=wx.Size(1008, 611), style=wx.TAB_TRAVERSAL)

        self.btnCodeReload = wx.Button(id=wxID_DBMBTNCODERELOAD,
              label=_(u'Reload'), name=u'btnCodeReload',
              parent=self.Pcodesnippet, pos=wx.Point(16, 8), size=wx.Size(80,
              24), style=0)
        self.btnCodeReload.Bind(wx.EVT_BUTTON, self.OnBtnCodeReloadButton,
              id=wxID_DBMBTNCODERELOAD)

        self.btnCodeSave = wx.Button(id=wxID_DBMBTNCODESAVE,
              label=_(u'SaveSel'), name=u'btnCodeSave',
              parent=self.Pcodesnippet, pos=wx.Point(112, 8), size=wx.Size(80,
              24), style=0)
        self.btnCodeSave.Bind(wx.EVT_BUTTON, self.OnBtnCodeSaveButton,
              id=wxID_DBMBTNCODESAVE)

        self.btnDb2Help = wx.Button(id=wxID_DBMBTNDB2HELP,
              label=_('db2 ? sqlXXXX'), name='btnDb2Help',
              parent=self.Pcodesnippet, pos=wx.Point(416, 8), size=wx.Size(248,
              24), style=0)
        self.btnDb2Help.Bind(wx.EVT_BUTTON, self.OnBtnDB2HelpButton,
              id=wxID_DBMBTNDB2HELP)

        self.button4 = wx.Button(id=wxID_DBMBUTTON4, label=_('button4'),
              name='button4', parent=self.Pcodesnippet, pos=wx.Point(680, 8),
              size=wx.Size(224, 24), style=0)
        self.button4.Bind(wx.EVT_BUTTON, self.OnButton4Button,
              id=wxID_DBMBUTTON4)

        self.splitterWindowCodeSnippet = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWCODESNIPPET,
              name=u'splitterWindowCodeSnippet', parent=self.Pcodesnippet,
              pos=wx.Point(16, 40), size=wx.Size(320, 136),
              style=wx.SP_NOBORDER)

        self.treeCodeSnippet = wx.TreeCtrl(id=wxID_DBMTREECODESNIPPET,
              name=u'treeCodeSnippet', parent=self.splitterWindowCodeSnippet,
              pos=wx.Point(0, 0), size=wx.Size(136, 136),
              style=wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE)
        self.treeCodeSnippet.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
              self.OnTreeCodeSnippetTreeItemRightClick,
              id=wxID_DBMTREECODESNIPPET)
        self.treeCodeSnippet.Bind(wx.EVT_TREE_SEL_CHANGED,
              self.OnTreeCodeSnippetTreeSelChanged, id=wxID_DBMTREECODESNIPPET)

        self.textCodeSnippet = wx.TextCtrl(id=wxID_DBMTEXTCODESNIPPET,
              name=u'textCodeSnippet', parent=self.splitterWindowCodeSnippet,
              pos=wx.Point(136, 0), size=wx.Size(184, 136),
              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.HSCROLL | wx.TE_NOHIDESEL,
              value=u'')

        self.Pprocedures = wx.Panel(id=wxID_DBMPPROCEDURES, name='Pprocedures',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.btnCallProc = wx.Button(id=wxID_DBMBTNCALLPROC,
              label=_(u'Call Proc'), name=u'btnCallProc',
              parent=self.Pprocedures, pos=wx.Point(376, 8), size=wx.Size(75,
              24), style=0)
        self.btnCallProc.Bind(wx.EVT_BUTTON, self.OnBtnCallProcButton,
              id=wxID_DBMBTNCALLPROC)

        self.btnListprocs = wx.Button(id=wxID_DBMBTNLISTPROCS,
              label=_(u'List All Procedures'), name=u'btnListprocs',
              parent=self.Pprocedures, pos=wx.Point(232, 8), size=wx.Size(136,
              24), style=0)
        self.btnListprocs.Bind(wx.EVT_BUTTON, self.OnBtnListprocsButton,
              id=wxID_DBMBTNLISTPROCS)

        self.splitterWindowProcedures = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWPROCEDURES,
              name=u'splitterWindowProcedures', parent=self.Pprocedures,
              pos=wx.Point(16, 40), size=wx.Size(328, 208),
              style=wx.SP_NOBORDER)

        self.lstProcedures = wx.CheckListBox(choices=[],
              id=wxID_DBMLSTPROCEDURES, name=u'lstProcedures',
              parent=self.splitterWindowProcedures, pos=wx.Point(0, 0),
              size=wx.Size(96, 208), style=0)
        self.lstProcedures.Bind(wx.EVT_CHECKLISTBOX,
              self.OnLstProceduresChecklistbox, id=wxID_DBMLSTPROCEDURES)

        self.textProcedures = wx.TextCtrl(id=wxID_DBMTEXTPROCEDURES,
              name=u'textProcedures', parent=self.splitterWindowProcedures,
              pos=wx.Point(96, 0), size=wx.Size(232, 208),
              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.HSCROLL | wx.TE_NOHIDESEL,
              value=u'')

        self.Pobjects = wx.Panel(id=wxID_DBMPOBJECTS, name='Pobjects',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.staticText_Msg = wx.StaticText(id=wxID_DBMSTATICTEXT_MSG,
              label=_(u'compare'), name=u'staticText_Msg', parent=self.Pobjects,
              pos=wx.Point(272, 8), size=wx.Size(64, 18), style=0)
        self.staticText_Msg.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, u'Arial Black'))

        self.statusBar_object = wx.StatusBar(id=wxID_DBMSTATUSBAR_OBJECT,
              name=u'statusBar_object', parent=self.Pobjects, style=0)

        self.choiceType = wx.Choice(choices=[], id=wxID_DBMCHOICETYPE,
              name=u'choiceType', parent=self.Pobjects, pos=wx.Point(0, 8),
              size=wx.Size(200, 22), style=0)
        self.choiceType.Bind(wx.EVT_CHOICE, self.OnChoiceTypeChoice,
              id=wxID_DBMCHOICETYPE)

        self.chkLink = wx.CheckBox(id=wxID_DBMCHKLINK, label=_(u'Link'),
              name=u'chkLink', parent=self.Pobjects, pos=wx.Point(208, 8),
              size=wx.Size(56, 24), style=0)
        self.chkLink.SetValue(False)
        self.chkLink.Bind(wx.EVT_CHECKBOX, self.OnCbxLinkCheckbox,
              id=wxID_DBMCHKLINK)

        self.splitterWindowObject = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWOBJECT,
              name=u'splitterWindowObject', parent=self.Pobjects,
              pos=wx.Point(0, 64), size=wx.Size(10, 10), style=wx.SP_NOBORDER)
        self.splitterWindowObject.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
              self.OnSplitterWindowObjectSplitterSashPosChanged,
              id=wxID_DBMSPLITTERWINDOWOBJECT)

        self.splitterWindowObject1 = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWOBJECT1,
              name=u'splitterWindowObject1', parent=self.splitterWindowObject,
              pos=wx.Point(0, 0), size=wx.Size(2, 1), style=wx.SP_NOBORDER)
        self.splitterWindowObject1.Bind(wx.EVT_LEFT_DCLICK,
              self.OnSplitterWindowObject1LeftDclick)
        self.splitterWindowObject1.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
              self.OnSplitterWindowObjectSplitterSashPosChanged,
              id=wxID_DBMSPLITTERWINDOWOBJECT1)

        self.panelM1 = wx.Panel(id=wxID_DBMPANELM1, name=u'panelM1',
              parent=self.splitterWindowObject1, pos=wx.Point(0, 0),
              size=wx.Size(1, 1), style=wx.TAB_TRAVERSAL)

        self.panelM2 = wx.Panel(id=wxID_DBMPANELM2, name=u'panelM2',
              parent=self.splitterWindowObject1, pos=wx.Point(2, 0),
              size=wx.Size(1, 1), style=wx.TAB_TRAVERSAL)

        self.choiceDb1 = wx.Choice(choices=[], id=wxID_DBMCHOICEDB1,
              name=u'choiceDb1', parent=self.panelM1, pos=wx.Point(0, 0),
              size=wx.Size(200, 22), style=0)
        self.choiceDb1.Bind(wx.EVT_CHOICE, self.OnChoiceDb1Choice,
              id=wxID_DBMCHOICEDB1)

        self.choiceSchema1 = wx.Choice(choices=[], id=wxID_DBMCHOICESCHEMA1,
              name=u'choiceSchema1', parent=self.panelM1, pos=wx.Point(0, 22),
              size=wx.Size(200, 22), style=0)
        self.choiceSchema1.Bind(wx.EVT_CHOICE, self.OnChoiceSchema1Choice,
              id=wxID_DBMCHOICESCHEMA1)

        self.txtI1 = wx.TextCtrl(id=wxID_DBMTXTI1, name=u'txtI1',
              parent=self.panelM1, pos=wx.Point(0, 44), size=wx.Size(200, 22),
              style=0, value=u'')
        self.txtI1.Bind(wx.EVT_TEXT, self.OnTxtI1Text, id=wxID_DBMTXTI1)

        self.lstT1 = wx.ListBox(choices=[], id=wxID_DBMLSTT1, name=u'lstT1',
              parent=self.panelM1, pos=wx.Point(0, 66), size=wx.Size(200, 120),
              style=0)
        self.lstT1.Bind(wx.EVT_LISTBOX, self.OnLstT1Listbox, id=wxID_DBMLSTT1)

        self.choiceDb2 = wx.Choice(choices=[], id=wxID_DBMCHOICEDB2,
              name=u'choiceDb2', parent=self.panelM2, pos=wx.Point(0, 0),
              size=wx.Size(200, 22), style=0)
        self.choiceDb2.Bind(wx.EVT_CHOICE, self.OnChoiceDb2Choice,
              id=wxID_DBMCHOICEDB2)

        self.choiceSchema2 = wx.Choice(choices=[], id=wxID_DBMCHOICESCHEMA2,
              name=u'choiceSchema2', parent=self.panelM2, pos=wx.Point(0, 22),
              size=wx.Size(200, 22), style=0)
        self.choiceSchema2.Bind(wx.EVT_CHOICE, self.OnChoiceSchema2Choice,
              id=wxID_DBMCHOICESCHEMA2)

        self.txtI2 = wx.TextCtrl(id=wxID_DBMTXTI2, name=u'txtI2',
              parent=self.panelM2, pos=wx.Point(0, 44), size=wx.Size(200, 22),
              style=0, value=u'')
        self.txtI2.Bind(wx.EVT_TEXT, self.OnTxtI2Text, id=wxID_DBMTXTI2)

        self.lstT2 = wx.ListBox(choices=[], id=wxID_DBMLSTT2, name=u'lstT2',
              parent=self.panelM2, pos=wx.Point(0, 66), size=wx.Size(200, 120),
              style=0)
        self.lstT2.Bind(wx.EVT_LISTBOX, self.OnLstT2Listbox, id=wxID_DBMLSTT2)

        self.btnExportDDL = wx.Button(id=wxID_DBMBTNEXPORTDDL,
              label=_(u'Export DDL'), name=u'btnExportDDL',
              parent=self.Pobjects, pos=wx.Point(344, 32), size=wx.Size(88, 24),
              style=0)
        self.btnExportDDL.Bind(wx.EVT_BUTTON, self.OnBtnExportDDLButton,
              id=wxID_DBMBTNEXPORTDDL)

        self.btnFormatSpace = wx.Button(id=wxID_DBMBTNFORMATSPACE,
              label=_(u'format Spaces'), name=u'btnFormatSpace',
              parent=self.Pobjects, pos=wx.Point(440, 32), size=wx.Size(96, 24),
              style=0)
        self.btnFormatSpace.Bind(wx.EVT_BUTTON, self.OnBtnFormatSpaceButton,
              id=wxID_DBMBTNFORMATSPACE)

        self.btnCompare = wx.Button(id=wxID_DBMBTNCOMPARE, label=_(u'Compare'),
              name=u'btnCompare', parent=self.Pobjects, pos=wx.Point(552, 32),
              size=wx.Size(112, 24), style=0)
        self.btnCompare.Bind(wx.EVT_BUTTON, self.OnBtnCompareButton,
              id=wxID_DBMBTNCOMPARE)

        self.splitterWindowObject2 = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWOBJECT2,
              name=u'splitterWindowObject2', parent=self.splitterWindowObject,
              pos=wx.Point(3, 0), size=wx.Size(1, 1), style=wx.SP_NOBORDER)
        self.splitterWindowObject2.Bind(wx.EVT_LEFT_DCLICK,
              self.OnSplitterWindowObject2LeftDclick)

        self.nbM1 = wx.Notebook(id=wxID_DBMNBM1, name=u'nbM1',
              parent=self.splitterWindowObject2, pos=wx.Point(16, 8),
              size=wx.Size(1, 1), style=0)
        self.nbM1.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnNbM1NotebookPageChanged, id=wxID_DBMNBM1)

        self.nbM2 = wx.Notebook(id=wxID_DBMNBM2, name=u'nbM2',
              parent=self.splitterWindowObject2, pos=wx.Point(104, 16),
              size=wx.Size(1, 1), style=0)
        self.nbM2.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnNbM2NotebookPageChanged, id=wxID_DBMNBM2)

        self.gridM11 = wx.grid.Grid(id=wxID_DBMGRIDM11, name=u'gridM11',
              parent=self.nbM1, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.gridM12 = wx.grid.Grid(id=wxID_DBMGRIDM12, name=u'gridM12',
              parent=self.nbM1, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.gridM13 = wx.grid.Grid(id=wxID_DBMGRIDM13, name=u'gridM13',
              parent=self.nbM1, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.gridM21 = wx.grid.Grid(id=wxID_DBMGRIDM21, name=u'gridM21',
              parent=self.nbM2, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.gridM22 = wx.grid.Grid(id=wxID_DBMGRIDM22, name=u'gridM22',
              parent=self.nbM2, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.gridM23 = wx.grid.Grid(id=wxID_DBMGRIDM23, name=u'gridM23',
              parent=self.nbM2, pos=wx.Point(0, 0), size=wx.Size(1, 1),
              style=0)

        self.Pexecute = wx.Panel(id=wxID_DBMPEXECUTE, name=u'Pexecute',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.btnSQLReload = wx.Button(id=wxID_DBMBTNSQLRELOAD,
              label=_(u'Reload'), name=u'btnSQLReload', parent=self.Pexecute,
              pos=wx.Point(0, 8), size=wx.Size(56, 24), style=0)
        self.btnSQLReload.Bind(wx.EVT_BUTTON, self.OnBtnSQLReloadButton,
              id=wxID_DBMBTNSQLRELOAD)

        self.btnSQLSave = wx.Button(id=wxID_DBMBTNSQLSAVE, label=_(u'SaveSel'),
              name=u'btnSQLSave', parent=self.Pexecute, pos=wx.Point(56, 8),
              size=wx.Size(56, 24), style=0)
        self.btnSQLSave.Bind(wx.EVT_BUTTON, self.OnBtnSQLSaveButton,
              id=wxID_DBMBTNSQLSAVE)

        self.choiceConnectedDbnames = wx.Choice(choices=[],
              id=wxID_DBMCHOICECONNECTEDDBNAMES, name=u'choiceConnectedDbnames',
              parent=self.Pexecute, pos=wx.Point(120, 8), size=wx.Size(304, 22),
              style=0)
        self.choiceConnectedDbnames.Bind(wx.EVT_CHOICE,
              self.OnChoiceConnectedDbnamesChoice,
              id=wxID_DBMCHOICECONNECTEDDBNAMES)

        self.txtTimeout = wx.TextCtrl(id=wxID_DBMTXTTIMEOUT, name=u'txtTimeout',
              parent=self.Pexecute, pos=wx.Point(760, 8), size=wx.Size(48, 22),
              style=0, value=u'10,1')
        self.txtTimeout.SetToolTipString(_(u'set execute timeout value (single,multi)'))

        self.txtSplitChar = wx.TextCtrl(id=wxID_DBMTXTSPLITCHAR,
              name=u'txtSplitChar', parent=self.Pexecute, pos=wx.Point(808, 8),
              size=wx.Size(32, 22), style=0, value=u';')
        self.txtSplitChar.SetToolTipString(_(u'query split char'))

        self.chkLogSqls = wx.CheckBox(id=wxID_DBMCHKLOGSQLS,
              label=_(u'Log Sqls'), name=u'chkLogSqls', parent=self.Pexecute,
              pos=wx.Point(848, 8), size=wx.Size(64, 22), style=0)
        self.chkLogSqls.SetValue(True)
        self.chkLogSqls.SetToolTipString(_(u'log sql statement to log file'))

        self.chkShowSqlsRes = wx.CheckBox(id=wxID_DBMCHKSHOWSQLSRES,
              label=_(u'Show Normal sql Message'), name=u'chkShowSqlsRes',
              parent=self.Pexecute, pos=wx.Point(912, 8), size=wx.Size(160, 22),
              style=0)
        self.chkShowSqlsRes.SetValue(True)
        self.chkShowSqlsRes.SetToolTipString(_(u'show normal execute message to TextCtrl  ! Speed in execute much sqls '))

        self.btnExecSqls = wx.Button(id=wxID_DBMBTNEXECSQLS,
              label=_(u'E&xec SQLs'), name=u'btnExecSqls', parent=self.Pexecute,
              pos=wx.Point(432, 8), size=wx.Size(96, 24), style=0)
        self.btnExecSqls.SetToolTipString(_(u'Ctrl-Enter execute selected multi sql statement'))
        self.btnExecSqls.Bind(wx.EVT_BUTTON, self.OnBtnExecSqlsButton,
              id=wxID_DBMBTNEXECSQLS)

        self.btnExecSqlSingle = wx.Button(id=wxID_DBMBTNEXECSQLSINGLE,
              label=_(u'Exec 1'), name=u'btnExecSqlSingle',
              parent=self.Pexecute, pos=wx.Point(528, 8), size=wx.Size(48, 24),
              style=0)
        self.btnExecSqlSingle.SetToolTipString(_(u'Shift-Enter execute selected single sql statement '))
        self.btnExecSqlSingle.Bind(wx.EVT_BUTTON, self.OnBtnExecSqlSingleButton,
              id=wxID_DBMBTNEXECSQLSINGLE)

        self.btnCommit = wx.Button(id=wxID_DBMBTNCOMMIT, label=_(u'Commit'),
              name=u'btnCommit', parent=self.Pexecute, pos=wx.Point(616, 8),
              size=wx.Size(56, 24), style=0)
        self.btnCommit.Bind(wx.EVT_BUTTON, self.OnBtnCommitButton,
              id=wxID_DBMBTNCOMMIT)

        self.btnRollback = wx.Button(id=wxID_DBMBTNROLLBACK,
              label=_(u'Rollback'), name=u'btnRollback', parent=self.Pexecute,
              pos=wx.Point(672, 8), size=wx.Size(59, 24), style=0)
        self.btnRollback.Bind(wx.EVT_BUTTON, self.OnBtnRollbackButton,
              id=wxID_DBMBTNROLLBACK)

        self.statusBar_exec = wx.StatusBar(id=wxID_DBMSTATUSBAR_EXEC,
              name=u'statusBar_exec', parent=self.Pexecute, style=0)

        self.splitterWindowExec = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWEXEC,
              name=u'splitterWindowExec', parent=self.Pexecute, pos=wx.Point(0,
              36), size=wx.Size(416, 68), style=wx.SP_NOBORDER)
        self.splitterWindowExec.Bind(wx.EVT_LEFT_DCLICK,
              self.OnSplitterWindowExecLeftDclick)

        self.splitterWindowExec1 = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWEXEC1,
              name=u'splitterWindowExec1', parent=self.splitterWindowExec,
              pos=wx.Point(8, 0), size=wx.Size(392, 64), style=wx.SP_NOBORDER)

        self.treeSQLs = wx.TreeCtrl(id=wxID_DBMTREESQLS, name=u'treeSQLs',
              parent=self.splitterWindowExec1, pos=wx.Point(0, 0),
              size=wx.Size(8, 64), style=wx.TR_HAS_BUTTONS)
        self.treeSQLs.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnTreeSQLsTreeBeginDrag,
              id=wxID_DBMTREESQLS)
        self.treeSQLs.Bind(wx.EVT_TREE_SEL_CHANGED,
              self.OnTreeSQLsTreeSelChanged, id=wxID_DBMTREESQLS)
        self.treeSQLs.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
              self.OnTreeSQLsTreeItemRightClick, id=wxID_DBMTREESQLS)

        self.nbResult = wx.Notebook(id=wxID_DBMNBRESULT, name='nbResult',
              parent=self.splitterWindowExec, pos=wx.Point(0, 4),
              size=wx.Size(384, 44), style=0)
        self.nbResult.Bind(wx.EVT_LEFT_DCLICK, self.OnNbResultLeftDclick)
        self.nbResult.Bind(wx.EVT_RIGHT_DOWN, self.OnNbResultRightDown)
        self.nbResult.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnNbResultNotebookPageChanged, id=wxID_DBMNBRESULT)

        self.Ppython = wx.Panel(id=wxID_DBMPPYTHON, name='Ppython',
              parent=self.nbMainFrame, pos=wx.Point(0, 0), size=wx.Size(1008,
              611), style=wx.TAB_TRAVERSAL)

        self.btnPythonReload = wx.Button(id=wxID_DBMBTNPYTHONRELOAD,
              label=_(u'Reload'), name=u'btnPythonReload', parent=self.Ppython,
              pos=wx.Point(8, 8), size=wx.Size(80, 24), style=0)
        self.btnPythonReload.Bind(wx.EVT_BUTTON, self.OnBtnPythonReloadButton,
              id=wxID_DBMBTNPYTHONRELOAD)

        self.btnPythonSave = wx.Button(id=wxID_DBMBTNPYTHONSAVE,
              label=_(u'SaveSel'), name=u'btnPythonSave', parent=self.Ppython,
              pos=wx.Point(96, 8), size=wx.Size(80, 24), style=0)
        self.btnPythonSave.Bind(wx.EVT_BUTTON, self.OnBtnPythonSaveButton,
              id=wxID_DBMBTNPYTHONSAVE)

        self.btnExecPython = wx.Button(id=wxID_DBMBTNEXECPYTHON,
              label=_(u'e&xec'), name=u'btnExecPython', parent=self.Ppython,
              pos=wx.Point(368, 8), size=wx.Size(104, 24), style=0)
        self.btnExecPython.SetToolTipString(_(u'Ctrl-Enter execute selected code'))
        self.btnExecPython.Bind(wx.EVT_BUTTON, self.OnBtnExecPythonButton,
              id=wxID_DBMBTNEXECPYTHON)

        self.splitterWindowPython = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWPYTHON,
              name=u'splitterWindowPython', parent=self.Ppython, pos=wx.Point(8,
              40), size=wx.Size(112, 160), style=wx.SP_NOBORDER)

        self.treePython = wx.TreeCtrl(id=wxID_DBMTREEPYTHON, name=u'treePython',
              parent=self.splitterWindowPython, pos=wx.Point(0, 0),
              size=wx.Size(112, 160), style=wx.TR_HAS_BUTTONS)
        self.treePython.Bind(wx.EVT_TREE_SEL_CHANGED,
              self.OnTreePythonTreeSelChanged, id=wxID_DBMTREEPYTHON)
        self.treePython.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
              self.OnTreePythonTreeItemRightClick, id=wxID_DBMTREEPYTHON)

        self.splitterWindowPython1 = wx.SplitterWindow(id=wxID_DBMSPLITTERWINDOWPYTHON1,
              name=u'splitterWindowPython1', parent=self.splitterWindowPython,
              pos=wx.Point(120, 8), size=wx.Size(8, 100), style=wx.SP_NOBORDER)

        self._init_coll_nbMainFrame_Pages(self.nbMainFrame)
        self._init_coll_nbDbs_Pages(self.nbDbs)
        self._init_coll_nbM1_Pages(self.nbM1)
        self._init_coll_nbM2_Pages(self.nbM2)

    def __init__(self, parent):
        gettext.install(pgname, './locale', True)
        self.str_encode = locale.getdefaultlocale()[1]
        self.cfgread()
        self._init_ctrls(parent)
        self.iWELCOME, self.iCONNECT, self.iCODESNIPPET, self.iPROCEDURES = 0, 1, 2, 3
        self.iOBJECTS, self.iSQL, self.iPYTHON = 4, 5, 6
        self.conf_password = None

        self.icon_noconn16 = None
        self.icon_noconn32 = None
        self.icon_conn16 = None
        self.icon_conn32 = None
        try:
            self.staticBitmap1.SetBitmap(images.main_image.GetBitmap())
            self.icon_conn16 = images.Smiles.GetIcon()
            ic = images.Smiles.GetImage().ConvertToGreyscale().ConvertToBitmap(-1)
            self.icon_noconn16 = wx.EmptyIcon()
            self.icon_noconn16.CopyFromBitmap(ic)
            
            self.icon_conn32 = self.icon_conn16
            self.icon_conn32.SetSize(wx.Size(32,32))
            self.icon_noconn32 = self.icon_noconn16
            self.icon_noconn32.SetSize(wx.Size(32,32))
        except Exception as _ee:
            pass

        # MainFrame
        ms = [
              (self.menuFile, _('&File')),
              (self.menuEdit, _('&Edit')),
              (self.menuExec, _('E&xecute')),
              (self.menuWindow, _('&Window')),
              (self.menuHelp, _('&Help')),
              ]
        for i in ms:
            self.menuMainMenuBar.Append(i[0], i[1])
        self.SetMenuBar(self.menuMainMenuBar)
        self.nbMainFrame.SetSelection(0)
        
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

        self.init_ctrl(parent)
        self.init_keys()
        self.init_data(parent)
        #gettext.install(pgname, './locale', False, locale.getdefaultlocale()[1])

    def init_ctrl(self, parent):
        # 1
        self.textActsql.SetMaxLength(160)
        self.gridDbs.CreateGrid(1, 1)
        self.gridDbs_bgc = self.gridDbs.GetCellBackgroundColour(0, 0)
        self.gridDbs.DisableDragRowSize()
        self.nbDbs.SetSelection(0)
        self.textConnMsg.SetMaxLength(2**20)

        # code snippet
        self.splitterWindowCodeSnippet.SplitVertically(self.treeCodeSnippet, self.textCodeSnippet)
        self.splitterWindowCodeSnippet.SetMinimumPaneSize(30)
        self.splitterWindowCodeSnippet.SetSashPosition(200)

        # procedures
        self.splitterWindowProcedures.SplitVertically(self.lstProcedures, self.textProcedures)
        self.splitterWindowProcedures.SetMinimumPaneSize(30)
        self.splitterWindowProcedures.SetSashPosition(200)

        # Pobjects
        self.choiceType.AppendItems(['TABLE', 'VIEW', 'SUMMARY TABLE',
            'SERVER', 'DRDA', 'NICKNAME', 'BUFFERPOOL', 'TABLESPACE',
            'FUNCTION', 'TRIGGER', 'PROCEDURE',
            ])
        self.splitterWindowObject.SplitVertically(self.splitterWindowObject1, self.splitterWindowObject2)
        self.splitterWindowObject.SetMinimumPaneSize(1)
        self.splitterWindowObject.SetSashPosition(210)
        self.splitterWindowObject1.SplitVertically(self.panelM1, self.panelM2)
        self.splitterWindowObject1.SetMinimumPaneSize(1)
        self.splitterWindowObject1.SetSashGravity(0.5)
        wxID_STCM1 = wx.NewId()
        self.stcM1 = stc2.EditWindow(id=wxID_STCM1, name='stcM1', parent=self.nbM1,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='SQL')
        wxID_STCM2 = wx.NewId()
        self.stcM2 = stc2.EditWindow(id=wxID_STCM2, name='stcM2', parent=self.nbM2,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='SQL')
        self.nbM1.InsertPage(0,self.stcM1,'DDL',True)
        self.nbM2.InsertPage(0,self.stcM2,'DDL',True)
        self.splitterWindowObject2.SplitHorizontally(self.nbM1, self.nbM2)
        self.splitterWindowObject2.SetMinimumPaneSize(1)
        self.splitterWindowObject2.SetSashGravity(0.5)
        self.statusBar_object.SetFieldsCount(4)
        self.statusBar_object.SetStatusWidths([-6, -3, -7, -4])
        self.nbM1.publisher = wx.lib.pubsub.Publisher()
        self.nbM2.publisher = wx.lib.pubsub.Publisher()
        self.nbM1.publisher.subscribe(self.OnNbM1NotebookPageChanged, self.lstT1)
        self.nbM2.publisher.subscribe(self.OnNbM2NotebookPageChanged, self.lstT2)

        # execute
        wxID_STCEXECLOGS = wx.NewId()
        self.stcExecLog = stc2.EditWindow(id=wxID_STCEXECLOGS, name='stcLogs', parent=self.nbResult,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='SQL')
        wxID_STCEXECDATA = wx.NewId()
        self.stcExecData = stc2.EditWindow(id=wxID_STCEXECDATA, name='stcData', parent=self.nbResult,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='SQL')
        self.nbResult.AddPage(imageId=-1, page=self.stcExecLog, select=True, text=_(u'Log'))
        self.nbResult.AddPage(imageId=-1, page=self.stcExecData, select=False, text=_(u'Result T'))
        
        self.splitterWindowExec.SplitHorizontally(self.splitterWindowExec1, self.nbResult)
        self.splitterWindowExec.SetMinimumPaneSize(1)
        self.splitterWindowExec.SetSashGravity(0.5)
        wxID_STCSQLS = wx.NewId()
        self.stcSQLs = stc2.EditWindow(id=wxID_STCSQLS, name='stcSQLs', parent=self.splitterWindowExec1,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='SQL')
        self.stcSQLs.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnStcSQLsUpdateUI, id=wxID_STCSQLS)
        self.stcSQLs.SetScrollWidth(8000)
        self.splitterWindowExec1.SplitVertically(self.treeSQLs, self.stcSQLs)
        self.splitterWindowExec1.SetMinimumPaneSize(1)
        self.splitterWindowExec1.SetSashPosition(120)
        self.splitterWindowExec1_up = 0
        self.nbResult.SetSelection(0)
        self.nbResult.oldpos = 0
        self.txtTimeout.SetMaxLength(10)
        self.txtSplitChar.SetMaxLength(5)
        self.stcExecLog.SetMaxLength(2**20)
        self.stcExecData.SetMaxLength(2**20)
        self.statusBar_exec.SetFieldsCount(4)
        self.statusBar_exec.SetStatusWidths([-6, -3, -7, -4])
        fts = self.cfg.get_config(u'defaultfontname', u'Courier New')
        ftss = self.cfg.get_config(u'defaultfontsize', 9)
        ff = wx.Font(ftss, wx.SWISS, wx.NORMAL, wx.NORMAL, False, fts)
        for gridX in [self.gridM11,self.gridM12,self.gridM13,self.gridM21,self.gridM22,self.gridM23]:
            gridX.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_select_cell__show_pos)
            gridX.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_grid_range_selection__show_range)
            gridX.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_grid_label_left_click__sort)
            gridX.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_grid_label_right_click__autosizecol)
            gridX.Bind(wx.grid.EVT_GRID_COL_SIZE, self.on_grid_col_size__save_size)
            gridX.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_grid_cell_right_click__show_menu)
            gridX.DisableDragRowSize()
            gridX.SetColLabelSize(24)
            gridX.SetRowLabelSize(50)
            gridX.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            gridX.SetDefaultCellFont(ff)
        self.choiceConnectedDbnames.SetBackgroundColour(wx.Color(255, 192, 235))

        # python
        self.splitterWindowPython.SplitVertically(self.treePython, self.splitterWindowPython1)
        self.splitterWindowPython.SetMinimumPaneSize(30)
        self.splitterWindowPython.SetSashPosition(200)
        wxID_STCPYTHON = wx.NewId()
        self.stcPython = stc2.EditWindow(id=wxID_STCPYTHON, name='stcPython', parent=self.splitterWindowPython1,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='PYTHON')
        wxID_STCPYTHONLOG = wx.NewId()
        self.stcPythonLog = stc2.EditWindow(id=wxID_STCPYTHONLOG, name='stcPythonLog', parent=self.splitterWindowPython1,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, typestr='TEXT')
        self.splitterWindowPython1.SplitHorizontally(self.stcPython, self.stcPythonLog)
        self.splitterWindowPython1.SetMinimumPaneSize(30)

        # Button
        self.set_btn_status(False)
        self.btnFormatSpace.Disable()

        # Window, Text
        fts = self.cfg.get_config(u'defaultmonofontname', u'Courier New')
        ftss = self.cfg.get_config(u'defaultmonofontsize', 9)
        ff = wx.Font(ftss, wx.SWISS, wx.NORMAL, wx.NORMAL, False, fts)
        self.set_ctrl_font2(ff)
        fts = self.cfg.get_config(u'defaultfontname', u'Courier New')
        ftss = self.cfg.get_config(u'defaultfontsize', 9)
        ff = wx.Font(ftss, wx.SWISS, wx.NORMAL, wx.NORMAL, False, fts)
        self.set_ctrl_font(ff)
        self.time_changectrlpos.Start(100, True) #c1
        self.bind_all_ctrl_set_focus(self)

    def bind_all_ctrl_set_focus(self, win):
        ics = win.GetChildren()
        if len(ics) != 0:
            for i in ics:
                self.bind_all_ctrl_set_focus(i)
        else:
            win.Bind(wx.EVT_SET_FOCUS, self.ctrl_set_focus)

    def ctrl_set_focus(self, event):
        ''' self.ctl using by  FindReplaceDialog 's OnFind, after switch control
        @param event:
        '''
        event.Skip()
        self.ctl = self.FindWindowById(event.GetId())
        if self.ctl != self.FindFocus():
            print ' Focus ?????'

    def init_keys(self, reg=True):
        ''' register or unregister Hot Key
        @param reg: default True
        '''
        if reg:
            self.hotkeys = [ 
#                    (wx.NewId(), wx.MOD_CONTROL, wx.WXK_RETURN , self.hotkey_ctrl_return),
#                    (wx.NewId(), wx.MOD_CONTROL, wx.WXK_RETURN , self.hotkey_right),
#                    (wx.NewId(), wx.MOD_SHIFT,   wx.WXK_RETURN , self.hotkey_right),
#                    (wx.NewId(), wx.MOD_CONTROL|wx.MOD_SHIFT, wx.WXK_RETURN , self.hotkey_left),
#                    (wx.NewId(), wx.MOD_SHIFT, wx.WXK_RETURN , self.hotkey_shift_return),
#                    (wx.NewId(), wx.MOD_CONTROL, wx.WXK_F1 , self.hotkey_left),
#                    (wx.NewId(), wx.MOD_CONTROL, wx.WXK_F2 , self.hotkey_right),
                ]

            for i in self.hotkeys:
                try:
                    if self.RegisterHotKey(i[0], i[1], i[2]):
                        self.Bind(wx.EVT_HOTKEY, i[3], id=i[0])
                except Exception as _ee:
                    pass

        else:
            for i in self.hotkeys:
                try:
                    self.UnregisterHotKey(i[0])
                except Exception as _ee:
                    pass

    def hotkey_shift_return(self, event):
        nbsel = self.nbMainFrame.GetSelection()
        if nbsel == self.iSQL:
            self.OnBtnExecSqlSingleButton(None)
        else:
            pass

    def hotkey_ctrl_return(self, event):
        nbsel = self.nbMainFrame.GetSelection()
        if nbsel == self.iSQL:
            self.OnBtnExecSqlsButton(None)
        elif nbsel == self.iPYTHON:
            self.OnBtnExecPythonButton(None)
        else:
            pass

    def hotkey_left(self, event):
        pos = self.nbMainFrame.GetSelection()
        if pos > 0:
            self.nbMainFrame.SetSelection(pos - 1)
        pass

    def hotkey_right(self, event):
        pos = self.nbMainFrame.GetSelection()
        if pos < self.nbMainFrame.GetPageCount() - 1:
            self.nbMainFrame.SetSelection(pos + 1)
        pass

    def init_data(self, parent):
        # data
        print 'init data\n'
        self.str_time_strf = '%Y%m%d%H%M%S'
        fnnt = time.strftime(self.str_time_strf)
        self.sqq = open('%s_sqlx.log' % fnnt, 'ab')
        self.logsqlf = open('%s_sql.log' % fnnt, 'ab')
        self.logpgf = open('%s_pg.log' % fnnt[:8], 'ab')
        startstr = '\n---- PROGRAM START AT %s ----\n' % time.strftime(self.str_time_strf)
        self.logpgf.write(startstr)

        self.editor = 'gvim'
        self.difftool = 'gvimdiff'

        print 'self.str_encode = %s' % self.str_encode
        self.logpgf.write(' default locale = %s\n' % self.str_encode)
        if os.name == 'nt': self.NL='\r\n'
        else:               self.NL='\n'

        self.cs_time_out = 100
        self.dbs_all = []
        self.dbs_connected = []
        self.str_connectstr_split = 'ID:'
        self.cfgread_dbs()

        self.tmpdb = sqlite3.connect(':memory:')
        self.tmpcur = self.tmpdb.cursor()
        self.Obj1 = {}
        self.Obj2 = {}
        self.Obj1['dbX'] = None
        self.Obj2['dbX'] = None
        self.Obj1['type'] = self.Obj1['value'] = ''
        self.Obj2['type'] = self.Obj2['value'] = ''

        self.ctl = self.nbMainFrame
        self.tree_root = None
        self.last_dlg = self
        self.findTxt = ''
        self.gridrightclick = (0, 0)        # in show data grid right click , record row ,col
        self.write_ds = StringIO.StringIO() # in exec python
        self.python_exec_redirect_std = True
        pass

    def OnDbMClose(self, event):
        event.Skip()
        self.on_quit()
        
    def on_quit(self):
        self.init_keys(False)
        self.cfgwrite()
        self.dis_all_connect()
        stopstr = '\n---- PROGRAM STOP AT %s ----\n' % time.strftime(self.str_time_strf)
        self.logpgf.write(stopstr)
        self.logsqlf.flush()
        self.logsqlf.close()
        self.sqq.flush()
        self.sqq.close()
        if os.stat(self.logsqlf.name).st_size == 0:
            self.logpgf.write('no sql\n')
            os.remove(self.logsqlf.name)
        self.logpgf.close()
        try: self.cfg.close()
        except Exception as _ee:
            pass
        print 'exit ...'

    def OnDbMSize(self, event):
        self.time_changectrlpos.Start(100, True)
        event.Skip()

    # ------------------------------------------------------------------------
    # ---------- functions ----------
    def cfgread(self):
        self.cfg = config2.dbConfig(self.str_encode)
        self.cfg.conf_password = True

    def cfgwrite(self):
        try:
            tt = time.strftime(self.str_time_strf)
            for (stcc,ctp) in [(self.stcSQLs,'sql'), (self.stcPython,'python')]:
                le = stcc.GetLength()
                if le > 20 and le <= 2*2**20:
                    code = stcc.GetValue().strip()
                    if code != '':
                        self.cfg.snippet_table_insert(ctp, 'Autosave', tt, code)
        except Exception as ee:
            print ' EX: cfgwrite:', ee

        try:
            self.cfgwrite_dbs()
            self.cfg.commit()
        except Exception as _ee:
            pass

        try: self.logsqlf.flush()
        except Exception as _ee:
            pass
        try: self.logpgf.flush()
        except Exception as _ee:
            pass
        pass

    def cfgread_dbs(self):
        try:
            dbs, desc = self.cfg.dbinfo_select()
            self.dbs_all = dbs
            ldata = len(dbs)
            ldesc = len(desc)

            rr = self.gridDbs.GetNumberRows()
            cc = self.gridDbs.GetNumberCols()
            if rr > 0:self.gridDbs.DeleteRows(0, rr, False)
            if cc > 0:self.gridDbs.DeleteCols(0, cc, False)
            self.gridDbs.InsertRows(numRows=ldata)
            self.gridDbs.InsertCols(numCols=ldesc)
            self.gridDbs.InsertCols(ldesc, numCols=1)
            self.gridDbs.SetColLabelValue(ldesc, ' Connect Status ')
            sz = [152, 76, 178, 86, 50, 158, 190, 174, 100, 100, 100, 100]
            for j in range(ldesc):
                self.gridDbs.SetColLabelValue(j, desc[j][0])
                self.gridDbs.SetColSize(j, sz[j])
            self.gridDbs.SetColSize(ldesc, sz[ldesc])
            for i in range(self.gridDbs.GetNumberRows()):
                self.gridDbs.SetReadOnly(i, ldesc)
            for i in range(ldata):
                for j in range(ldesc):
                    try:
                        self.gridDbs.SetReadOnly(i, j)
                        if j != 4:
                            if not dbs[i][j] is None:
                                self.gridDbs.SetCellValue(i, j, dbs[i][j])
                        else:
                            if not dbs[i][j] is None and dbs[i][j] != '':
                                self.gridDbs.SetCellValue(i, j, '****')
                    except UnicodeDecodeError as ee:
                        self.log_pg(' EX: encoding: %s\n' % str(ee.args))
            for i in range(ldata):
                for j in [3, 4, 5]:
                    self.gridDbs.SetReadOnly(i, j, False)
            self.log_pg('  cfgread_dbs: read %d dbs\n' % len(dbs))
        except Exception as ee:
            self.log_pg(' In read dbs cfg: %s\n' % str(ee))
            self.dbread_error = 1
        self.gridDbs.SetSelectionMode(1)

    def cfgwrite_dbs(self, lstChd=None):
        '''write self.dbs_all data to config db userpass table
        @param lstChd: a list [ 3,4,6, ], indent self.dbs_all element
        '''
        if lstChd is None or hasattr(self, 'dbread_error'):
            return
        tt = time.strftime(self.str_time_strf)
        self.cfg.dbinfo_save(self.dbs_all, lstChd, tt)
        self.log_pg('  cfgwrite_dbs: change %d username,password\n' % len(lstChd))

    def decode(self, msg):
        if self.conf_password is None:
            return msg
        try:
            return zlib.decompress(base64.b64decode(msg))
        except Exception as _ee:
            return msg

    def encode(self, msg):
        if self.conf_password is None:
            return msg
        try:
            return base64.b64encode(zlib.compress(msg))
        except Exception as _ee:
            return msg

    def change_ctrl_pos(self):
        '''Change window layout , used on time event. cannot on window EVT_SIZE call this
        '''
        self.resize_m()
        self.resize_p_connect()
        self.resize_p_codesnippet()
        self.resize_p_procedures()
        self.resize_p_objects()
        self.resize_p_exec()
        self.resize_p_python()

    def resize_m(self):
        pass

    def resize_p_connect(self):
        pt = self.nbDbs.GetPosition()
        self.nbDbs.SetPosition(wx.Point(0, pt.y))
        psz = self.nbDbs.GetParent().GetSize()
        self.nbDbs.SetSize(wx.Size(psz.x, psz.y - pt.y))

    def resize_p_codesnippet(self):
        pt = self.splitterWindowCodeSnippet.GetPosition()
        psz = self.splitterWindowCodeSnippet.GetParent().GetSize()
        self.splitterWindowCodeSnippet.SetPosition(wx.Point(0, pt.y))
        self.splitterWindowCodeSnippet.SetSize(wx.Size(psz.x, psz.y - pt.y))

    def resize_p_procedures(self):
        pt = self.splitterWindowProcedures.GetPosition()
        psz = self.splitterWindowProcedures.GetParent().GetSize()
        self.splitterWindowProcedures.SetPosition(wx.Point(0, pt.y))
        self.splitterWindowProcedures.SetSize(wx.Size(psz.x, psz.y - pt.y))

    def resize_p_objects(self, refa=True):
        if refa:
            sts = self.statusBar_object.GetSize()
            psz = self.statusBar_object.GetParent().GetSize()
            self.statusBar_object.SetPosition(wx.Point(0, psz.y - sts.y))
            self.statusBar_object.SetSize(wx.Size(psz.x, sts.y))

            psz = self.splitterWindowObject.GetParent().GetSize()
            pt = self.staticText_Msg.GetPosition()
            sz = self.staticText_Msg.GetSize()
            self.staticText_Msg.SetSize(wx.Size(psz.x - pt.x, sz.y))

            pt = self.splitterWindowObject.GetPosition()
            self.splitterWindowObject.SetPosition(wx.Point(0, 64))
            self.splitterWindowObject.SetSize(wx.Size(psz.x - pt.x, psz.y - pt.y - sts.y))

            psz = self.splitterWindowObject1.GetSize()
            if wx.SPLIT_HORIZONTAL == self.splitterWindowObject1.GetSplitMode():
                self.splitterWindowObject1.SetSashPosition(psz.y/2)
            else:
                self.splitterWindowObject1.SetSashPosition(psz.x/2)
            psz = self.splitterWindowObject2.GetSize()
            if wx.SPLIT_HORIZONTAL == self.splitterWindowObject2.GetSplitMode():
                self.splitterWindowObject2.SetSashPosition(psz.y/2)
            else:
                self.splitterWindowObject2.SetSashPosition(psz.x/2)

        psz = self.lstT1.GetParent().GetSize()
        self.choiceDb1.SetSize(wx.Size(psz.x, 22))
        self.choiceSchema1.SetSize(wx.Size(psz.x, 22))
        self.txtI1.SetSize(wx.Size(psz.x, 22))
        pt = self.lstT1.GetPosition()
        self.lstT1.SetSize(wx.Size(psz.x, psz.y - pt.y))

        psz = self.lstT2.GetParent().GetSize()
        self.choiceDb2.SetSize(wx.Size(psz.x, 22))
        self.choiceSchema2.SetSize(wx.Size(psz.x, 22))
        self.txtI2.SetSize(wx.Size(psz.x, 22))
        pt = self.lstT2.GetPosition()
        self.lstT2.SetSize(wx.Size(psz.x, psz.y - pt.y))

    def resize_p_exec(self):
        sts = self.statusBar_exec.GetSize()
        psz = self.statusBar_exec.GetParent().GetSize()
        self.statusBar_exec.SetPosition(wx.Point(0, psz.y - sts.y))
        self.statusBar_exec.SetSize(wx.Size(psz.x, sts.y))

        pt = self.splitterWindowExec.GetPosition()
        self.splitterWindowExec.SetPosition(wx.Point(0, pt.y))
        self.splitterWindowExec.SetSize(wx.Size(psz.x, psz.y - pt.y - sts.y))

    def resize_p_python(self):
        pt = self.splitterWindowPython.GetPosition()
        psz = self.splitterWindowPython.GetParent().GetSize()
        self.splitterWindowPython.SetPosition(wx.Point(0, pt.y))
        self.splitterWindowPython.SetSize(wx.Size(psz.x, psz.y - pt.y))
        
        self.splitterWindowPython1.SetSashPosition(-200)


    def set_ctrl_font(self, ff, ff2=None):
        ''' set text list control font
        @param ff: wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        @param ff2: wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        '''
        self.txtActtime.SetFont(ff)
        self.textActsql.SetFont(ff)
        self.gridDbs.SetDefaultCellFont(ff)
        self.gridDbs.Refresh()
        self.textConnMsg.SetFont(ff)

        self.choiceConnectedDbnames.SetFont(ff)
        self.txtTimeout.SetFont(ff)
        self.txtSplitChar.SetFont(ff)
        self.treeSQLs.SetFont(ff)
        self.nbResult.SetFont(ff)
        self.stcExecLog.SetFont(ff)
        self.stcExecData.SetFont(ff)
        for i in range(2, self.nbResult.GetPageCount()):
            gridX = self.nbResult.GetPage(i)
            gridX.SetDefaultCellFont(ff)

        self.lstProcedures.SetFont(ff)
        self.textProcedures.SetFont(ff)

        self.choiceType.SetFont(ff)
        self.choiceDb1.SetFont(ff)
        self.choiceDb2.SetFont(ff)
        self.choiceSchema1.SetFont(ff)
        self.choiceSchema2.SetFont(ff)
        self.txtI1.SetFont(ff)
        self.txtI2.SetFont(ff)
        self.lstT1.SetFont(ff)
        self.lstT2.SetFont(ff)
        self.nbM1.SetFont(ff)
        self.nbM2.SetFont(ff)
        self.gridM11.SetDefaultCellFont(ff)
        self.gridM12.SetDefaultCellFont(ff)
        self.gridM13.SetDefaultCellFont(ff)
        self.gridM21.SetDefaultCellFont(ff)
        self.gridM22.SetDefaultCellFont(ff)
        self.gridM23.SetDefaultCellFont(ff)

        self.treeCodeSnippet.SetFont(ff)
        self.textCodeSnippet.SetFont(ff)

        self.treePython.SetFont(ff)
        dc = wx.MemoryDC()
        fontinfo = dc.GetFullTextExtent('e', ff)
        self.fontw = fontinfo[0] + fontinfo[3] - 1
        self.fonth = fontinfo[1]

    def set_ctrl_font2(self, ff, ff2=None):
        fn = ff.GetFaceName()
        fs = ff.GetPointSize()
        FACES3 = stc2.FACES
        FACES3['size'] = fs
        FACES3['mono'] = fn
        self.stcSQLs.setStyles(FACES3)
        self.stcExecLog.setStyles(FACES3)
        self.stcExecData.setStyles(FACES3)
        self.stcM1.setStyles(FACES3)
        self.stcM2.setStyles(FACES3)
        self.stcPython.setStyles(FACES3)
        self.stcPythonLog.setStyles(FACES3)

    def set_btn_status(self, status=False):
        '''Set Control status,
        @param status: True/False
        '''
        if status:
            self.SetTitle(u'[%s] db2 tool' % self.choiceConnectedDbnames.GetStringSelection())
            if self.icon_conn16: self.SetIcon(self.icon_conn16)
            if self.icon_conn32: self.SetIcon(self.icon_conn32)
            self.textConnMsg.SetEditable(False)

            # Exec
            self.btnExecSqls.Enable()
            self.btnExecSqlSingle.Enable()
            self.btnCommit.Enable()
            self.btnRollback.Enable()
            #self.stcExecLog.SetEditable(False)
            #self.stcExecData.SetEditable(False)
            # proc n
            self.btnListprocs.Enable()
            self.btnCallProc.Enable()
            # Compare
            self.choiceType.Enable()
            self.choiceDb1.Enable()
            self.choiceDb2.Enable()
            self.choiceSchema1.Enable()
            self.choiceSchema2.Enable()
            self.txtI1.Enable()
            self.txtI2.Enable()
            self.lstT1.Enable()
            self.lstT2.Enable()
            self.btnExportDDL.Enable() #
            self.btnCompare.Enable()
        else:
            self.SetTitle(u'db2tool: no connect')
            if self.icon_noconn16: self.SetIcon(self.icon_noconn16)
            if self.icon_noconn32: self.SetIcon(self.icon_noconn32)
            self.textConnMsg.SetEditable(True)
            # Exec
            self.btnExecSqls.Disable()
            self.btnExecSqlSingle.Disable()
            self.btnCommit.Disable()
            self.btnRollback.Disable()
            #self.stcExecLog.SetEditable(True)
            #self.stcExecData.SetEditable(True)
            # proc n
            self.btnListprocs.Disable()
            self.btnCallProc.Disable()
            # Compare
            self.choiceType.Disable()
            self.choiceDb1.Disable()
            self.choiceDb2.Disable()
            self.choiceSchema1.Disable()
            self.choiceSchema2.Disable()
            self.txtI1.Disable()
            self.txtI2.Disable()
            self.lstT1.Disable()
            self.lstT2.Disable()
            self.btnExportDDL.Disable()
            self.btnFormatSpace.Disable()
            self.btnCompare.Disable()

    def init_dbtree(self):
        ''' test
        - if connect to a database,  list db's object
        '''
        self.clear_tree()
        self.tree_root = self.treeCodeSnippet.AddRoot("no any")
        # tree
#        isz = (16,16)
#        il = wx.ImageList(isz[0], isz[1])
#        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
#        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
#        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
#        smileidx    = il.Add(images.Smiles.GetBitmap())

#        self.treeCodeSnippet.SetImageList(il)
#        self.il = il

        # or use dictionary ,
        self.dbcons = [
            'TABLESPACES',  """select * from syscat.tablespaces """,
            'USER',         """select * from syscat.tablespaces """,
            'FUNCTION',     """select * from syscat.functionss """,
            'TABLE',        """select * from syscat.tabless """,
            'VIEW',         """select * from syscat.views """,
            'PROCEDURE',    """select * from syscat.proecedures """,
            'SERVER',       """select * from syscat.servers """,
            'MAPPING',      """select * from syscat.mappings """,
            'NICKNAME',     """select * from syscat.nicknames """
        ]

        #self.tree_root = treeCodeSnippet.AddRoot("Databases")
        self.treeCodeSnippet.SetItemText(self.tree_root, u"Databases")
        self.treeCodeSnippet.SetPyData(self.tree_root, None)
#        treeCodeSnippet.SetItemImage(self.tree_root, fldridx, wx.TreeItemIcon_Normal)
#        treeCodeSnippet.SetItemImage(self.tree_root, fldropenidx, wx.TreeItemIcon_Expanded)
        for i in range(0, len(self.dbcons), 2):
            child = self.treeCodeSnippet.AppendItem(self.tree_root, self.dbcons[i])
            self.treeCodeSnippet.SetPyData(child, None)
            self.treeCodeSnippet.SetPyData(child, None)
#            treeCodeSnippet.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
#            treeCodeSnippet.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)
            self.treeCodeSnippet.AppendItem(child, u"AA")
            self.treeCodeSnippet.SetPyData(child, None)
            self.treeCodeSnippet.AppendItem(child, u"BB")
            self.treeCodeSnippet.SetPyData(child, None)
            self.treeCodeSnippet.AppendItem(child, self.dbcons[i + 1])
            self.treeCodeSnippet.SetPyData(child, None)

        self.treeCodeSnippet.Expand(self.tree_root)

    def clear_tree(self):
        self.treeCodeSnippet.DeleteAllItems()
        pass

    def OnTime_KeepActive(self, event):
        '''keep connect active time event
        @param event:
        '''
        if event: event.Skip()
        dbX = self.get_db2db_from_connect_string()
        tt = ''
        lconn = len(self.dbs_connected)

        asql = self.textActsql.GetValue().encode(self.str_encode)
        fail_ids = []
        for i in range(len(self.dbs_connected)):
            item = self.dbs_connected[i]
            db = item[self.iDB]
            cs = item[self.iCS]
            #node = item[self.iNODE]
            #dbname = item[self.iDBNAME]
            #dbuser = item[self.iDBUSER]
            id_db = id(db)
            try:
                cs.execute(asql)
                f = cs.fetchall()
                #self.log_pg(' %s - %s (%s) Keep connect Active at %s\n' % (node, dbname, dbuser, f[0][0]))
                if dbX.id_db == id_db: tt = f[0][0]
            except DB2.Error as _ee:# as ee:
                try:
                    cs.close()
                    db.close()
                except Exception as _ee:
                    pass
                fail_ids.insert(0, i)
                #self.log_pg(' %s - %s (%s) Error: %s %s %s\n' % (node, dbname, dbuser, ee.args[0], ee.args[1], ee.args[2]))
            except Exception as _ee:# as ee:
                #self.log_pg(' %s - %s (%s) Error: %s\n' % (node, dbname, dbuser, ee))
                pass

        for i in range(len(fail_ids)):
            try:
                #print ' remove: %s ' % fail_ids[i]
                self.dbs_connected.pop(fail_ids[i])
            except Exception:# as ee:
                #print ' --- UNKNOW  UNKNOW UNKNOW ---- %s ------' % ee
                pass

        if len(self.dbs_connected) != lconn:
            self.refresh_choice_and_set_btnstatus(True, u'actt lost connect')
        
        msg = '%s-%s(%s) %s' % (dbX.node, dbX.dbname, dbX.dbuser, tt)
        msg = msg.decode(self.str_encode)
        self.statusBar_exec.SetStatusText(msg, 3)

    def OnTime_ChangeCtrlPos(self, event):
        if event: event.Skip()
        self.time_changectrlpos.Stop()
        self.change_ctrl_pos()

    def get_stc_from_current_page(self):
        '''
        @return: stc control from current selected main Frame
        '''
        nbsel = self.nbMainFrame.GetSelection()
        if nbsel == self.iSQL:
            return self.stcSQLs
        elif nbsel == self.iPROCEDURES:
            return self.textProcedures
        elif nbsel == self.iCODESNIPPET:
            return self.textCodeSnippet
        elif nbsel == self.iPYTHON:
            return self.stcPython
        else:
            return self
        
    def OnTime_SetEditFocus(self, event):
        if event: event.Skip()
        self.time_seteditfocus.Stop()
        self.get_stc_from_current_page().SetFocus()

    def OnNbMainFrameNotebookPageChanged(self, event):
        self.time_seteditfocus.Start(100, True)
        event.Skip()
        pass

    # ------------------------------------------------------------------------
    # ---------- connect page ----------
    def OnBtnSaveDbsButton(self, event):
        self.cfgwrite()
        event.Skip()

    def get_db2_catalog(self, typestr):
        ''' db2 list  node / db  directory
        @param typestr: 'node' or 'db'
        '''
        if str(typestr).lower() == 'node':
            cmd = 'db2 list node directory'
        elif str(typestr).lower() == 'db':
            cmd = 'db2 list db directory'
        else:
            print 'unknow typestr'
            return []

        lls = ''
        ss = subprocess.Popen('%s ' % (cmd), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        lls = ss.stdout.read()
        if len(lls) == 0:
            print ' read error'
            return []
        lls = lls.split('\n')
        ii, iLines = 0, len(lls)
        for i in range(ii, iLines):
            part = lls[i].split('=')
            if len(part) == 2:
                try:    iItems=int(part[1])
                except: return []
                ii = i + 1
                break
        if iItems == 0: return []

        items = []
        iit = int((iLines - ii) / iItems)
        iit2 = (iLines - ii) % iItems
        for i in range(iItems):
            item = []
            for j in range(iit):
                part = lls[ii+iit2 + i*iit +j].split('=')
                if len(part) == 2:
                    msg = part[1].strip()
                    msg = msg.decode(self.str_encode)
                    item.append(msg)
            items.append(item)
        print '"%s"' % cmd
        print iItems, len(items)
        return items


    def func_dbs_connected_sort(self, L, R):
        try:
            nl, dl, ul = L[self.iDB], L[self.iDBNAME], L[self.iDBUSER]
            nr, dr, ur = R[self.iDB], R[self.iDBNAME], R[self.iDBUSER]
            if nl == nr:
                if dl == dr:
                    return cmp(ul, ur)
                else:
                    return cmp(dl, dr)
            else:
                return cmp(nl, nr)
        except Exception as _ee:
            return 0

    def OnGridDbsGridCellChange(self, event):
        event.Skip()
        row, col = event.GetRow(), event.GetCol()
        new_value = self.gridDbs.GetCellValue(row, col)

        chd = []
        self.dbs_all[row][col] = new_value
        if col == 4: self.gridDbs.SetCellValue(row, 4, u'****')
        chd.append(row)

        nodeval = self.gridDbs.GetCellValue(row, 1)
        for i in range(self.gridDbs.GetNumberRows()):
            if i == row: continue
            if nodeval == self.dbs_all[i][1] and self.dbs_all[i][col] == u'':
                self.dbs_all[i][col] = new_value
                if col == 4:self.gridDbs.SetCellValue(i, 4, u'****')
                else:       self.gridDbs.SetCellValue(i, col, new_value)
                chd.append(i)
        self.cfgwrite_dbs(chd)

    def OnGridDbsGridCellRightClick(self, event):
        ''' self.gridDbs    wx.grid.EVT_GRID_CELL_RIGHT_CLICK '''
        event.Skip()
        iRow, iCol = event.GetRow(), event.GetCol()
        self.db2_connect_or_disconnect(iRow, iCol)

    def db2_connect_or_disconnect(self, iRow, iCol):
        lconn = len(self.dbs_connected)
        gridX = self.nbDbs.GetPage(0)
        self.gridDbs.SetFocus()
        self.gridDbs.SelectRow(iRow)

        assert len(self.dbs_all) >= gridX.GetNumberRows()
        node = gridX.GetCellValue(iRow, 1)
        dbname = gridX.GetCellValue(iRow, 2).split(u' [')[0]
        dbuser = gridX.GetCellValue(iRow, 3)
        password = self.dbs_all[iRow][4]
        comment = gridX.GetCellValue(iRow, 5)
        if dbuser == u'' or password == u'':
            wx.MessageBox(_('No user or password !'), _('Error'), wx.OK | wx.ICON_ERROR, self.last_dlg)
            return

        iConmsgCol = self.gridDbs.GetNumberCols() - 1
        connstr = gridX.GetCellValue(iRow, iConmsgCol)
        self.gridDbs.Refresh()

        if connstr.find(self.str_connectstr_split) == -1: #no connect
            if wx.YES != wx.MessageBox(u'''db2 connect to %s user %s using ******\n\nUSE  "%s"  CONNECT TO  "%s"  'S  "%s [%s]"  ?''' \
                 % (dbname, dbuser, dbuser, node, dbname, comment), _('connect database ?'), wx.YES_NO | wx.ICON_QUESTION, self.last_dlg):
                return

            try:
                dlg = wx.ProgressDialog(_('connect ...'), u' db2 connect to %s user %s using ****' % (dbname, dbuser), 100, self, style=wx.PD_ELAPSED_TIME)
                dlg.Update(50)
                db = DB2.connect(dsn=dbname, uid=dbuser, pwd=password)
                cs = db.cursor()
                cs.set_timeout(1)
            except DB2.Error as ee:
                msg = '%s' % ee.args[2]
                tap = '%s, %s' % (ee.args[0], ee.args[1])
                self.log_pg('%s, %s%s\n' % (tap, msg, '--' *50))
                wx.MessageBox(msg.decode(self.str_encode), tap.decode(self.str_encode), wx.OK | wx.ICON_ERROR, dlg)
                return
            except Exception as ee:
                wx.MessageBox(str(ee).decode(self.str_encode), u'Exception', wx.OK | wx.ICON_ERROR, dlg)
                return
            finally:
                dlg.Destroy()

            '''227,227,227, 207,235,248, 244,252,203, 253,202,241, 219,234,236, 243,211,220, 253,202,239'''
            id_db = id(db)
            color = wx.Color(random.randint(200,255), random.randint(200,255), random.randint(200,255))
            self.dbs_connected.append([db, cs, node.encode(self.str_encode), dbname.encode(self.str_encode),
                   dbuser.encode(self.str_encode), password.encode(self.str_encode), comment.encode(self.str_encode), color])
            # column order
            self.iDB, self.iCS, self.iNODE, self.iDBNAME = 0, 1, 2, 3
            self.iDBUSER, self.iPASSWORD, self.iCOMMENT, self.iCOLOR = 4, 5, 6, 7

            gridX.SetCellValue(iRow, iConmsgCol, u'%d connect ID:%s' % (iRow + 1, id_db))
            gridX.SetReadOnly(iRow, iConmsgCol)

            self.log_pg('db2 connect to %s user %s using *******\n' % (dbname.encode(self.str_encode), dbuser.encode(self.str_encode)))
            cs.execute('''select current timestamp from syscat.tables fetch first 1 rows only''')
            f = cs.fetchall()
            self.log_pg('    %s\n  success at %s  [%s]\n' % (db.__str__(), f[0][0], id_db))

            conn_color = wx.Color(0, 255, 0)
            for col in range(self.gridDbs.GetNumberCols()):
                self.gridDbs.SetCellBackgroundColour(iRow, col, conn_color)
            self.gridDbs.Refresh()
        else: # connect reset
            if wx.YES != wx.MessageBox(u'db2 connect reset ? ', _('disconnect database ? '),
                                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION, self.last_dlg):
                return

            id_str = int(connstr.split(self.str_connectstr_split)[1])
            try:
                dlg = wx.ProgressDialog(_('disconnect ...'), u' db2 connect reset [      ]', 100, self, style=wx.PD_ELAPSED_TIME)
                for i in range(len(self.dbs_connected)):
                    item = self.dbs_connected[i]
                    db, cs, id_db = item[self.iDB], item[self.iCS], id(item[self.iDB])
                    if id_db == id_str:
                        try:
                            try:
                                msgs = '%s' % item[self.iDBNAME]
                                msgs = msgs.decode(self.str_encode)
                            except Exception as _ee:
                                msgs = u' db2 connect reset [ ?? ]'
                            dlg.Update(50, msgs)
                            cs.close()
                            db.close()
                        except Exception as _ee:
                            pass
                        self.dbs_connected.pop(i)
                        break
            finally:
                dlg.Destroy()
            self.log_pg('\ndb2 connect reset  [%s]\n%s\n' % (id_str, '=='*50))
            gridX.SetCellValue(iRow, iConmsgCol, u'no connect')

            for col in range(self.gridDbs.GetNumberCols()):
                self.gridDbs.SetCellBackgroundColour(iRow, col, self.gridDbs_bgc)
            self.gridDbs.Refresh()

        # status
        self.gridDbs.SelectBlock(iRow, iCol, iRow, iCol)
        if len(self.dbs_connected) != lconn:
            self.refresh_choice_and_set_btnstatus()
        self.log_pg('\n')

    def refresh_choice_and_set_btnstatus(self, changeGridStatus=False, connstr=u'no connect'):
        ''' Refresh ChoiceList dbnames , Set Btnstatus, Changed ListGrid db connect status
        @param changeGridStatus:  default is False
        @param connstr: u'no connect'
        '''
        if changeGridStatus:
            ids = [id(i[self.iDB]) for i in self.dbs_connected]
            reset_lines = []
            iCol = self.gridDbs.GetNumberCols()
            for row in range(self.gridDbs.GetNumberRows()):
                connstrl = self.gridDbs.GetCellValue(row, iCol - 1).split(self.str_connectstr_split)
                if len(connstrl) >= 2:
                    try:
                        if not int(connstrl[1]) in ids: reset_lines.append(row)
                    except Exception as _ee:
                        pass
            for row in reset_lines:
                for col in range(iCol):
                    self.gridDbs.SetCellBackgroundColour(row, col, self.gridDbs_bgc)
                self.gridDbs.SetCellValue(row, iCol - 1, connstr)

        # refresh choice
        self.dbs_connected.sort(self.func_dbs_connected_sort)
        its1 = ['%s %s (%s) - %s - \tID:%d' % (i[self.iDBNAME], '- %s -' % i[self.iCOMMENT] if len(i[self.iCOMMENT])>0 else '', \
                                    i[self.iDBUSER], i[self.iNODE], id(i[self.iDB])) for i in self.dbs_connected]
        its = [it.decode(self.str_encode) for it in its1 ]
        self.choiceConnectedDbnames.Clear()
        self.choiceConnectedDbnames.AppendItems(its)
        for obj in [self.choiceDb1, self.choiceDb2]:
            oriselstr = obj.GetStringSelection()
            obj.Clear()
            obj.AppendItems(its)
            obj.SetStringSelection(oriselstr)
        if self.choiceDb1.GetSelection() == -1: self.Obj1['dbX']=None
        if self.choiceDb2.GetSelection() == -1: self.Obj2['dbX']=None

        if len(self.dbs_connected) == 0:
            self.set_btn_status(False)
            self.time_keepactive.Stop()
        else:
            self.set_btn_status(True)
            t = self.txtActtime.GetValue()
            try:    self.time_keepactive.Start(int(t) * 1000)
            except: self.time_keepactive.Start(180000)

    def get_db2db_from_connect_string(self, connstr=u'', newcs=False):
        '''
        @param connstr: choice 's string, if None get selected string from self.choiceConnectedDbnames
        @param newcs: default False,  from db create new cursor
        @return  ( Db2db() = dbname, dbuser, password, db, cs } )
        '''
        db2db = Db2db()
        if connstr == u'':
            connstr = self.choiceConnectedDbnames.GetStringSelection()
        if connstr.find(self.str_connectstr_split) == -1:
            return db2db
        id_str = int(connstr.split(self.str_connectstr_split)[1])
        for i in range(len(self.dbs_connected)):
            item = self.dbs_connected[i]
            if id(item[self.iDB]) == id_str:
                db2db.node = item[self.iNODE]
                db2db.id_db = id(item[self.iDB])
                db2db.db = item[self.iDB]
                if newcs:
                    db2db.cs = item[self.iDB].cursor() # new cursor
                else:
                    db2db.cs = item[self.iCS]
                db2db.dbname = item[self.iDBNAME]
                db2db.dbuser = item[self.iDBUSER]
                db2db.color = item[self.iCOLOR]
                break
        return db2db

    def dis_all_connect(self):
        ''' disconnect all
        - default used on process exit, no change choice_dbs values and button status
        '''
        try:
            dlg = wx.ProgressDialog(_('disconnect ...'), u'db2 connect reset [        ]',
                                    len(self.dbs_connected), self, style=wx.PD_ELAPSED_TIME)
            ixx = -1
            for i in range(len(self.dbs_connected)):
                it = self.dbs_connected[i]
                try:
                    ixx += 1
                    try:
                        msgs = 'db2 connect reset ... [%s]' % it[self.iDBNAME]
                        msgs = msgs.decode(self.str_encode)
                    except Exception:
                        msgs = u'db2 connect reset ... [ ?? ]'
                    dlg.Update(ixx, msgs)
                    it[self.iCS].close()
                    it[self.iDB].close()
                    print ' Disconnect %s' % id(it[self.iDB])
                except Exception as _ee:
                    pass
            self.dbs_connected = []
        finally:
            dlg.Destroy()

    def OnBtnFontButton(self, event):
        event.Skip()
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(self.textConnMsg.GetForegroundColour())
        data.SetInitialFont(self.textConnMsg.GetFont())
        dlg = wx.FontDialog(self, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetFontData()
                font = data.GetChosenFont()
                ff=wx.Font(font.GetPointSize(),wx.SWISS,wx.NORMAL,wx.NORMAL,False,font.GetFaceName())
                self.set_ctrl_font(ff, ff)
                self.cfg.save_config(u'defaultfontname', font.GetFaceName())
                self.cfg.save_config(u'defaultfontsize', font.GetPointSize())
        finally:
            dlg.Destroy()

        data.SetColour(self.textConnMsg.GetForegroundColour())
#        data.SetInitialFont(stc2.FACES['mono'])
        dlg = wx.FontDialog(self, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetFontData()
                font = data.GetChosenFont()
                colour = data.GetColour()
                colour.Get()
                ff=wx.Font(font.GetPointSize(),wx.SWISS,wx.NORMAL,wx.NORMAL,False,font.GetFaceName())
                self.set_ctrl_font2(ff, ff)
                #self.stcSQLs.SetBackgroundColour(colour.Get())
                #self.stcSQLs.SetBackgroundColour(colour.Get())
                self.cfg.save_config(u'defaultmonofontname', font.GetFaceName())
                self.cfg.save_config(u'defaultmonofontsize', font.GetPointSize())
        finally:
            dlg.Destroy()

    def OnBtnRefreshDbButton(self, event):
        self.dis_all_connect()
        self.refresh_choice_and_set_btnstatus()
        self.set_btn_status(False)
        self.cfgread_dbs()
        event.Skip()

    def OnBtnRefreshDbsButton(self, event):
        event.Skip()
        dlg = wx.ProgressDialog(_('Please waiting ...'), _(' Rescan system DB2 catalog directory ... '),
                                100, self, style=wx.PD_ELAPSED_TIME)
        try:
            dlg.Update(50)
            nodes = self.get_db2_catalog('node')
            dbs = self.get_db2_catalog('db')
        finally:
            dlg.Destroy()
        tts = time.strftime(self.str_time_strf)
        if len(nodes) > 0:
            self.cfg.nodes_table_reset(nodes, tts)
        if len(dbs) > 0:
            self.cfg.dbs_table_reset(dbs, tts)

        self.cfgread_dbs()

    def OnBtnDisconnectAllButton(self, event):
        event.Skip()
        if wx.YES != wx.MessageBox(_(' Disconnect All  ??'), _('Ask'), 
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION, self.last_dlg):
            return
        self.dis_all_connect()
        self.set_btn_status(False)
        self.refresh_choice_and_set_btnstatus(True, u'disconned')

    def OnTextConnMsgLeftDclick(self, event):
        self.textConnMsg.Clear()
        event.Skip()

    # ------------------------------------------------------------------------
    # ----------  code snippet page ----------
    def OnButton4Button(self, event):
        self.remove_page_grid()
        event.Skip()

    # ------------------------------------------------------------------------
    # ---------- procedures page  ----------
    def OnBtnListprocsButton(self, event):
        event.Skip()
        dbX = self.get_db2db_from_connect_string()
        if not dbX.cs: return
        try:
            dbX.cs.execute('''select procschema,procname from syscat.procedures
            where procschema not like 'SYS%' and procschema not like 'SQLJ%'
            order by procschema,procname
            ''')
        except Exception as _ee:
            self.textProcedures.AppendText('eoor')
            return

        fd = dbX.cs.fetchall()
        ii = self.lstProcedures.GetCount()
        self.lstProcedures.Clear()
        msgs = [u'%s.%s' % (f[0].decode(self.str_encode).rstrip(), f[1].decode(self.str_encode).rstrip()) for f in fd]
        self.lstProcedures.InsertItems(msgs, 0)


    def OnBtnCallProcButton(self, event):
        event.Skip()
        print self.textProcedures.GetStringSelection()

    def OnLstProceduresChecklistbox(self, event):
        si = event.GetSelection()
        if self.lstProcedures.IsChecked(si):
            self.textProcedures.AppendText(u'\ncall %s ;\n' % self.lstProcedures.GetString(si))
        else:
            n = self.lstProcedures.GetString(si)
            sa = self.textProcedures.GetValue()
            sa = sa.replace(u'\ncall %s ;\n' % n, u'\n-- call %s ;\n' % n)
            self.textProcedures.Clear()
            self.textProcedures.SetValue(sa)
        event.Skip()

    # ------------------------------------------------------------------------
    # ---------- execute page ----------
    def OnStcSQLsUpdateUI(self, event):
        event.Skip()
        if self.stcSQLs.GetSelectionStart() == self.stcSQLs.GetSelectionEnd():
            self.btnExecSqls.Disable()
            self.btnExecSqlSingle.Disable()
        else:
            self.btnExecSqls.Enable()
            self.btnExecSqlSingle.Enable()

    def set_commit_btn_status(self, IsChanged=True):
        bcolor = self.btnExecPython.GetBackgroundColour()
        if IsChanged:
#            self.btnExecSqls.Disable()
#            self.btnExecSqlSingle.Disable()
#            self.btnCommit.Enable()
#            self.btnRollback.Enable()
            self.btnCommit.SetBackgroundColour(wx.Color(0, 255, 0))
            self.btnRollback.SetBackgroundColour(wx.Color(255, 0, 0))
        else:
#            self.btnExec2.Enable()
#            self.btnExec3.Enable()
#            self.btnCommit.Disable()
#            self.btnRollback.Disable()
            self.btnCommit.SetBackgroundColour(bcolor)
            self.btnRollback.SetBackgroundColour(bcolor)
        pass

    def on_grid_label_right_click__autosizecol(self, event):
        gridX = self.FindWindowById(event.GetId())
        col = event.GetCol()
        #gridX.SetColSize(col, gridX.description2[col][2] * self.fontw)
        if len(gridX.GetTable().data) < 100000:
            gridX.AutoSizeColumn(col, False)
            gridX.ForceRefresh()

    def on_grid_label_left_click__sort(self, event):
        '''sort col value'''
        gridX = self.FindWindowById(event.GetId())
        col = event.GetCol()
        if col != -1:
            dlg = wx.ProgressDialog(_('Please waiting ...'), _('Sort data, Please waiting ... '), 100, self, style=wx.PD_ELAPSED_TIME)
            dlg.Update(50)
            data = gridX.GetTable().data
            desc = gridX.GetTable().desc
            if gridX.issort:
                if gridX.sortcol == col:
                    if desc[gridX.sortcol][-5:] == ' (UP)':
                        data.sort(key=lambda x:x[col], reverse=True)
                        desc[gridX.sortcol] = desc[gridX.sortcol][:-5] + ' (DN)'
                    else:
                        data.sort(key=lambda x:x[col])
                        desc[gridX.sortcol] = desc[gridX.sortcol][:-5] + ' (UP)'
                else:
                    data.sort(key=lambda x:x[col])
                    desc[gridX.sortcol] = desc[gridX.sortcol][:-5]
                    gridX.sortcol = col
                    desc[gridX.sortcol] = desc[gridX.sortcol] + ' (UP)'
            else:
                gridX.issort = True
                data.sort(key=lambda x:x[col])
                gridX.sortcol = col
                desc[gridX.sortcol] = desc[gridX.sortcol] + ' (UP)'

            gridX.Refresh()
            dlg.Destroy()
        pass

    def on_grid_col_size__save_size(self, event):
        ''' save tabname column size '''
        col = event.GetRowOrCol()
        gridX = self.FindWindowById(event.GetId())
        if gridX.tabname.find('?') == -1:
            try:
                colname = gridX.GetTable().desc[col]
                if gridX.issort and gridX.sortcol == col:
                    colname = colname[:-5]
                self.cfg.colsize_delete(gridX.tabname, colname, False)
                self.cfg.colsize_insert(gridX.tabname, colname, gridX.GetColSize(col), True)
            except Exception as ee:
                print ' EX: on_grid_col_size__save_size:', ee
                pass


    def on_grid_select_cell__show_pos(self, event):
        event.Skip()
        gridX = self.FindWindowById(event.GetId())
        if gridX in [self.gridM11, self.gridM12, self.gridM13, self.gridM21, self.gridM22, self.gridM23]:
            startbar =   self.statusBar_object
        else:startbar = self.statusBar_exec
        row, col = event.GetRow(), event.GetCol()
        try:
            startbar.SetStatusText(u'%d , %d' % (row + 1, col + 1), 1)
            tag = '%s:%s.%s: ' % (gridX.dbname, gridX.tabschema, gridX.tabname)
            msg = '/'.join([str(i) for i in gridX.description2[col]])
            startbar.SetStatusText(tag.decode(self.str_encode)+msg.decode(self.str_encode), 2)
        except Exception as ee:
            print ' EX: on_grid_select_cell__show_pos:', ee

    def on_grid_range_selection__show_range(self, event):
        event.Skip()
        gridX = self.FindWindowById(event.GetId())
        if gridX in [self.gridM11, self.gridM12, self.gridM13, self.gridM21, self.gridM22, self.gridM23]:
            startbar =   self.statusBar_object
        else:startbar = self.statusBar_exec
        #print gridX.dbname, gridX.dbuser, gridX.tabname, gridX.sql, gridX.resmsg
        LT = gridX.GetSelectionBlockTopLeft()
        BR = gridX.GetSelectionBlockBottomRight()
        try:
            if len(LT) > 0 and len(BR) > 0:
                msg = '%s, %s [%d, %d]' % (LT[0], BR[0], BR[0][0] - LT[0][0] + 1 , BR[0][1] - LT[0][1] + 1)
                startbar.SetStatusText(msg.decode(self.str_encode), 1)
        except Exception as ee:
            print ' EX: on_grid_range_selection__show_range:', ee

    # -------- grid context menu --------
    def popup2_ExportSQL(self, event):
        self.stcSQLs.SetFocus()
        self.export_data(1,self.gridX)

    def popup2_ExportDEL(self, event):
        self.stcSQLs.SetFocus()
        self.export_data(2,self.gridX)

    def popup2_ExportIXF(self, event):
        self.stcSQLs.SetFocus()
        self.export_data(3,self.gridX)

    def popup2_SelectAll(self, event):
        gridX = self.gridX
        gridX.SelectAll()

    def popup2_Find(self, event):
        gridX = self.gridX
        row, col = self.gridrightclick
        data = gridX.GetTable().data
        desc = gridX.description2[col]
        descstr = '"%s" (%s/%s)' % (desc[0],desc[1],desc[2])
        descstr = descstr.decode(self.str_encode)
        if hasattr(self,'str_search'):
            ss = self.str_search
        else:
            ss = data[row][col]
            if ss is None:
                ss = u''
            elif type(ss) == type(''):
                ss = ss.decode(self.str_encode)
        dlg = wx.TextEntryDialog(self.last_dlg, u'Search Text In Column %s :' % descstr, _('Input:'), ss, style=wx.OK | wx.CANCEL)
        try:
            if wx.ID_OK == dlg.ShowModal():
                self.str_search = dlg.GetValue()
                s = self.str_search.encode(self.str_encode)
                if s == '':
                    return
                s = s.replace('*','.*').replace('?','.')
                for i in range(row + 1, len(data)):
                    if re.match(s, str(data[i][col]), re.IGNORECASE):
                        gridX.SelectBlock(i, col, i, col)
                        gridX.SetGridCursor(i, col)
                        gridX.MakeCellVisible(i, col)
                        return
                for i in range(0, row + 1):
                    if re.match(s, str(data[i][col]), re.IGNORECASE):
                        gridX.SelectBlock(i, col, i, col)
                        gridX.SetGridCursor(i, col)
                        gridX.MakeCellVisible(i, col)
                        return
                wx.MessageBox(u' Not Find "%s" !' % self.str_search, parent=self.last_dlg)
        finally:
            dlg.Destroy()
            gridX.SetFocus()

    def popup2_CopyLineSQL(self, event):
        self.copy_value_thread(self.copy_line_sql)
        
    def copy_value_thread(self, function):
        t1 = time.time()
        progress = [-1, 100, False]  # pos, count, Break
        th = threading.Thread(target=function, args=((progress,)))
        th.start()
        dlg = wx.ProgressDialog(_('Please waiting ...'), _('On copy value ( %d / %d ) ...') % (progress[0],progress[1]),
                    100, self.last_dlg, style=wx.PD_ELAPSED_TIME|wx.PD_CAN_ABORT)
        try:
            while True:
                th.join(0.4)
                if th.isAlive():
                    if dlg:
                        if not progress[2]:
                            msg = _('On copy value ( %d / %d ) ...') % (progress[0], progress[1])
                        else:
                            msg = _('On copy ( %d / %d ) , CANCELED ...') % (progress[0], progress[1])
                        cont =  dlg.Update(int(progress[0]*100/progress[1]), msg)[0]
                        if not cont and not progress[2]:
                            progress[2] = True
                else:
                    break
        finally:
            if dlg: dlg.Destroy()
        print ' copy', progress[1], 'lines used time:', time.time() - t1
                
    def copy_line_sql(self, progress):
        gridX = self.gridX
        Rows = gridX.GetSelectedRows()
        if len(Rows) <= 0: return
        data = gridX.GetTable().data
        desc = gridX.description2
        tabschema = gridX.tabschema
        tabname = gridX.tabname
        cols = len(desc)

        inss = ''
        for col in range(cols):
            inss += """, %s""" % desc[col][0]
        inss = inss[2:]
        rl = '%s ' % self.NL if len(inss) > 80 else ''
        inssqls = StringIO.StringIO()
        progress[1] = len(Rows)
        for row in Rows:
            if progress[2]: break
            progress[0] += 1
            v = ''
            for col in range(cols):
                if not data[row][col] is None:
                    if desc[col][1] in ['INTEGER', 'SMALLINT', 'BIGINT', 'INT']:
                        v += ', %d' % data[row][col]
                    elif desc[col][1] in ['DECIMAL', 'REAL', 'DOUBLE']:
                        v += ', %f' % data[row][col]
                    else:
                        v += """, '%s'""" % str(data[row][col]).replace("'", "''")
                else:
                    v += ', NULL'
            inssqls.write('insert into %s.%s ( %s )%s values ( %s ) ;%s' % (tabschema, tabname, inss, rl, v[2:], self.NL))
        self.copy_text_to_clipboard(inssqls)

    def popup2_CopyCondSelectSQL(self, event):
        self.copy_value_thread(self.copy_cond_sql)
        
    def copy_cond_sql(self, progress):
        gridX = self.gridX
        print gridX.dbname, gridX.dbuser, gridX.tabname, gridX.sql, gridX.resmsg
        print gridX.GetSelectedCells()
        print gridX.GetSelectedRows()
        print gridX.GetSelectedCols()
        TL = gridX.GetSelectionBlockTopLeft()
        RB = gridX.GetSelectionBlockBottomRight()
        if len(TL) <= 0 or len(RB) <=0:
            return
        ds = StringIO.StringIO()
        if RB[0][1] - TL[0][1] > 1:
            pass    #TODO
#            for i in range(TL[0][0], RB[0][0]+1):
#                ls = ''
#                for j in range(TL[0][1], RB[0][1]+1):
#                    ls += ',%s' % gridX.GetCellValue(i, j)
#                ds.write('%s%s' % (ls[1:], self.NL))
        else:
            col = TL[0][1]
            row = TL[0][0]
            row2 = row + RB[0][0] - TL[0][0] + 1
            colname = gridX.description2[col][0]
            colisnum = gridX.description2[col][1] in ['INTEGER', 'SMALLINT', 'BIGINT', 'INT', 'DECIMAL', 'REAL', 'DOUBLE']
            progress[1] = row2 - row
            for i in range(row, row2):
                if progress[2]: break
                progress[0] += 1
                s = gridX.GetCellValue(i, col)
                if colisnum:
                    ds.write("  %s,%s" % (s, self.NL))
                else:
                    ds.write("  '%s',%s" % (s, self.NL))
            self.copy_text_to_clipboard('select * from %s.%s where %s in (%s%s%s);%s' % \
                    (gridX.tabschema, gridX.tabname, colname, self.NL, ds.getvalue()[:-(len(self.NL)+1)], self.NL, self.NL))
        pass

    def popup2_Copy(self, event):
        self.copy_value_thread(self.copy_string)
        
    def copy_string(self, progress):
        gridX = self.gridX
        TL = gridX.GetSelectionBlockTopLeft()
        RB = gridX.GetSelectionBlockBottomRight()
        if len(TL) <= 0 or len(RB) <=0:
            Rows = gridX.GetSelectedRows()
            if len(Rows) <= 0:
                return
            else:
                TL.append([Rows[0], 0])
                RB.append([Rows[0], len(gridX.description2)-1])
        ds = StringIO.StringIO()
        progress[1] = RB[0][0]+1 - TL[0][0]
        for i in range(TL[0][0], RB[0][0]+1):
            if progress[2]: break
            progress[0] += 1
            ls = ''
            for j in range(TL[0][1], RB[0][1]+1):
                ls += ',%s' % gridX.GetCellValue(i, j)
            ds.write('%s%s' % (ls[1:], self.NL))
        self.copy_text_to_clipboard(ds)
        pass

    def copy_text_to_clipboard(self, text):
        xx = wx.Clipboard()
        if not xx.Open(): return
        try:
            if type(text) == type(''):
                try: text = text.decode(self.str_encode)
                except Exception as _ee:
                    pass
                xx.SetData(wx.TextDataObject(text))
            elif type(text) == type(u''):
                xx.SetData(wx.TextDataObject(text))
            else:
                try:
                    msg = text.getvalue()
                    try: msg = msg.decode(self.str_encode)
                    except Exception as _ee:
                        pass
                    xx.SetData(wx.TextDataObject(msg))
                except Exception as ee:
                    print ' EX: on copy text to clipboard except:', ee
        finally:
            xx.Flush()
            xx.Close()

    def on_grid_cell_right_click__show_menu(self, event):
        ''' show menu or add line to select '''
        event.Skip()
        gridX = self.FindWindowById(event.GetId())
        self.gridX = gridX
        row, col = event.GetRow(), event.GetCol()
        gridX.SetGridCursor(row, col)
        self.gridrightclick = (row, col)
        if event.ShiftDown():
            gridX.SelectRow(row, True)
            return
        TL = gridX.GetSelectionBlockTopLeft()
        RB = gridX.GetSelectionBlockBottomRight()
        Rows = gridX.GetSelectedRows()
        if not hasattr(self, "popup2Copy"):
            self.popup2Copy = wx.NewId()
            self.popup2Find = wx.NewId()
            self.popup2SelectAll = wx.NewId()
            self.popup2CopyLineSQL = wx.NewId()
            self.popup2CopyCondSelectSQL = wx.NewId()
            self.popup2ExportSQL = wx.NewId()
            self.popup2ExportDEL = wx.NewId()
            self.popup2ExportIXF = wx.NewId()
            self.Bind(wx.EVT_MENU, self.popup2_Copy, id=self.popup2Copy)
            self.Bind(wx.EVT_MENU, self.popup2_Find, id=self.popup2Find)
            self.Bind(wx.EVT_MENU, self.popup2_SelectAll, id=self.popup2SelectAll)
            self.Bind(wx.EVT_MENU, self.popup2_CopyLineSQL, id=self.popup2CopyLineSQL)
            self.Bind(wx.EVT_MENU, self.popup2_CopyCondSelectSQL, id=self.popup2CopyCondSelectSQL)
            self.Bind(wx.EVT_MENU, self.popup2_ExportSQL, id=self.popup2ExportSQL)
            self.Bind(wx.EVT_MENU, self.popup2_ExportDEL, id=self.popup2ExportDEL)
            self.Bind(wx.EVT_MENU, self.popup2_ExportIXF, id=self.popup2ExportIXF)
        menu = wx.Menu()
        tbns = self.nbResult.GetPageText(self.nbResult.GetSelection())
        item2Copy = wx.MenuItem(menu, self.popup2Copy, _("&Copy Selected \tCtrl-C"))
        item2Find = wx.MenuItem(menu, self.popup2Find, _("&Find Value"))
        item2SelectAll = wx.MenuItem(menu, self.popup2SelectAll, _("Select &All"))
        item2CopyLineSQL = wx.MenuItem(menu, self.popup2CopyLineSQL, _("Copy Selected Line(s) Data to &SQL"))
        item2CopyCondSelectSQL = wx.MenuItem(menu, self.popup2CopyCondSelectSQL, _("Create Selec&t SQL condition "))
        item2ExportSQL = wx.MenuItem(menu, self.popup2ExportSQL, _('&Export SQL \t"%s"') % tbns)
        item2ExportDEL = wx.MenuItem(menu, self.popup2ExportDEL, _('&Export DEL \t"%s"') % tbns)
        item2ExportIXF = wx.MenuItem(menu, self.popup2ExportIXF, _('&Export IXF \t"%s"') % tbns)
        menu.AppendItem(item2Copy)
        menu.AppendItem(item2Find)
        menu.AppendItem(item2SelectAll)
        menu.AppendItem(item2CopyLineSQL)
        menu.AppendItem(item2CopyCondSelectSQL)
        menu.AppendItem(item2ExportSQL)
        menu.AppendItem(item2ExportDEL)
        menu.AppendItem(item2ExportIXF)
        if len(Rows) <= 0:
            item2CopyLineSQL.Enable(False)
        if (len(TL) <= 0 or len(RB) <=0) and len(Rows) <=0:
            gridX.SelectRow(row)
        self.PopupMenu(menu)
        menu.Destroy()
#        print 'cell pos: %d %d' % (event.GetRow(), event.GetCol())
#        print ' selected status:  Cells, Rows, Cols, LeftTop , BottomRight'
#        nbX = self.FindWindowById(event.GetId())
#        gridX = nbX.GetPage(nbX.GetSelection())
#        print gridX.dbname, gridX.dbuser, gridX.tabname, gridX.sql, gridX.resmsg
#        print gridX.GetSelectedCells()
#        print gridX.GetSelectedRows()
#        print gridX.GetSelectedCols()
#        print gridX.GetSelectionBlockTopLeft()
#        print gridX.GetSelectionBlockBottomRight()
        # TODO

    # -------- notebook context menu --------
    def popup_ShowSQL(self, args=None):
        i = self.nbResult.GetSelection()
        if i >= 2:
            sqlori = self.nbResult.GetPage(i).sql
            az = sqld.QueryTokenizer()
            sqlnoc = az.removeAllCommentsFromQuery(sqlori)
            wx.MessageBox(u'%s\n---\n%s'%(sqlori.decode(self.str_encode), 
                sqlnoc.decode(self.str_encode)), u'SQL', wx.OK, self.last_dlg)
        pass

    def popup_ClosePage(self, args=None):
        i = self.nbResult.GetSelection()
        if i >= 2:
            self.nbResult.DeletePage(i)

    def popup_CloseAllPage(self, args=None):
        if wx.YES != wx.MessageBox(_('Close All Data Page?'), _('Ask'),
                        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self.last_dlg):
            return
        self.nbResult.SetSelection(0)
        a = self.nbResult.GetPageCount()
        for __j in range(2, a):
            self.nbResult.DeletePage(2)


    def popup_CloseOtherPage(self, args=None):
        if wx.YES != wx.MessageBox(_('Close Other no selected Data Page?'), _('Ask'),
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self.last_dlg):
            return
        i = self.nbResult.GetSelection()
        a = self.nbResult.GetPageCount()
        if i == 0 or i == 1:
            for __j in range(2, a):
                self.nbResult.DeletePage(2)
        elif i == 2:
            for __j in range(i+1,a):
                self.nbResult.DeletePage(i+1)
        elif i > 2:
            for __j in range(i+1,a):
                self.nbResult.DeletePage(i+1)
            for __j in range(2,i):
                self.nbResult.DeletePage(2)# 2

    def popup_SwitchPage(self, args=None):
        # Switch Log and DataGrid
        if self.nbResult.GetSelection() != 0:
            oldpos = self.nbResult.GetSelection()
            self.nbResult.oldpos = oldpos
            pos = 0
        else:
            if self.nbResult.oldpos > 0 and self.nbResult.oldpos < self.nbResult.GetPageCount():
                pos = self.nbResult.oldpos
            else:
                pos = self.nbResult.GetPageCount() - 1
        self.nbResult.SetSelection(pos)
        self.set_statusbar_text(pos)
        pass

    def popup_RefreshData(self, args=None):
        self.statusBar_exec.SetStatusText(_('Please waiting refresh ...'))
        gridX = self.nbResult.GetPage(self.nbResult.GetSelection())
        try:
            cont = False
            cs = None
            cs1 = None
            for i in self.dbs_connected:        # 1.origin connect
                if i[self.iDB] == gridX.db2db.db:
                    cs = i[self.iCS]
                    break
            else:
                for i in self.dbs_connected:    # 2.not origin connect , new connect dbname,dbuser same as origin
                    if i[self.iDBNAME] == gridX.db2db.dbname and i[self.iDBUSER] == gridX.db2db.dbuser:
                        cs = i[self.iCS]
                        break
                else:
                    for i in self.dbs_connected:# 3.only same connected dbname
                        if i[self.iDBNAME] == gridX.db2db.dbname:
                            cs1 = i[self.iCS]
                            break
            if not cs:  #not use "is None"  , PyDB2 problem
                if cs1:
                    if wx.YES != wx.MessageBox(_('execute sql on other user connect ?'), \
                                    _('Info'), wx.YES_NO | wx.ICON_QUESTION, self.last_dlg):
                        return
                    cs = cs1
                else:
                    wx.MessageBox(_(' Database Disconnected ? '), _('Error'), wx.OK | wx.ICON_ERROR, self.last_dlg)
                    return

            self.log_usersql('-- * [%s/%s] [%s] *\n%s ;\n' % (gridX.dbname, gridX.dbuser, 
                            time.strftime(self.str_time_strf), gridX.sql), False, True)
            t1 = time.time()
            self.execSQL(cs, gridX.sql, self.getts()[0], 1)
            exec_time = str(time.time() - t1)
            exec_time = exec_time[:exec_time.find('.')+3]
            t1 = time.time()
            data, rese = self.fetchData(cs, gridX.sql)
            if rese and len(data) == 0:
                cont = False
                raise rese
            description2 = cs._description2()
            fetchdata_time = str(time.time() - t1)
            fetchdata_time = fetchdata_time[:fetchdata_time.find('.')+3]
            rows, cols = len(data), len(gridX.description2)
            gridX.resmsg = '%d rows (%d cols) selected in %s sec.  Ftt: %s' % (rows, cols, exec_time, fetchdata_time)
            gridX.desc = [i[0] for i in description2]
            if rese and len(data)>0:
                cont = True
                raise rese
        except DB2.Error as ee:
            m = '  # DB2: %s %s %s\n' % (ee.args[0], ee.args[1], ee.args[2])
            self.statusBar_exec.SetStatusText(m.encode(self.str_encode))
            self.log_usersql2('--%s' % m)
            self.log_usersql(m, True)
            if not cont: 
                print '??'
                return
        except Exception as ee:
            m = '  # Except: %s\n' % str(ee)
            self.statusBar_exec.SetStatusText(m.encode(self.str_encode))
            self.log_usersql2('--%s' % m)
            self.log_usersql(m, True)
            if not cont:
                print '??'
                return

        for i in gridX.GetTable().data_change_pos:
            gridX.SetCellBackgroundColour(i[0], i[1], gridX.bgc)

        ## TODO, no refresh row ,col .  unknow .
#        tb = gridX.GetTable()   # TODO, BUG, no change grid size
#        tb.data = data
#        tb.desc = [i[0] for i in description2]
#        tb.row = len(data)
#        tb.col = len(tb.desc)
#        gridX.Fit()
#        gridX.ForceRefresh()

        try:
            self.new_page__show_data(data, description2, gridX.db2db, '', '', '', '', gridX)
        except Exception as ee:
            print ee

        gridX.Refresh()
        self.statusBar_exec.SetStatusText(u'Refreshed. %s ' % gridX.resmsg.decode(self.str_encode))
        pass

    def OnNbResultLeftDclick(self, event):
        event.Skip()
        self.popup_SwitchPage(None)

    def OnNbResultRightDown(self, event):
        event.Skip()
        curpos = self.nbResult.HitTest(event.GetPosition())[0]
        self.nbResult.SetSelection(curpos)
        if not hasattr(self, "popupClose"):
            self.popupShowSQL = wx.NewId()
            self.popupClose = wx.NewId()
            self.popupCloseOther = wx.NewId()
            self.popupCloseAll = wx.NewId()
            self.popupSwitchPage = wx.NewId()
            self.popupRefreshData = wx.NewId()
            self.Bind(wx.EVT_MENU, self.popup_ShowSQL, id=self.popupShowSQL)
            self.Bind(wx.EVT_MENU, self.popup_ClosePage, id=self.popupClose)
            self.Bind(wx.EVT_MENU, self.popup_CloseOtherPage, id=self.popupCloseOther)
            self.Bind(wx.EVT_MENU, self.popup_CloseAllPage, id=self.popupCloseAll)
            self.Bind(wx.EVT_MENU, self.popup_SwitchPage, id=self.popupSwitchPage)
            self.Bind(wx.EVT_MENU, self.popup_RefreshData, id=self.popupRefreshData)
        menu = wx.Menu()
        itemShowSQL = wx.MenuItem(menu, self.popupShowSQL, _("&Show SQL"))
        itemClose = wx.MenuItem(menu, self.popupClose, _('&Close Current Page'))
        itemCloseOther = wx.MenuItem(menu, self.popupCloseOther, _('Clos&e Other Pages'))
        itemCloseAll = wx.MenuItem(menu, self.popupCloseAll, _('Close &All Pages'))
        itemSwitchPage = wx.MenuItem(menu, self.popupSwitchPage, _('S&witch Log Page'))
        itemRefreshData = wx.MenuItem(menu, self.popupRefreshData, _("&Refresh Data"))
        menu.AppendItem(itemShowSQL)
        menu.AppendItem(itemClose)
        menu.AppendItem(itemCloseOther)
        menu.AppendItem(itemCloseAll)
        menu.AppendItem(itemSwitchPage)
        menu.AppendItem(itemRefreshData)
        if curpos < 2:
            itemShowSQL.Enable(False)
            itemClose.Enable(False)
            itemRefreshData.Enable(False)
        if self.nbResult.GetPageCount() <= 2:
            itemCloseOther.Enable(False)
            itemCloseAll.Enable(False)
        self.PopupMenu(menu)
        menu.Destroy()
        pass

    def OnNbResultNotebookPageChanged(self, event):
        newpos = event.GetSelection()
        if newpos >= 2:
            self.nbResult.oldpos = newpos
        elif newpos == 0:
            #self.stcExecLog.ShowPosition(self.stcExecLog.GetLastPosition())
            pass
        self.set_statusbar_text(newpos)
        #self.time_seteditfocus.Start(100, True)
        event.Skip()

    # -------- 
    def set_statusbar_text(self, currpos):
        # first run in  wx.EVT_NOTEBOOK_PAGE_CHANGED, id=wxID_DBMNBRESULT
        #self.nbResult.SetToolTipString('')
        try:
            if self.statusBar_exec.GetFieldsCount() >= 3:
                self.statusBar_exec.SetStatusText(u'', 1)
                self.statusBar_exec.SetStatusText(u'', 2)
    
            if currpos >= 2:
                gridX = self.nbResult.GetPage(currpos)
                self.statusBar_exec.SetStatusText(gridX.resmsg)
                msgs = '%s: %s.%s' % (gridX.dbname, gridX.tabschema, gridX.tabname)
                self.statusBar_exec.SetStatusText(msgs.decode(self.str_encode), 2) #ok
                #if len(gridX.sql) > 80:
                #    s = '%s ... %s' % (gridX.sql[:30], gridX.sql[-30:])    #unicode
                #else:
                #    s = gridX.sql
                #self.nbResult.SetToolTipString('DB:%s  SQL: %s' % (gridX.dbname, s))
            elif currpos == 0:
                self.statusBar_exec.SetStatusText(_(' Execute Log'))
            elif currpos == 1:
                self.statusBar_exec.SetStatusText(_(' Text format result'))
        except Exception as ee:
            print ee


    def new_page__show_data(self, data, description2, db2db=None, tabschema='', tabname='', sql='', resmsg='', gridx=None):
        ''' new page, grid and show data
        @param data:
        @param description2:
        @param db2db: Db2db or None
        @param tabschema: if '' not change origin value
        @param tabname: if '' not change origin value
        @param sql: if '' not change origin value
        @param resmsg: if '' not change origin value
        @param gridx: if None new page and grid, else show data on origin, use SetTable()
        '''
        ''' create a notebook page, add grid, show data . '''
        if gridx is None:
            gridid = wx.NewId()
            gridname = 'grid%d' % gridid
            gridX = wx.grid.Grid(id=gridid, name=gridname, parent=self.nbResult,
                  pos=wx.Point(0, 0), size=wx.Size(968, 309), style=0)
            gridX.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_select_cell__show_pos)        #msg
            gridX.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_grid_range_selection__show_range) #msg
            gridX.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_grid_label_left_click__sort)  #sort
            gridX.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_grid_label_right_click__autosizecol)
            gridX.Bind(wx.grid.EVT_GRID_COL_SIZE, self.on_grid_col_size__save_size)             #save table col's size
            gridX.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_grid_cell_right_click__show_menu) # popup menu
            gridX.SetDefaultCellFont(self.textConnMsg.GetFont())
            gridX.DisableDragRowSize()
            gridX.SetColLabelSize(24)
            gridX.SetRowLabelSize(50)
            gridX.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)

            if db2db:
                gridX.bgc = db2db.color
                gridX.SetDefaultCellBackgroundColour(gridX.bgc)

            pn = '%s.%s' % (tabschema, tabname)
            self.nbResult.AddPage(gridX, pn.decode(self.str_encode), False)
            #testdb = [ ['abcdefghij', '1234567890'] * 200, [234, 32342423424234234] * 200 ] * 2600000  # 5000000
            self.bind_all_ctrl_set_focus(gridX)
        else:
            gridX = gridx

        #print ' set data table ID: %s' % id(data) #check []
        griddata = dbGridTable(data, description2, self.str_encode)
        gridX.SetTable(griddata, True) # auto delete tablebase
        gridX.description2 = description2
        if db2db:
            gridX.db2db, gridX.dbname, gridX.dbuser = db2db, db2db.dbname, db2db.dbuser
        if tabschema:   gridX.tabschema = tabschema
        if tabname:     gridX.tabname = tabname
        if sql:         gridX.sql = sql
        if resmsg:
            gridX.resmsg = resmsg
        else:
            rows, cols = len(data), len(description2)
            gridX.resmsg = '%d rows (%d cols) selected in %s sec.' % (rows, cols, 0.0)
        if not hasattr(gridX,'dbname'): gridX.dbname = ''
        if not hasattr(gridX,'dbuser'): gridX.dbuser = ''
        if not hasattr(gridX,'tabschema'): gridX.tabschema = ''
        if not hasattr(gridX,'tabname'): gridX.tabname = ''
        if not hasattr(gridX,'sql'): gridX.sql = ''
        if not hasattr(gridX,'resmsg'): gridX.resmsg = ''

        gridX.issort = False
        gridX.sortcol = 0
        
        for i in range(len(description2)):
            gridX.SetColMinimalWidth(i, 1)

        try:    #set column size
            cl, sz = self.cfg.colsize_select(gridX.tabname)
            if cl:
                for ii in range(len(description2)):
                    try:
                        ix = cl.index(description2[ii][0])
                        gridX.SetColSize(ii, sz[ix])
                    except Exception as _ee:
                        pass
            elif len(data) < 100:   # grid.AutoSizeColumns may use long time.
                gridX.AutoSizeColumns()
        except Exception as _ee:
            pass

        if gridx is None:
            # don't in AppPage method set select=True.
            #  1.new gridX not has custom status message 2.table show problem: not have rows number
            self.nbResult.SetSelection(self.nbResult.GetPageCount() - 1)
        gridX.ForceRefresh()
        pass

    def remove_page_grid(self, gridXX=None):
        '''Remove a notebook page
        @param gridXX:  None , remove early page.   else remove gridXX
        '''
        if self.nbResult.GetPageCount() > 2:
            self.nbResult.DeletePage(2)


    def getQuoteInnerValue(self, str, quote_s='"'):
        lx=len(quote_s)
        mi=str[lx:]
        Rq=mi.find(quote_s)
        L=mi[:Rq].rstrip()
        R=mi[Rq+lx:].lstrip()
        return (L,R)

    def analyse_select_SQL_TableName(self, sql, dbuser):
        ''' from select * from ??  SQL get  tabschema and tabname
        Ugly code .
        @param sql:
        @param dbuser:
        '''
        assert type(sql) == type('')
        az = sqld.QueryTokenizer()
        sql = az.removeAllCommentsFromQuery(sql)
        sql = az.removeAllQuoteString(sql, True)
        tabschema = ''
        tabname = ''
        # bug bug bug ,unknow how to get tabname,
        # select * from  " user "." TABname "  ; select * from (select ? from xx) ; select ? from a A, b B where ...
        mi = re.sub('\s+[fF][rR][oO][mM]\s+', ' FROM ', sql.lstrip())
        mi = mi[mi.find(' FROM ')+6:]
        if mi[0]=='(':  #
            tabschema='_UN'
            tabname='KNOW_'
        elif mi[0]=='"':
            L,R=self.getQuoteInnerValue(mi,'"')
            if len(R)>0:
                if R[0]=='.':
                    R=R[1:].lstrip()
                    if R[0]=='"':
                        L1,R1=self.getQuoteInnerValue(R,'"')
                        if L1==L1.upper() and L1==L1.lstrip():
                            tabname=L1  # ok "??" . "UPPER"
                        else:
                            tabname='"%s"' % L1 # ok "??"."lower"
                    else:
                        for i in range(len(R)):
                            if R[i] not in '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                                break   # ok "??".abcd where ..
                        else:
                            i+=1    # ok "??".abcd$
                        tabname=R[:i].upper()   # ok "??".UPPERorlower
                    if L==L.upper() and L==L.lstrip():
                        tabschema=L # ok "UPPER ".??
                    else:
                        tabschema='"%s"' % L    # ok " lower".??
                else:
                    if L==L.upper() and L==L.lstrip():
                        tabname=L   # ok "TABNAME " where ..
                    else:
                        tabname='"%s"' % L # ok " lower" where ..
                    tabschema=dbuser.upper()
            else:
                if L==L.upper() and L==L.lstrip():
                    tabname=L   # ok "TABNAME " $
                else:
                    tabname='"%s"' % L  # ok " lower" $
                tabschema=dbuser.upper()
        else:   # from NAME ..., not begin by quote
            for i in range(len(mi)):
                if mi[i] not in '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                    break   # ok abc.??
            else:
                i+=1
            L=mi[:i]
            if i!=len(mi):
                R=mi[i:].lstrip()
                if R[0]=='.':
                    R=R[1:].lstrip()
                    if R[0]=='"':
                        L1,R1=self.getQuoteInnerValue(R, '"')
                        if L1==L1.upper() and L1==L1.lstrip():
                            tabname=L1  #ok abc."DEF"
                        else:
                            tabname='"%s"' % L1 #ok abc." lower"
                    else:
                        for i in range(len(R)):
                            if R[i] not in '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                                break # ok ??.?? where ...
                        else:
                            i+=1    # ok ??.?? $
                        tabname=R[:i].upper()
                    tabschema=L.upper()
                else:
                    tabname=L.upper()   # ok abcd where ...
                    tabschema=dbuser.upper()
            else:
                tabname=L.upper()   # ok abcd
                tabschema=dbuser.upper()

        if tabschema[0] != '"' and tabschema.find(' ') != -1:
            tabschema = '"%s"' % tabschema
        if tabname[0] != '"' and tabname.find(' ') != -1:
            tabname = '"%s"' % tabname
        return tabschema.rstrip(), tabname.rstrip()

    def execute_sql_thread(self, *args):
        ''' create a thread to execute sql
        @note:  cannot call direct, used threading.Thread target
        @param *args: (cs, sql, returnExcept[])
        '''
        cs, sql, returnExcept = args
        try:
            cs.execute(sql)
        except Exception as ee:
            returnExcept.append(ee)
            return
        return

    def execSQL(self, cs, sql, time_out=1, show_dlg_time=3):
        ''' execute sql statement
        @param cs:
        @param sql:
        @param time_out:
        @param show_dlg_time:
        '''
        try:
            if type(sql) == type(u''):
                sql = sql.encode(self.str_encode)
        except UnicodeError as ee:
            print ' Ex:', ee
            try:
                sql = unicode(sql, 'utf-8').encode(self.str_encode)
            except Exception as ee:
                raise ee

        dlg = None
        try:
            cs.set_timeout(time_out)  # python cannot break a thread
            res = []
            th = threading.Thread(target=self.execute_sql_thread, args=(cs,sql,res))
            th.start()
            ti = 0.0
            iprog = 10
            isBrk = False
            while True:
                th.join(0.3)
                if th.isAlive():
                    ti += 0.3
                    if not dlg and ti >= show_dlg_time:  # more than ? seconds show ProgressDialog
                        try:
                            sqll = sql.lstrip()[:70].encode(self.str_encode)
                        except Exception as ee:
                            sqll = _(' ?? unknow split sql ')
                        dlg = wx.ProgressDialog(_('Please waiting ...'), u'EXECUTE: %s\n  %s' % \
                            (u'  '*30, sqll), 100, self.last_dlg, style=wx.PD_ELAPSED_TIME)
                            # | wx.PD_CAN_ABORT)
                    iprog = (iprog + 10) % 100
                    if dlg and not dlg.Update(iprog)[0]:
                        if not isBrk:
                            #th
                            isBrk = True
                            print 'cancel1  , cannot brak thread'
                            #break
                else:
                    if len(res) != 0:
                        raise res[0]
                    break
        except Exception as ee:
            raise ee
        finally:
            if ti >= 3: print ' execute finally. used %s sec.' % ti
            #else: print ' exec finally time %s '  % ti
            if dlg: dlg.Destroy()

    def fetch_data_thread(self, *args):
        ''' fetch data from cs
        @param *args: 
        @note:  cursor
        @note:  isBreakOrPause [ T/F, T/F ]
        @note:  iCount[i_fetched, i_plus, i_Warnning]
        @note:  data []
        @note:  returnExcept[]
        '''
        cs, isBrkOrPause, iCount, data, returnExcept = args
        try:
            while not isBrkOrPause[0]:
                da = cs.fetchmany(iCount[1])
                iCount[0] += iCount[1]
                data += da
                while isBrkOrPause[1]:
                    time.sleep(0.01)
        except TypeError as ee:
            return
        except Exception as ee:
            returnExcept.append(ee)
            return

    def fetchData(self, cs, sql=''):
        '''  WARRING !!!
        @param cs:
        @param sql:
        @return: (cs.fetch(), None | Exception )
        '''
        msg = _('execute sql success, fetch data ( %d rows ), Please waiting ...   ')
        try:
            sql2 = sql[:70].decode(self.str_encode)
        except:
            sql2 = u'??'
        dlg = None
        try:
            dlg = wx.ProgressDialog(sql2, msg % 0, 100, self.last_dlg, style=wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT)
        except Exception as ee:
            print ee
        iprog = 10
        if dlg: dlg.Update(iprog)
        isBrkOrPasue = [False, False]
        iCount = [0, 2000, 100000]
        das = []
        res = []
        rese = None
        ti = 0
        th =  threading.Thread(target=self.fetch_data_thread, args=(cs, isBrkOrPasue, iCount, das, res))
        th.start()
        try:
            while True:
                th.join(0.4)
                ti += 0.4
                if th.isAlive():
                    iprog = (iprog + 5) % 100
                    if dlg and not dlg.Update(iprog, msg % iCount[0])[0]:
                        if not isBrkOrPasue[0]:
                            self.log_usersql('-- fetch %d rows, cancel\n' % iCount[0])
                            isBrkOrPasue[0] = True
                    if not isBrkOrPasue[0] and iCount[0] >= iCount[2]:
                        isBrkOrPasue[1] = True
                        if wx.YES != wx.MessageBox(_('fetch %d rows, may be have more rows,  continue?') % iCount[0], \
                                                   _('Ask'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self.last_dlg):
                            self.log_usersql('-- fetch %d rows; no continue.\n' % iCount[0])
                            isBrkOrPasue[0] = True
                        else:
                            iCount[2] += 100000
                        isBrkOrPasue[1] = False
                else:
                    if len(res) != 0:
                        rese = res[0]
                    break
        finally:
            if ti > 4: print ' fetch %d rows, used %s sec.' % (len(das), ti)
            if dlg: dlg.Destroy()
        return das, rese

    def showData(self, db2db, sql, execsql_time=0.0):
        '''show data
        @param db2db: Db2db()
        @param sql: sql
        @param execsql_time: execute select time   t2-t1
        @return: resmsg_0:  message select result and time
        '''
        ##sql = sql.decode(self.str_encode)
        exec_time = str(execsql_time)
        exec_time = exec_time[:exec_time.find('.')+3]
        self.statusBar_exec.SetStatusText(u'Selected in %s . Please waiting...' % exec_time)
        t1 = time.time()
        data, rese = self.fetchData(db2db.cs, sql)
        if rese and len(data) == 0: raise rese
        desc = db2db.cs._description2()

        #in DB2 v8.2 a connect change date but uncommit,other connect selected date look like is commited.
        #in DB2 v9.5 , except SQL0952N
        # if len(data) == 0
        rows, cols = len(data), len(desc)
        resmsg_0 = '%d rows (%d cols) selected in %s sec.' % (rows, cols, exec_time)
        self.statusBar_exec.SetStatusText(u'%s  Please waiting...' % resmsg_0.decode(self.str_encode))
        tabschema, tabname = '', ''

        try:
            tabschema,tabname=self.analyse_select_SQL_TableName(sql, db2db.dbuser)
        except Exception as ee:
            self.log_pg('-- Exception in analyse_select_SQL_TableName ?? %s\n'  % str(ee))
        t3 = time.time()
        fetchdata_time = str(time.time() - t1)
        fetchdata_time = fetchdata_time[:fetchdata_time.find('.')+3]
        resmsg_s = '%s  Ftt: %s' % (resmsg_0, fetchdata_time)
        try:
            self.new_page__show_data(data, desc, db2db, tabschema, tabname, sql, resmsg_s)
        except Exception as ee:
            self.log_pg('-- Exception in new_page__show_data: %s\n' % str(ee))
        showdataongrid_time = str(time.time() - t3)
        showdataongrid_time = showdataongrid_time[:showdataongrid_time.find('.')+3]
        msg = '%s  Ftt: %s Stt: %s' % (resmsg_0, fetchdata_time, showdataongrid_time)
        self.statusBar_exec.SetStatusText(msg.decode(self.str_encode))
        return resmsg_0, rese

    # -------- control event --------
    def OnChoiceConnectedDbnamesChoice(self, event):
        msg = self.choiceConnectedDbnames.GetStringSelection()
        self.SetTitle(msg)
        self.stcSQLs.SetFocus()
        event.Skip()


    def OnSplitterWindowExecLeftDclick(self, event):
        #event.Skip()    # not Skip()
        if self.splitterWindowExec1_up == 0:
            self.splitterWindowExec.SetSashPosition(1)
        elif self.splitterWindowExec1_up == 1:
            self.splitterWindowExec.SetSashPosition(-1)
        else:
            sz = self.splitterWindowExec.GetSize()
            self.splitterWindowExec.SetSashPosition(sz.y/2)
        self.splitterWindowExec1_up = (self.splitterWindowExec1_up + 1) % 3
#        if self.splitterWindowExec.GetSashPosition() > 100:
#            self.splitterWindowExec.SetSashPosition(1)

    def getsplitchar(self):
        spc = self.txtSplitChar.GetValue()
        if spc: return spc
        else:   return ';'

    def getts(self):
        try:
            time_out = self.txtTimeout.GetValue().split(',')
            if len(time_out)==1:
                return int(time_out[0]),1
            elif len(time_out)>=1:
                return int(time_out[0]),int(time_out[1])
        except Exception as _ee:
            return 10,1

    def OnBtnExecSqlsButton(self, event):
        if event: event.Skip()
        self.execSQLs()


    def OnBtnExecSqlSingleButton(self, event):
        if event: event.Skip()
        self.execSQLs(True)


    def removeSQLComment(self, sql):
        sql = sql.strip()
        if sql[:2] == '--':
            rl = sql.find('\n')
            if rl == -1:
                return ''
            else:
                sql = sql[rl + 1:]
                return self.removeSQLComment(sql)
        else:
            return sql


    def execute_sqls_thread(self, *args):
        '''
        @param *args: (cs, sqls, lock, iRes, Res_or_Except, ds)
        @param cs: 
        @param sqls: string list
        @param lock: threading.Lock()
        @param iRes: [ [iSqls, iSucc, iFail, iCurrent in sqls position],  False,  ]
        @param isCancel: a list have a elementitem, [ True | False ]
        @param Res_or_Escept: select res [ (True,sql,time) ],     Except: [ (False, sql, Exception as ee ) ]
        @param ds: StringIO.String()
        '''
        cs, sqls, lock, iRes, isCancel, Res_or_Except, ds = args #ds.write
        iRes[0][0] = len(sqls)
        tts1, tts2 = self.getts()
        if iRes[0][0] <= 1: cs.set_timeout(tts1)
        else:               cs.set_timeout(tts2)
        az = sqld.QueryTokenizer()
        for ss in sqls:
            if isCancel[0]:
                print ' canceled thread... '
                lock.acquire();ds.write('-- execute progress cancel\n\n');lock.release()
                break
            lock.acquire()
            iRes[0][3] += 1
            lock.release()
            sql = ss[0]

            sql2 = az.removeAllCommentsFromQuery(sql)#self.removeSQLComment(sql)
            if sql2 == '':
                iRes[0][0] -= 1
                continue
            try:
                lock.acquire();ds.write('%s ;\n' % sql);lock.release()
                t1 = time.time()
                self.sqq.write(sql)
                self.sqq.write(self.NL)
                self.sqq.write(self.NL)
                cs.execute(sql)
                t2 = time.time()
                iRes[0][1] += 1
                if cs.description is not None and len(cs.description) > 0: # select statement
                    if sql[:6].upper() != 'SELECT':
                        print ' = Error - Error - Error = '
                        print sql
                    m = ''
                    lock.acquire();Res_or_Except.append((True, sql, t2-t1));lock.release()
                    while True:
                        lock.acquire();il = len(Res_or_Except);lock.release()
                        if il == 0 or isCancel[0]: break
                        else:   time.sleep(0.02)
                else:   # other sql statement
                    exec_time = str(t2 - t1)
                    exec_time = exec_time[:exec_time.find('.') + 3]
                    if cs.rowcount == -1:
                        self.set_commit_btn_status(True)
                        m = 'Processed in %s sec. ' % exec_time
                    elif cs.rowcount == 0:
                        m = '0 row applied in %s sec.' % exec_time
                    else:
                        self.set_commit_btn_status(True)
                        m = '%d rows applied in %s sec.' % (cs.rowcount, exec_time)
                # all
                if m != '':
                    lock.acquire();ds.write('-- %s\n\n' % m);lock.release()
            except Exception as ee:
                iRes[0][2] += 1
                lock.acquire();Res_or_Except.append((False, sql, ee));lock.release()
                while True:
                    lock.acquire();il = len(Res_or_Except);lock.release()
                    if il == 0 or isCancel[0]: break
                    else:   time.sleep(0.02)
        pass

    def execSQLs(self, isSingle=False, sqlstr=''):
        ''' execute SQLs
        @param isSingle: run selected as a single sql statments
        @param sqlstr: a list, element is sql statements
        '''
        assert type(sqlstr) in [type(''), type(u'')]

        dbX = self.get_db2db_from_connect_string(self.choiceConnectedDbnames.GetStringSelection(), True)
        if not dbX.cs:
            wx.MessageBox(_('No has database connect  !'), _('Error'), wx.OK | wx.ICON_ERROR, self.last_dlg)
            return

        self.islogsql = self.chkLogSqls.GetValue()
        self.isshowsql = self.chkShowSqlsRes.GetValue()
        isShowCurrentSql = True
        sqls, beee, eeed, spt = self.get_sqls_from_stcSQLs(isSingle, sqlstr)
        if spt > 2: print ' split sqls use', spt
        if not sqls: return

        m = '\n--** BEGIN %s\n-- * [%s/%s] [%s] *\n' % \
                ('**'*34, dbX.dbname, dbX.dbuser, time.strftime(self.str_time_strf))
        self.log_usersql2(m)
        self.log_usersql(m)

        iSqls, iSucc, iFail, iii = 0, 0, 0, -1
        iRes = [[iSqls, iSucc, iFail, iii], False, ]
        isCancel = [False]
        Res_or_Except = []
        ds = StringIO.StringIO()
        es = StringIO.StringIO()
        msg = ''
        msg2 = ''
        iProgmax = len(sqls)
        dlg = None
        dlg = wx.ProgressDialog(_('Please waiting ...'), u'execute %3d/%3d statement %s\n\n\n' % \
                (iSucc + iFail, iSqls, u'=='*20), iProgmax+2, self.last_dlg, style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
        dlg.Update(1)
        llast_dlg = self.last_dlg
        self.last_dlg = dlg
        pt = dlg.GetPosition()
        sz = dlg.GetSize()
        dlg.SetPosition(wx.Point(pt.x, pt.y - sz.y/2))
        lock = threading.Lock()
        th = threading.Thread(target=self.execute_sqls_thread, args= \
                (dbX.cs, sqls, lock, iRes, isCancel, Res_or_Except, ds))
        th.start()
        ti = 0.0
        splittime = 0.05
        try:
            while True:
                th.join(splittime)
                ti += splittime
                if th.isAlive():
                    lock.acquire()
                    iSqls, iSucc, iFail, iii = iRes[0]
                    if isShowCurrentSql and not isSingle:
                        __1, be, ed = sqls[iii]
                        self.stcSQLs.SetSelection(be, ed)
                    lock.release()
                    try:
                        sqlu = sqls[iii][0].lstrip()[:78].decode(self.str_encode)
                    except Exception as ee:
                        sqlu = _(' ?? unknow split sql ')
                    if isCancel[0]: # 2@#$&@)#&@)
                        splittime = 0.3
                        if dlg: dlg.Update(iSucc + iFail + 1, u'execute %3d ( %3d ) statement. Success %2d, Failed %2d\n\n Cancel, waiting ...' \
                            % (iSucc + iFail, iSqls, iSucc, iFail))
                        continue
                    msgs = 'execute %3d ( %3d ) statement. Success %2d, Failed %2d\n\n%s' \
                            % (iSucc + iFail, iSqls, iSucc, iFail, sqlu)
                    if dlg and not isCancel[0] and not dlg.Update(iSucc + iFail + 1, msgs)[0]:
                        isCancel[0] = True
                        print ' execute progress press cancel  '
                    else:
                        lock.acquire()
                        try:
                            for __i in range(len(Res_or_Except)):
                                re1 = Res_or_Except.pop(0)
                                m = ''
                                if re1[0]:  #'SELECT'
                                    try:
                                        remsg, rese = self.showData(dbX, re1[1], re1[2])
                                        m = ' %s\n\n' % remsg
                                        ds.write('--%s' % m)
                                        if rese: raise rese
                                    except DB2.Error as ee:
                                        iRes[0][1] -= 1; iRes[0][2] += 1
                                        m = '  # DB2: %s %s %s\n' % (ee.args[0], ee.args[1], ee.args[2])
                                        if m.find('SQL0952N') > 0:
                                            m = '  # DB2: Timeout or Break.  SQL0952N %s %s\n' % (ee.args[0], ee.args[1])
                                        ds.write('--%s' % m)
                                        es.write(m)
                                    except Exception as ee:
                                        iRes[0][1] -= 1; iRes[0][2] += 1
                                        m = '  # EXCEPT Ex: %s\n' % ee
                                        ds.write('--%s' % m)
                                        es.write(m)
                                else:   # Exception
                                    try:
                                        raise re1[2]
                                    except DB2.Error as ee:
                                        m = '  # DB2: %s %s %s\n' % (ee.args[0], ee.args[1], ee.args[2])
                                        ds.write('--%s' % m)
                                        es.write('%s ;\n%s' % (re1[1], m))
                                        if iRes[0][1] == 0 and iRes[0][2] >= 1:   # fail.
                                            ans = wx.MessageBox(m.decode(self.str_encode), _('Error, Continue ? '), wx.ICON_ERROR | wx.YES_NO | wx.NO_DEFAULT, self.last_dlg)
                                            if ans != wx.YES:
                                                isCancel[0] = True
                                                break
                                        elif m.find('SQL1024N') != -1:  # no db connect
                                            ans = wx.MessageBox(m.decode(self.str_encode), _('Error, Continue ? '), wx.ICON_ERROR | wx.YES_NO | wx.NO_DEFAULT, self.last_dlg)
                                            if ans != wx.YES:
                                                isCancel[0] = True
                                                break
                                    except Exception as ee:
                                        m = '  # EXCEPT: %s\n' % str(ee)
                                        ds.write('--%s' % m)
                                        es.write('%s ;\n%s' % (re1[1], m))
                                        ans = wx.MessageBox(m.decode(self.str_encode), _('Error, Continue ? '), wx.ICON_ERROR | wx.YES_NO | wx.NO_DEFAULT, self.last_dlg)
                                        if ans != wx.YES:
                                            isCancel[0] = True
                                            break
                            # end for Result_Select_Stmt_or_Except
                            if ds.len > 0:
                                msg = ds.getvalue()
                                ds.truncate(0)
                            if es.len > 0:
                                msg2 = es.getvalue()
                                es.truncate(0)
                        finally:
                            lock.release()
                        if msg != '':
                            if self.islogsql: self.log_usersql2(msg)
                            if self.isshowsql:self.log_usersql(msg)
                            msg = ''
                        if msg2 != '':
                            self.log_usersql(msg2, True, False)
                            msg2 = ''
                else:
                    break
        finally:
            try:
                iSqls, iSucc, iFail, iii = iRes[0]
                for __i in range(len(Res_or_Except)):
                    re1 = Res_or_Except.pop(0)
                    m = ''
                    if re1[0]:  #'SELECT'
                        try:
                            remsg, rese = self.showData(dbX, re1[1], re1[2])
                            m = '-- %s\n' % remsg
                            ds.write('--%s' % m)
                            if rese: raise rese
                        except DB2.Error as ee:
                            m = '  # DB2: %s %s %s\n' % (ee.args[0], ee.args[1], ee.args[2])
                            if m.find('SQL0952N') > 0:
                                m = '  # DB2: Timeout or Break.  SQL0952N %s %s\n' % (ee.args[0], ee.args[1])
                            ds.write('--%s' % m)
                            es.write(m)
                        except Exception as ee:
                            m = '  # EXCEPT Ex: %s\n' % ee
                            ds.write('--%s' % m)
                            es.write(m)
                    else:   # Exception
                        #wx.MessageBox(' Please Check Program ... 674353 .   not run here', 'ERROR', wx.OK, self.last_dlg)
                        try:
                            raise re1[2]
                        except DB2.Error as ee:
                            iRes[0][2] += 1
                            m = '  # DB2: %s %s %s\n' % (ee.args[0], ee.args[1], ee.args[2])
                            ds.write('--%s' % m)
                            es.write('%s ;\n%s' % (re1[1], m))
                        except Exception as ee:
                            iRes[0][2] += 1
                            m = '  # EXCEPT: %s\n' % ee
                            ds.write('--%s' % m)
                            es.write('%s ;\n%s' % (re1[1], m))
                msg = ds.getvalue()
                msg2 = es.getvalue()
                if msg != '':
                    if self.islogsql: self.log_usersql2(msg)
                    if self.isshowsql:self.log_usersql(msg)
                    msg = ''
                if msg2 != '':
                    self.log_usersql(msg2, True, False)
                    msg2 = ''

                m = '\n-- * [%s/%s] [%s]      Total: %d sql: Success:%d  Fail:%d\n--** END **%s\n' % \
                    (dbX.dbname, dbX.dbuser, time.strftime(self.str_time_strf), iSucc + iFail, iSucc, iFail, '--'*50)
                self.log_usersql2(m)
                self.log_usersql(m)

                if self.islogsql and iProgmax > 10:
                    self.logsqlf.flush()
                dbX.cs.close()
            except Exception as _ee:
                pass
            if not isSingle and not isCancel[0] and eeed:
                self.stcSQLs.SetSelection(beee, eeed)
            else:
                if isShowCurrentSql and not isSingle:
                    __1, be, ed = sqls[iRes[0][3]]
                    self.stcSQLs.SetSelection(be, ed)
            if dlg:
                self.last_dlg = llast_dlg
                if iFail == 0: dlg.Destroy()
                else:dlg.Update(iProgmax+2, u'Done. \n\n  execute %3d ( %3d ) statement.\n  Success %2d, Failed %2d  ' \
                                % (iSucc + iFail, iSqls, iSucc, iFail))
        pass

    def get_sqls_from_stcSQLs(self, isSingle=False, exsql=''):
        '''
        @param isSingle:
        @param exsql:
        @return: sqls[], beee, eeed, time
        '''
        sqls, beee, eeed = [], None, None
        t1 = time.time()
        if exsql.strip() == '':
            self.stcSQLs.SetFocus()
            exsql = self.stcSQLs.GetSelectedText()
        elif type(exsql) != type(u''):
            try:
                exsql = exsql.decode(self.str_encode)   # pg local --> unicode
            except UnicodeDecodeError as ee: # may be sql from execPython, string code is unicode,but type is str
                try:
                    exsql = exsql.decode('utf-8')
                except Exception as ee:
                    exsql = ''
                    print ' analyse SQLs Error:', ee
                    print '''-------------------- try used u'XXX' string --------------------'''
                    return sqls, beee, eeed, 0
        if exsql.strip() == '':
            print 'no select sql statement'
            return sqls, beee, eeed, 0
        if isSingle:
            sqls.append((exsql.encode(self.str_encode), self.stcSQLs.GetSelectionStart(), self.stcSQLs.GetSelectionEnd()))
        else:
            dlg = None
            try:
                beee = self.stcSQLs.GetSelectionStart()
                eeed = self.stcSQLs.GetSelectionEnd()
                if eeed - beee > 2*2**20:
                    dlg = wx.ProgressDialog(_('Please waiting ...'), _('in split query statement '), 100)
                    dlg.Update(50)
                b = self.stcSQLs.GetTextRange(0, beee)
                u8sp=len(b.encode(self.str_encode))-len(b)
                beforepos = u8sp*2 + len(b)
                assert beforepos == beee
                az = sqld.QueryTokenizer()
                sqls = az.tokenize(exsql, self.str_encode, self.getsplitchar(), beforepos)
                del az
                #if len(exsql)>10:ss=10
                #else:ss=len(exsql)
                #for i in range(ss):
                #    print 'self.stcSQLs.SetSelection(%d,%d)' % (exsql[i][1]+beee,exsql[i][2]+beee)
            finally:
                if dlg: dlg.Destroy()

        return sqls, beee, eeed, time.time() - t1

    def OnBtnCommitButton(self, event):
        self.stcSQLs.SetFocus()
        event.Skip()
        if wx.YES != wx.MessageBox(_(' Commit ?     '), _('Ask'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR, self.last_dlg):
            return
        dbX = self.get_db2db_from_connect_string()
        dbX.db.commit()
        self.set_commit_btn_status(False)
        self.log_usersql('COMMIT ;\n-- on %s at %s\n\n' % (dbX.dbname, time.strftime(self.str_time_strf)), False, True)


    def OnBtnRollbackButton(self, event):
        self.stcSQLs.SetFocus()
        event.Skip()
        if wx.YES != wx.MessageBox(_(' Rollback ?            A  applied be lost '), _('Ask'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR, self.last_dlg):
            return
        dbX = self.get_db2db_from_connect_string()
        dbX.db.rollback()
        self.set_commit_btn_status(False)
        self.log_usersql('ROLLBACK ;\n-- on %s at %s\n\n' % (dbX.dbname, time.strftime(self.str_time_strf)), False, True)
        event.Skip()

    def export_data_thread(self, *args):
        '''
        @param *args: ( data_type, data, gridX, ff, isBrk[], iC[] )
        '''
        data_type, data, gridX, ff, isBrk, iC = args
        # export
        desc = gridX.description2
        tabschema = gridX.tabschema
        tabname = gridX.tabname
        rows = len(data)
        cols = len(desc)
        if data_type == 1:
            ftype = 'SQL'
            inss = ''
            for col in range(cols):
                inss += """, %s""" % desc[col][0]
            inss = inss[2:]
            rl = '%s ' % self.NL if len(inss) > 80 else ''
            for row in range(rows):
                v = ''
                for col in range(cols):
                    if not data[row][col] is None:
                        if desc[col][1] in ['INTEGER', 'SMALLINT', 'BIGINT', 'INT']:
                            v += ', %d' % data[row][col]
                        elif desc[col][1] in ['DECIMAL', 'REAL', 'DOUBLE']: #bug2
                            v += ', %f' % data[row][col]        # %s > %f
                        else:
                            v += """, '%s'""" % str(data[row][col]).replace("'", "''") #bug3
                    else:
                        v += ', NULL'
                #v = str(data[i])  # encoding problem
                #v = v[2:].replace('None', 'NULL')
                inssql1 = 'insert into %s.%s ( %s )%s values ( %s ) ;%s' % (tabschema, tabname, inss, rl, v[2:], self.NL)
                ff.write(inssql1)
                iC[0] += 1
                if isBrk[0]: break
        elif data_type == 2:
            ftype = 'DEL'
            for row in range(rows):
                v = ''
                for col in range(cols):
                    if not data[row][col] is None:
                        if desc[col][1] in ['INTEGER', 'SMALLINT', 'BIGINT', 'INT']:
                            v += ',%d' % data[row][col]
                        elif desc[col][1] in ['DECIMAL', 'REAL', 'DOUBLE']:
                            v += ',%f' % data[row][col]
                        else:
                            v += ''',"%s"''' % str(data[row][col]).replace('"', '""')
                    else:
                        v += ','
                ff.write('%s%s' % (v[1:], self.NL))
                iC[0] += 1
                if isBrk[0]: break
        elif data_type == 3:
            ftype = 'IXF'
            print 'un implement'
        return ftype

    def export_data(self, data_type, gridX):
        '''export to data.
        @param data_type: 1: SQL     2: DEL    3: IXF
        @return : True or False
        '''
        try:
            data = gridX.GetTable().data
        except Exception as _ee:
            print ' un grid'
            return False
        #print ' get data table ID: %s' % id(data) #check []

        fext = u'Any files (*.*)|*.*'
        if data_type == 1:
            fext = u'%s|%s' % (u'Insert SQL file (*.sql)|*.sql', fext)
        elif data_type == 2:
            fext = u'%s|%s' % (u'DB2 DEL file (*.del)|*.del', fext)
        elif data_type == 3:
            fext = u'%s|%s' % (u'DB2 IXF file (*.ixf)|*.ixf', fext)
        else:
            print ' Error export type'
            return False

        if data_type == 1:  ftype = 'SQL'
        elif data_type == 2:ftype = 'DEL'
        elif data_type == 3:ftype = 'IXF'
        savefile = ''
        dfn = '%s.%s.%s_%s' % (gridX.dbname, gridX.tabschema, gridX.tabname, time.strftime(self.str_time_strf))
        dlg = wx.FileDialog(self, message=_("Save file as ..."),
                defaultFile=dfn.decode(self.str_encode),
                wildcard=fext , style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            savefile = dlg.GetPath()
        dlg.Destroy()
        if savefile == '':
            return False
        else:
            ff = open(savefile,'wb')

        t1 = time.time()
        iC = [0]
        isBrk = [False]
        msg = 'export  "%s"."%s"   of  "%s" ' % (gridX.tabschema, gridX.tabname, ftype)  + '  Write %4d' + ' of %d records.' % len(data)
        dlg = wx.ProgressDialog(_('Please waiting ...'), msg.decode(self.str_encode) % 0, len(data), self, style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
        th = threading.Thread(target=self.export_data_thread, args=(data_type, data, gridX, ff, isBrk, iC))
        th.start()
        while True:
            th.join(0.5)
            if th.isAlive():
                try:
                    msgs = msg % iC[0]
                    msgs = msgs.decode(self.str_encode)
                except Exception:
                    msgs = u'ex'
                if not isBrk[0] and not dlg.Update(iC[0], msgs)[0]:
                    isBrk[0] = True
            else:
                break
        dlg.Destroy()

        ff.close()
        st = os.stat(ff.name)
        s_time = str(time.time() - t1)
        msgs = 'export to "%s" of %s "%s"\n  Write %d bytes, Used %s sec.\n' % \
                    (ff.name.encode(self.str_encode), ftype, gridX.sql, st.st_size, s_time[:s_time.find('.')+3])
        self.log_pg(msgs)
        if st.st_size <= 10 * 2**20:
            try:
                dlg = wx.TextEntryDialog(self, u'', _('open file ?'), u'%s "%s"' % (self.editor, ff.name))
                if wx.ID_OK == dlg.ShowModal():
                    os.system(dlg.GetValue().encode(self.str_encode))
            except Exception as _ee:
                pass
            finally:
                dlg.Destroy()
        return True

    # ------------------------------------------------------------------------
    # ---------- objects page ----------
    # -------- schemas --------
    def set_obj_ctrl_s(self, isSingleLine):
        if isSingleLine:
            self.choiceSchema1.Disable()
            self.choiceSchema2.Disable()
            self.txtI1.Disable()
            self.txtI2.Disable()
            self.lstT1.Disable()
            self.lstT2.Disable()
#            self.stcM1.ClearAll()
#            self.stcM1.AppendText('\n'.join([str(f1[i]) for i in range(len(f1))]))
#            self.stcM2.ClearAll()
#            self.stcM2.AppendText('\n'.join([str(f2[i]) for i in range(len(f2))]))
        else:
            self.choiceSchema1.Enable()
            self.choiceSchema2.Enable()
            self.txtI1.Enable()
            self.txtI2.Enable()
            self.lstT1.Enable()
            self.lstT2.Enable()
#            self.choiceSchema1.Clear()
#            self.choiceSchema1.AppendItems([f1[i][0] for i in range(len(f1))])
#            self.choiceSchema2.Clear()
#            self.choiceSchema2.AppendItems([f2[i][0] for i in range(len(f2))])

    def query_schemas(self, cs, typestr):
        ''' user cursor query schema
        @param cs: cursor
        @param typestr: string TABLE  VIEW SERVER ...
        @return:  None   or    schema objects string list   or   (objects , ) tuple
        '''
        isR = False
        isSingleLine = True
        if typestr == 'TABLE':
            vt = '''select rtrim(TABSCHEMA) from SYSCAT.TABLES where TYPE='T' group by TABSCHEMA order by TABSCHEMA'''
        elif typestr == 'VIEW':
            vt = '''select rtrim(TABSCHEMA) from SYSCAT.TABLES where TYPE='V' group by TABSCHEMA order by TABSCHEMA'''
        elif typestr == 'SUMMARY TABLE':
            vt = '''select rtrim(TABSCHEMA) from SYSCAT.TABLES where TYPE='S' group by TABSCHEMA order by TABSCHEMA'''
        elif typestr == 'SERVER':
            vt = '''select * from SYSCAT.SERVERS order by SERVERNAME'''
            isSingleLine = False
        elif typestr == 'DRAP':
            vt = '''select * from SYSCAT.SERVERS order by SERVERNAME'''
            isR = True
        elif typestr == 'NICKNAME':
            vt = '''select TABSCHEMA from SYSCAT.NICKNAMES group by TABSCHEMA order by TABSCHEMA'''
        elif typestr == 'BUFFERPOOL':
            vt = '''select * from SYSCAT.BUFFERPOOLS order by BPNAME'''
            isSingleLine = False
        elif typestr == 'TABLESPACE':
            vt = '''select TBSPACEID,TBSPACE,DEFINER,TBSPACETYPE,DATATYPE,EXTENTSIZE,DBPGNAME,BUFFERPOOLID,DROP_RECOVERY,NGNAME from SYSCAT.TABLESPACES order by TBSPACE'''
            isSingleLine = False
        elif typestr == 'FUNCTION':
            vt = '''select rtrim(FUNCSCHEMA) from SYSCAT.FUNCTIONS group by FUNCSCHEMA order by FUNCSCHEMA'''
        elif typestr == 'TRIGGER':
            vt = '''select rtrim(TRIGSCHEMA) from SYSCAT.TRIGGERS  group by TRIGSCHEMA order by TRIGSCHEMA'''
        elif typestr == 'PROCEDURE':
            vt = '''select rtrim(PROCSCHEMA) from SYSCAT.PROCEDURES  group by PROCSCHEMA order by PROCSCHEMA'''
        else:
            vt = ''
            print '  unknow implement select '
            isR = True

        if not isR:
            try:
                f1 = []
                cs.execute(vt)
                f1 = cs.fetchall()
            except DB2.Error as ee:
                m = ' DB2: %s, %s, %s' % (ee.args[0], ee.args[1], ee.args[2])
                wx.MessageBox(m.decode(self.str_encode), u'query_schemas error', wx.OK, self.last_dlg)
                return None

            if isSingleLine:
                return [f1[i][0] for i in range(len(f1))]
            else:
                return (f1, )

    def query_schemas_and_show(self, L):
        typestr = self.choiceType.GetStringSelection()
        if typestr == '':  return
        if L == 1:
            if not self.Obj1['dbX']: return
            objs = self.query_schemas(self.Obj1['dbX'].cs, typestr)
            if objs:
                if type(objs) == type(()):
                    self.stcM1.SetValue(str(objs[0]))
                    self.set_obj_ctrl_s(True)
                else:
                    self.choiceSchema1.Clear()
                    self.choiceSchema1.AppendItems(objs)
                    self.set_obj_ctrl_s(False)
        elif L == 2:
            if not self.Obj2['dbX']: return
            objs = self.query_schemas(self.Obj2['dbX'].cs, typestr)
            if objs:
                if type(objs) == type(()):
                    self.stcM2.SetValue(str(objs[0]))
                    self.set_obj_ctrl_s(True)
                else:
                    self.choiceSchema2.Clear()
                    self.choiceSchema2.AppendItems(objs)
                    self.set_obj_ctrl_s(False)
        else:
            print 'unknow'

    def OnChoiceTypeChoice(self, event):
        event.Skip()
        self.query_schemas_and_show(1)
        self.query_schemas_and_show(2)

    def OnChoiceDb1Choice(self, event):
        event.Skip()
        self.Obj1['dbX'] = self.get_db2db_from_connect_string(self.choiceDb1.GetStringSelection())
        self.query_schemas_and_show(1)

    def OnChoiceDb2Choice(self, event):
        event.Skip()
        self.Obj2['dbX'] = self.get_db2db_from_connect_string(self.choiceDb2.GetStringSelection())
        self.query_schemas_and_show(2)

    # -------- schema objects --------
    def query_schema_objects(self, cs, typestr, schema):
        '''using cursor query owner = %schema% objects
        @param cs:
        @param typestr:
        @param schema:
        @return:  None or objects list
        '''
        schema2 = schema.replace("'","''")
        if typestr == 'TABLE':
            vt = """select TABNAME from SYSCAT.TABLES where TYPE='T' and TABSCHEMA='%s' order by TABNAME""" % schema2
        elif typestr == 'VIEW':
            vt = """select TABNAME from SYSCAT.TABLES where TYPE='V' and TABSCHEMA='%s' order by TABNAME""" % schema2
        elif typestr == 'SUMMARY TABLE':
            vt = """select TABNAME from SYSCAT.TABLES where TYPE='S' and TABSCHEMA='%s' order by TABNAME""" % schema2
        elif typestr == 'NICKNAME':
            vt = """select TABNAME from SYSCAT.NICKNAMES where TABSCHEMA='%s' order by TABNAME""" % schema2
        elif typestr == 'FUNCTION':
            vt = """select FUNCNAME from SYSCAT.FUNCTIONS where FUNCSCHEMA='%s' order by FUNCNAME""" % schema2
        elif typestr == 'TRIGGER':
            vt = """select TRIGNAME from SYSCAT.TRIGGERS where TRIGSCHEMA='%s' order by TRIGNAME""" % schema2
        elif typestr == 'PROCEDURE':
            vt = """select PROCNAME from SYSCAT.PROCEDURES where PROCSCHEMA='%s' order by PROCNAME""" % schema2
        else:
            vt = ''
            print '   unknown  ??? '
            return None

        try:
            cs.execute(vt)
            f = cs.fetchall()
            objs = [f[i][0] for i in range(len(f))]
            return objs
        except DB2.Error as ee:
            m = ' DB2: %s, %s, %s' % (ee.args[0], ee.args[1], ee.args[2])
            wx.MessageBox(m.decode(self.str_encode), u'query_schema_objects error', wx.OK, self.last_dlg)
            return None

    def query_schema_objects_and_show(self, L):
        typestr = self.choiceType.GetStringSelection()
        if typestr == '':  return
        if L == 1:
            cs = self.Obj1['dbX'].cs
            schema = self.choiceSchema1.GetStringSelection()
            if not cs or schema == '':  return
            objs = self.query_schema_objects(cs, typestr, schema)
            self.Obj1['type'] = typestr
            self.Obj1['value'] = objs
            if objs:
                self.lstT1.Clear()
                self.lstT1.AppendItems(objs)
        elif L == 2:
            cs = self.Obj2['dbX'].cs
            schema = self.choiceSchema2.GetStringSelection()
            if not cs or schema == '':  return
            objs = self.query_schema_objects(cs, typestr, schema)
            self.Obj2['type'] = typestr
            self.Obj2['value'] = objs
            if objs:
                self.lstT2.Clear()
                self.lstT2.AppendItems(objs)
        else:
            print 'unknow '

    def OnChoiceSchema1Choice(self, event):
        event.Skip()
        self.query_schema_objects_and_show(1)


    def OnChoiceSchema2Choice(self, event):
        event.Skip()
        self.query_schema_objects_and_show(2)

    # -------- filter --------
    def get_match_list(self, ori, matchstr):
        match = []
        matchstr = '.*%s.*' % matchstr.replace('*', '.*').replace('?', '.')
        for i in ori:
            if re.match(matchstr, i, re.IGNORECASE | re.UNICODE):
                match.append(i)
        return match

    def OnTxtI1Text(self, event):
        event.Skip()
        matchstr = self.txtI1.GetValue()
        new = self.get_match_list(self.Obj1['value'], matchstr)
        self.lstT1.Clear()
        self.lstT1.SetItems(new)

    def OnTxtI2Text(self, event):
        event.Skip()
        matchstr = self.txtI2.GetValue()
        new = self.get_match_list(self.Obj2['value'], matchstr)
        self.lstT2.Clear()
        self.lstT2.SetItems(new)

    # -------- schema object detail --------
    def query_schema_object_detail(self, cs, typestr, schema, objname, textMsg):
        '''query_schema_object_detail
        @param cs: cursor
        @param typestr:
        @param schema:
        @param objname:
        @param textMsg:
        @return:  None , values write to textMesg TextCtrl
        '''
        owner2 = schema.replace("'","''")
        objname2 = objname.replace("'","''")
        textMsg.ClearAll()
        isR = False

        if typestr == 'TABLE':
            vts = [
                """select COLNAME, TYPENAME, LENGTH, SCALE, DEFAULT, NULLS
                    from SYSCAT.COLUMNS where TABSCHEMA='%s' and TABNAME='%s' order by COLNAME""" % (owner2, objname2),
                """select TABSCHEMA, TABNAME, COLNAMES, UNIQUERULE, TBSPACEID
                    from SYSCAT.INDEXES  where TABSCHEMA='%s' and TABNAME='%s' order by COLNAMES""" % (owner2, objname2),
                """select TABSCHEMA, TABNAME, COLNAME
                    from SYSCAT.KEYCOLUSE where TABSCHEMA='%s' and TABNAME='%s' order by CONSTNAME""" % (owner2, objname2),
            ]
            msg = [u'''\n\n---- COLUMNS:\n---- COLNAME, TYPENAME, LENGTH, SCALE, DEFAULT, NULLS ----\n''' ,
                   u'''\n\n---- INDEXS:\n---- TABSCHEMA, TABNAME, COLNAMES, UNIQUERULE, TBSPACEID ----\n''' ,
                   u'''\n\n---- KEYS:\n---- TABSCHEMA, TABNAME, COLNAME ----\n''' ,
                   ]

            for i in range(len(vts)):
                textMsg.AppendText(msg[i])
                try:
                    cs.execute(vts[i])
                    f = cs.fetchall()
                    textMsg.AppendText('\n'.join([str(f[i]).decode(self.str_encode) for i in range(len(f))]))
                except DB2.Error as ee:
                    m = ' DB2: %s, %s, %s%s\n' % (ee.args[0], ee.args[1], ee.args[2], u'--' *50)
                    wx.MessageBox(m.decode(self.str_encode), u'query_schema_object_detail error', wx.OK, self.last_dlg)
                    textMsg.AppendText(m.decode(self.str_encode))
            isR = True
        elif typestr == 'VIEW':
            vt = """select TEXT from SYSCAT.VIEWS where VIEWSCHEMA='%s' and VIEWNAME='%s'""" % (owner2, objname2)
        elif typestr == 'SUMMARY TABLE':
            msg = """  'SUMMARY TABLE': %s %s """ % (schema, objname)
            textMsg.AppendText(msg.decode(self.str_encode))
            isR = True
        elif typestr == 'NICKNAME':
            vt = """select SERVERNAME || ':' || REMOTE_SCHEMA || ':' || REMOTE_TABLE from SYSCAT.NICKNAMES where TABSCHEMA='%s' and TABNAME='%s'""" % (owner2, objname2)
        elif typestr == 'FUNCTION':
            vt = """select BODY from SYSCAT.FUNCTIONS where FUNCSCHEMA='%s' and FUNCNAME='%s'""" % (owner2, objname2)
        elif typestr == 'TRIGGER':
            vt = """select TEXT from SYSCAT.TRIGGERS where TRIGSCHEMA='%s' and TRIGNAME='%s'""" % (owner2, objname2)
        elif typestr == 'PROCEDURE':
            vt = """select TEXT from SYSCAT.PROCEDURES where PROCSCHEMA='%s' and PROCNAME='%s'""" % (owner2, objname2)
        else:
            print '   unknown  ??? '
            isR = True
            return

        if not isR:
            try:
                cs.execute(vt)
                f = cs.fetchall()
                textMsg.AppendText(str(f[0][0]))
            except DB2.Error as ee:
                m = ' DB2: %s, %s, %s' % (ee.args[0], ee.args[1], ee.args[2])
                wx.MessageBox(m.decode(self.str_encode), u'query_schema_object_detail error', wx.OK, self.last_dlg)
        textMsg.ShowPosition(0)

    def query_schema_object_detail_and_show(self, L):
        if L == 1:
            cs = self.Obj1['dbX'].cs
            typestr = self.Obj1['type']
            schema1 = self.choiceSchema1.GetStringSelection()
            objname1 = self.lstT1.GetStringSelection()
            if not cs or len(typestr) == 0  or len(schema1) == 0 or len(objname1) == 0:
                return
            self.query_schema_object_detail(cs, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.stcM1)

            if self.chkLink.GetValue():
                try:
                    i = self.lstT2.GetItems().index(objname1)
                    self.lstT2.SetSelection(i)
                    cs = self.Obj1['dbX'].cs
                    schema2 = self.choiceSchema2.GetStringSelection()
                    if not cs or len(schema2) == 0 or len(objname1) == 0:
                        return
                    self.query_schema_object_detail(cs, typestr, schema2.encode(self.str_encode), objname1.encode(self.str_encode), self.stcM2)
                except ValueError:
                    self.stcM2.SetValue(u'%s no exists.' % objname1)
                    self.staticText_Msg.SetLabel(u'%s.%s                   == ?' % (schema1, objname1))
                    self.staticText_Msg.SetForegroundColour(wx.Color(255, 0, 0))
                    return
                self.compare_text(schema1,objname1,schema2)
        elif L == 2:
            cs = self.Obj2['dbX'].cs
            typestr = self.Obj2['type']
            schema2 = self.choiceSchema2.GetStringSelection()
            objname2 = self.lstT2.GetStringSelection()
            if not cs or len(typestr) == 0   or len(schema2) == 0 or len(objname2) == 0:
                return
            self.query_schema_object_detail(cs, typestr, schema2.encode(self.str_encode), objname2.encode(self.str_encode), self.stcM2)

            if self.chkLink.GetValue():
                try:
                    i = self.lstT1.GetItems().index(objname2)
                    self.lstT1.SetSelection(i)
                    cs = self.Obj2['dbX'].cs
                    schema1 = self.choiceSchema1.GetStringSelection()
                    if not cs or len(schema1) == 0 or len(objname2) == 0:
                        return
                    self.query_schema_object_detail(cs, typestr, schema1.encode(self.str_encode), objname2.encode(self.str_encode), self.stcM1)
                except ValueError:
                    self.stcM1.SetValue(u'%s no exists.' % objname2)
                    self.staticText_Msg.SetLabel(u' ?                      == %s.%s' % (schema2, objname2))
                    self.staticText_Msg.SetForegroundColour(wx.Color(255, 0, 0))
                    return
                self.compare_text(schema1,objname2,schema2)
        else:
            print 'unknow '

    def OnLstT1Listbox(self, event):
        event.Skip()
        self.OnNbM1NotebookPageChanged(None)

    def OnLstT2Listbox(self, event):
        event.Skip()
        self.OnNbM2NotebookPageChanged(None)

    def query_schema_object_table(self, db2db, typestr, schema, tabname, gridX, typeid):
        '''query_schema_object_detail
        @param db2db: Db2db()
        @param typestr:
        @param schema:
        @param tabname:
        @param gridX
        @param typeid: 1 table view columns    2 data     3  count
        '''
        cs = db2db.cs
        if typestr == 'TABLE' or typestr == 'VIEW' or typestr == 'SUMMARY TABLE' or typestr == 'NICKNAME':
            if typeid == 1:
                vt = """select COLNAME, TYPENAME, LENGTH, SCALE, DEFAULT, NULLS from SYSCAT.COLUMNS 
                    where TABSCHEMA='%s' and TABNAME='%s' order by COLNAME""" % (schema.replace("'","''"), tabname.replace("'","''"))
                tabname = 'columns'
            elif typeid == 2:
                vt = """select * from "%s"."%s" where 1=1""" % (schema, tabname)
            elif typeid == 3:
                vt = """select count(*) from "%s"."%s" where 1=1""" % (schema, tabname)
                tabname = 'count'
            else:
                print ' unknow ?? '
                return
        else:
            return
        try:
            self.execSQL(cs, vt, self.getts()[0])
            data, rese = self.fetchData(cs, vt)
            if rese and len(data) == 0: raise rese
            description2 = cs._description2()
            self.new_page__show_data(data, description2, db2db, schema, tabname, vt, '', gridX)
            gridX.MakeCellVisible(len(data)-1, 0)
            if rese: raise rese
        except DB2.Error as ee:
            m = ' DB2: %s, %s, %s' % (ee.args[0], ee.args[1], ee.args[2])
            wx.MessageBox(m.decode(self.str_encode), u'query_schema_object_table error', wx.OK, self.last_dlg)
        except Exception as ee:
            m = '%s' % str(ee)
            wx.MessageBox(m.decode(self.str_encode), u'query_schema_object_table error', wx.OK, self.last_dlg)

    def OnNbM1NotebookPageChanged(self, event=None):
        try:
            pos = event.GetSelection()
            event.Skip()
        except Exception as _ee: #' pubsub lstT1'
            pos =self.nbM1.GetSelection()
        if not hasattr(self, 'Obj1'):return
        self.nbchange = True
        dbX = self.Obj1['dbX']
        typestr = self.Obj1['type']
        schema1 = self.choiceSchema1.GetStringSelection()
        objname1 = self.lstT1.GetStringSelection()
        if not dbX or len(typestr) == 0  or len(schema1) == 0 or len(objname1) == 0:
            return
        if pos == 0:
            self.query_schema_object_detail_and_show(1)
        elif pos == 1:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM11, pos)
        elif pos == 2:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM12, pos)
        elif pos == 3:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM13, pos)

    def OnNbM2NotebookPageChanged(self, event=None):
        try:
            pos = event.GetSelection()
            event.Skip()
        except Exception as _ee: #' pubsub lstT2'
            pos =self.nbM2.GetSelection()
        if not hasattr(self, 'Obj2'):return
        self.nbchange = True
        dbX = self.Obj2['dbX']
        typestr = self.Obj2['type']
        schema1 = self.choiceSchema2.GetStringSelection()
        objname1 = self.lstT2.GetStringSelection()
        if not dbX or len(typestr) == 0  or len(schema1) == 0 or len(objname1) == 0:
            return
        if pos == 0:
            self.query_schema_object_detail_and_show(2)
        elif pos == 1:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM21, pos)
        elif pos == 2:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM22, pos)
        elif pos == 3:
            self.query_schema_object_table(dbX, typestr, schema1.encode(self.str_encode), objname1.encode(self.str_encode), self.gridM23, pos)

    def OnSplitterWindowObject1LeftDclick(self, event):
        event.Skip()
        psz = self.splitterWindowObject1.GetSize()
        if wx.SPLIT_HORIZONTAL == self.splitterWindowObject1.GetSplitMode():
            self.splitterWindowObject1.SetSplitMode(wx.SPLIT_VERTICAL)
            self.splitterWindowObject1.SetSashPosition(psz.x/2)
        else:
            self.splitterWindowObject1.SetSplitMode(wx.SPLIT_HORIZONTAL)
            self.splitterWindowObject1.SetSashPosition(psz.y/2)
        self.splitterWindowObject1.UpdateSize()
        self.resize_p_objects(False)

    def OnSplitterWindowObject2LeftDclick(self, event):
        event.Skip()
        psz = self.splitterWindowObject2.GetSize()
        if wx.SPLIT_HORIZONTAL == self.splitterWindowObject2.GetSplitMode():
            self.splitterWindowObject2.SetSplitMode(wx.SPLIT_VERTICAL)
            self.splitterWindowObject2.SetSashPosition(psz.x/2)
        else:
            self.splitterWindowObject2.SetSplitMode(wx.SPLIT_HORIZONTAL)
            self.splitterWindowObject2.SetSashPosition(psz.y/2)
        self.splitterWindowObject2.UpdateSize()

    def OnSplitterWindowObjectSplitterSashPosChanged(self, event):
        event.Skip()
        self.splitterWindowObject.UpdateSize()
        self.splitterWindowObject1.UpdateSize()
        self.resize_p_objects(False)

    # -------- control event --------
    def compare_text(self, schema1='', objname='', schema2=''):
        if self.stcM1.GetValue().strip() == self.stcM2.GetValue().strip():
            msgs = 'info: %s.%s == %s.%s' % (schema1, objname, schema2, objname)
            self.staticText_Msg.SetLabel(msgs.decode(self.str_encode))
            self.staticText_Msg.SetForegroundColour(wx.Color(0, 0, 0))
        else:
            msgs = 'INFO: %s.%s <> %s.%s' % (schema1, objname, schema2, objname)
            self.staticText_Msg.SetLabel(msgs.decode(self.str_encode))
            self.staticText_Msg.SetForegroundColour(wx.Color(255, 0, 0))


    def OnBtnCompareButton(self, event):
        if self.lstT1.GetStringSelection() == '' and self.lstT2.GetStringSelection() == '':
            print '  Comare: no select'
            try:
                self.tmpcur.execute(''' create table LL (a)''')
                self.tmpcur.execute(''' create table RR (a)''')
            except Exception as _ee:
                pass
            self.tmpcur.execute(''' delete from  LL ''')
            self.tmpcur.execute(''' delete from  RR ''')
            self.tmpcur.executemany(''' insert into LL values (?) ''' , [(i,) for i in self.Obj1['value'] ])
            self.tmpcur.executemany(''' insert into RR values (?) ''' , [(i,) for i in self.Obj2['value'] ])

            typestr = self.choiceType.GetStringSelection()
            try:
                self.tmpcur.execute('''select a from LL where a not in (select a from RR) ''')
                f = self.tmpcur.fetchall()
                ows = self.choiceSchema1.GetStringSelection()
                ow = u'' if ows == u'' else u'"%s".' % ows.encode(self.str_encode)
                self.stcM1.SetValue(u'\n'.join([ u'drop %s  %s"%s" ; ' % (typestr, ow, str(s[0]).decode(self.str_encode)) for s in f]))
            except Exception as ee:
                print '11 %s' % str(ee)

            try:
                self.tmpcur.execute('''select a from RR where a not in (select a from LL) ''')
                f = self.tmpcur.fetchall()
                ows = self.choiceSchema2.GetStringSelection()
                ow = u'' if ows == u'' else u'"%s".' % ows.encode(self.str_encode)
                self.stcM2.SetValue(u'\n'.join([ u'drop %s  %s"%s" ; ' % (typestr, ow, str(s[0]).decode(self.str_encode)) for s in f]))
            except Exception as ee:
                print '22 %s' % str(ee)
        else:
            print '  Compare: diff text'
            self.compare_text_used_file()

        self.tmpdb.commit()
        event.Skip()

    def compare_text_used_file(self):
        ''' compare_text_used_file   -  compare 2 table define '''
        f1 = tempfile.NamedTemporaryFile(prefix='dbtl_', delete=False)
        f2 = tempfile.NamedTemporaryFile(prefix='dbtr_', delete=False)
        f1.write(self.stcM1.GetValue())
        f2.write(self.stcM2.GetValue())
        f1.close()
        f2.close()
        try:
            os.system('%s %s %s' % (self.difftool, f1.name.encode(self.str_encode), f2.name.encode(self.str_encode)))
        except Exception as ee:
            wx.MessageBox(str(ee).decode(self.str_encode), _("Error"), wx.OK | wx.ICON_ERROR, self.last_dlg)
#        os.unlink(f1.name)
#        os.unlink(f2.name)

    def OnBtnExportDDLButton(self, event):
        print 'OnBtnExportDDLButton'
        event.Skip()

    def OnCbxLinkCheckbox(self, event):
        self.staticText_Msg.SetForegroundColour(wx.Color(0, 0, 0))
        if self.chkLink.GetValue():
            self.staticText_Msg.SetLabel(_('compare'))
            self.btnFormatSpace.Enable()
        else:
            self.staticText_Msg.SetLabel(_('message'))
            self.btnFormatSpace.Disable()
        event.Skip()

    def OnBtnFormatSpaceButton(self, event):
        if self.choiceType.GetStringSelection() == 'VIEW':
            for tt in [self.stcM1, self.stcM2]:
                mi = tt.GetValue().encode(self.str_encode)
                mi = re.sub('\s*\(\s*', ' (', mi)
                mi = re.sub('\s*\)\s*', ') ', mi)

                mi = re.sub('\s*=\s*', '=', mi)
                mi = re.sub('\s*>\s*', '>', mi)
                mi = re.sub('\s*>=\s*', '>=', mi)
                mi = re.sub('\s*<\s*', '<', mi)
                mi = re.sub('\s*<=\s*', '<=', mi)
                mi = re.sub('\s*!=\s*', '!=', mi)
                mi = re.sub('\s*==\s*', '==', mi)
                mi = re.sub('\s*<>\s*', '<>', mi)
                mi = re.sub('\s*\|\|\s*', '||', mi)

                mi = re.sub('\s*,\s*', ', ', mi)
                mi = re.sub('\s+', ' ', mi)
                mi = re.sub(r'\s*(\d+)\s*,\s*(\d+)', r'\1,\2', mi)

#                i = mi[:50].upper().find(' AS ')
#                mi = mi[i+4:]
                tt.SetValue(mi.decode(self.str_encode))
        else:
            print ' NO implement. no view bold '

        #self.stcM1.SetEditable(True)
        #self.stcM2.SetEditable(True)
        self.compare_text()
        event.Skip()

    # ------------------------------------------------------------------------
    # ---------- python exec page ----------
    def OnBtnExecPythonButton(self, event):
        if event: event.Skip()
        self.execPython()

    def execPython(self):
        '''
        @note: from stc control get string, default is unicode
        use exec command execute this string, if string has quote string, and string not has u'', 
        used it to python or sql, may be occurrence wrong;
        Or transform unicode string to local string, but  subset quote string has u''
        
        EXAMPLE:
        exec(u"""a="some not ascii char" ; print a """)
        # on print , occurrence invalid code
        # on use a to another , may occurrence UnicodeDecodeError or UnicodeEncodeError
        '''
        self.stcPython.SetFocus()
        pystr = self.stcPython.GetSelectedText().strip().encode(self.str_encode)
        pystr = pystr.replace('\r\n','\n').replace('\r','\n')
        if pystr == '':
            return

        if self.python_exec_redirect_std:
            # exec python source string may be output some message, self 's write method use a StringIO record it.
            try:
                self.write_ds.truncate(0)
            except Exception as ee:
                self.write_ds = StringIO.StringIO()
            self.write_ds.write('#[[[ <%s> PYTHON EXEC:\n%s\n]]]\n' % (time.strftime(self.str_time_strf), pystr))
            self.stdii, self.stdoo, self.stdee = sys.stdin, sys.stdout, sys.stderr
            sys.stdin, sys.stdout, sys.stderr = self, self, self
        dlg = None
        try:
            try:
                msgs =  pystr[:80].decode(self.str_encode)
            except Exception as _ee:
                msgs = u' exec split er'
            try:
                dlg = wx.ProgressDialog(_('exec ...'), msgs, 100, self, style=wx.PD_ELAPSED_TIME)
            except Exception as _ee:
                pass
            llast_dlg = self.last_dlg
            if dlg:
                self.last_dlg = dlg
                dlg.Update(50)
            #exec(pystr)     # 
            pycom = compile(pystr, '', 'exec')
            exec(pycom)
        except Exception as ee:
            errds = StringIO.StringIO()
            errds.write('<<< EXEC EXCEPT: \n')
            for i in range(len(ee.args)):
                if type(ee.args[i]) ==  type(()) or type(ee.args[i]) == type([]):
                    errds.write(' [')
                    for j in range(len(ee.args[i])):
                        errds.write(str(ee.args[i][j]))
                        errds.write(', ')
                    errds.write('] ')
                else:
                    errds.write(str(ee.args[i]))
            errds.write('\n>>>\n')
            print errds.getvalue()
        finally:
            self.last_dlg = llast_dlg
            if dlg: dlg.Destroy()
            if hasattr(self,'stdii'):    # not use if self.python_exec_redirect_std:
                sys.stdin, sys.stdout, sys.stderr = self.stdii, self.stdoo, self.stdee
                del self.stdii, self.stdoo, self.stdee
            if self.write_ds.len > 0:
                self.log_pg(self.write_ds.getvalue())
                self.write_ds.truncate(0)
        pass

    def isatty(self):
        return False

    def pstdatty(self):
        self.stcExecLog.AppendText(u' sys.stdin, out, err isatty: %s, %s, %s\n' % (sys.stdin.isatty(),sys.stdout.isatty(),sys.stderr.isatty()))

    def write(self, *args):
        ''' not call. used in exec string redirect stdout stderr messages.
        @param *args: 
        '''
        for i in args:
            val = str(i)
            self.write_ds.write(val)
            self.stcPythonLog.AppendText(val.decode(self.str_encode))

    def read(self, msg=u'sys.stdin.read() ', israw=False):
        '''
        @param msg:
        @param israw:
        @return:  unicode string
        '''
        dlg = wx.TextEntryDialog(self.last_dlg, msg, _('Input:'), '')
        try:
            dlg.ShowModal()
            s = dlg.GetValue()
            if israw:
                if s == u'':
                    return u'\n'
                else:
                    return s
            else:
                return s.strip()
        finally:
            dlg.Destroy()

    def readline(self, *args):
        ss = u''
        for i in args:
            ss += str(i).decode(self.str_encode)
        return self.read(u'sys.stdin.readline() : %s' % ss, True)

    def readlines(self, *args):
        ss = u''
        for i in args:
            ss += str(i).decode(self.str_encode)
        return self.read(u'sys.stdin.readlines() : %s' % ss, True)

    # ------------------------------------------------------------------------
    # ---------- user functions ----------
    def log_pg(self, text=''):
        try:
            self.logpgf.write(text)
            self.textConnMsg.AppendText(text.decode(self.str_encode))
            self.textConnMsg.ShowPosition(self.textConnMsg.GetLastPosition())
        except Exception as _ee:
            pass
        print text,

    def log_usersql(self, text='', isSwitchTab=False, isWriteToFile=False):
        ''' append to stcExecLog,  and or SwitchTab,  and or WriteToFile
        @param text:
        @param isSwitchTab: defautl False
        @param isWriteToFile: defautl False
        '''
        try:
            if isWriteToFile:
                self.logsqlf.write(text)
            if isSwitchTab:
                self.nbResult.SetSelection(0)
            self.stcExecLog.AppendText(text.decode(self.str_encode))
            self.stcExecLog.ShowPosition(self.stcExecLog.GetLastPosition())
        except Exception as _ee:
            pass

    def log_usersql2(self, text=''):
        ''' write text to file
        @param text:
        '''
        try:
            self.logsqlf.write(text)
        except Exception as _ee:
            pass

    def log_user(self, text=''):
        print text,

    def ss_set_icon(self, args=None):
        for i in images.index:
            print i
            time.sleep(2)
            try:
                ic = images.catalog[i].GetIcon()
                self.SetIcon(ic)
            except Exception as ee:
                print ee

    # -------- textCtrl maxlen event --------
    def OnTextConnMsgTextMaxlen(self, event):
        self.textConnMsg.Clear()
        event.Skip()

    # --------
    # -------- all treeCtrl and Load Save btn event --------
    def treectrl_delete_item(self, treeCtrl, itemtype, itemname, codetype):
        '''delete tree item, not delete database
        @param treeCtrl:
        @param itemtype:
        @param itemname:
        @param codetype: value in ['sql', 'python', 'code']
        '''
        root = treeCtrl.GetRootItem()
        if not root.IsOk():
            self.snippet_refresh_from_table(codetype, treeCtrl)
            return
        try:
            item, cookie = treeCtrl.GetFirstChild(root)
            item2, cookie2 = None, None
            while item:
                if treeCtrl.GetItemText(item) == itemtype:
                    item2, cookie2 = treeCtrl.GetFirstChild(item)
                    break
                item, cookie = treeCtrl.GetNextChild(item, cookie)
            while item2:
                if treeCtrl.GetItemText(item2) == itemname:
                    treeCtrl.Delete(item2)
                    msg = u' delete %s ( %s, %s ) treeCtrl' % (codetype, itemtype, itemname)
                    self.log_pg(msg.encode(self.str_encode))
                    return
                item2, cookie2 = treeCtrl.GetNextChild(item2, cookie2)
            print ' no find'
        finally:
            treeCtrl.SelectItem(root)

    def treectrl_add_item(self, treeCtrl, itemtype, itemname, codetype):
        '''add tree item , not insert database
        @param treeCtrl:
        @param itemtype: typestr
        @param itemname: name
        @param codetype: value in ['sql', 'python', 'code']
        '''
        root = treeCtrl.GetRootItem()
        if not root.IsOk(): # not show, refresh
            self.snippet_refresh_from_table(codetype, treeCtrl)
            return
        try:
            item, cookie = treeCtrl.GetFirstChild(root)
            while item:
                if treeCtrl.GetItemText(item) == itemtype:
                    its = treeCtrl.AppendItem(item, itemname)
                    return
                item, cookie = treeCtrl.GetNextChild(item, cookie)
            item = treeCtrl.AppendItem(root, itemtype)
            its = treeCtrl.AppendItem(item, itemname)
        finally:
            treeCtrl.Refresh()
            treeCtrl.Expand(root)
            treeCtrl.Expand(item)
            treeCtrl.SelectItem(its)
            print ' add %s , %s ' % (itemtype, itemname)
    
    def treectrl_selected(self, codetype, treectrl, stcctrl, item):
        '''
        @param codetype:
        @param treectrl:
        @param stcctrl:
        @param item: event.GetItem()
        '''
        if item == treectrl.GetRootItem(): return
        itemp = treectrl.GetItemParent(item)
        if itemp == treectrl.GetRootItem(): return
        typestr = treectrl.GetItemText(itemp)
        name = treectrl.GetItemText(item)
        try:
            val = self.cfg.snippet_table_select_1row(codetype, typestr, name)
            if val and val.strip() != stcctrl.GetSelectedText().strip():
                #li = stcctrl.GetCurrentLine()
                #pos = stcctrl.GetLineEndPosition(li)
                pos = stcctrl.GetCurrentPos()
                stcctrl.BeginUndoAction()
                stcctrl.AddText(u'\n%s\n' % val)
                stcctrl.EndUndoAction()
                pos2 = stcctrl.GetCurrentPos()
                stcctrl.SetSelectionStart(pos)
                stcctrl.SetSelectionEnd(pos2)
                stcctrl.EnsureCaretVisible()
        except Exception as ee:
            print ee
            pass
        self.time_seteditfocus.Start(100, True)

    def snippet_refresh_from_table(self, codetype, treeCtrl):
        ''' select type,name from TABLE, add to treeCtrl
        @param codetype: value in ['sql', 'python', 'code']
        @param treeCtrl:
        '''
        treeCtrl.DeleteAllItems()
        root = treeCtrl.AddRoot(u'Code')
        types, names = self.cfg.snippet_table_select_all(codetype)
        for i in range(len(types)):
            it = treeCtrl.AppendItem(root, types[i])
            for j in range(len(names[i])):
                treeCtrl.AppendItem(it, names[i][j])
        #treeCtrl.ExpandAll()
        treeCtrl.Expand(root)
        treeCtrl.SelectItem(root)
        self.time_seteditfocus.Start(100, True)

    def snippet_add_item(self, codetype, textCtrl, treeCtrl):
        ''' from textCtrl get Selection String , get type and name, save to config,  show to treeCtrl
        @param codetype: config file table, value in ['sql', 'python', 'code']
        @param textCtrl:
        @param treeCtrl:
        '''
        code = textCtrl.GetStringSelection().strip()
        if code == '':
            wx.MessageBox(_(' no select value'), _('Error'), wx.OK, self.last_dlg)
            return
        dlg = wx.TextEntryDialog(self.last_dlg, _('Please input TYPE and NAME, comma split : '), u'Type,Name', u'', style=wx.OK | wx.CANCEL)
        try:
            if wx.ID_OK == dlg.ShowModal():
                s = dlg.GetValue().strip().split(',')
                if len(s) != 2:
                    wx.MessageBox(_('  input error'), _('Error'), wx.OK, self.last_dlg)
                    return
                typestr, name = s[0].strip(), s[1].strip()
                if typestr == u'' or name == u'':
                    wx.MessageBox(_('  input error'), _('Error'), wx.OK, self.last_dlg)
                    return
                try:
                    if self.cfg.snippet_table_select_1row(codetype, typestr, name):
                        if wx.YES != wx.MessageBox(_('Data alread exists. override ? '), _('Ask'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self.last_dlg):
                            return
                        else:
                            self.cfg.snippet_table_delete(codetype, typestr, name)
                    self.cfg.snippet_table_insert(codetype, typestr, name, code)
                    self.treectrl_add_item(treeCtrl, typestr, name, codetype)
                except Exception as _ee:
                    pass
        finally:
            dlg.Destroy()
            textCtrl.SetFocus()

    def snippet_delete_item(self, codetype, treeCtrl, item):
        '''delete treeCtrl selected item, and config db table 's data
        @param codetype:
        @param treeCtrl:
        @param item:    treeCtrl rightclick event.GetItem()
        '''
        try:
            root = treeCtrl.GetRootItem()
            itemp = treeCtrl.GetItemParent(item)
            if item == root or itemp == root:
                self.time_seteditfocus.Start(100, True)
                return
            typestr = treeCtrl.GetItemText(itemp)
            name = treeCtrl.GetItemText(item)
        except Exception as _ee:
            return
        if wx.YES == wx.MessageBox(u'Delete [ %s %s ] ?' % (typestr, name), _('Ask'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self.last_dlg):
            n = self.cfg.snippet_table_delete(codetype, typestr, name)
            treeCtrl.Delete(item)
            treeCtrl.SelectItem(root)
            msg = u' delete %s ( %s, %s ) applied  %s ' % (codetype, typestr, name, n)
            self.log_pg(msg.encode(self.str_encode))
        self.time_seteditfocus.Start(100, True)
    
    # -------- sql --------
    def OnTreeSQLsTreeSelChanged(self, event):
        event.Skip()
        return self.treectrl_selected('sql', self.treeSQLs, self.stcSQLs, event.GetItem())

    def OnTreeSQLsTreeItemRightClick(self, event):
        self.snippet_delete_item('sql', self.treeSQLs, event.GetItem())
        event.Skip()

    def OnBtnSQLReloadButton(self, event):
        self.snippet_refresh_from_table('sql', self.treeSQLs)
        if self.splitterWindowExec1.GetSashPosition() < 20:
            self.splitterWindowExec1.SetSashPosition(120)
        event.Skip()
        
    def OnBtnSQLSaveButton(self, event):
        self.snippet_add_item('sql', self.stcSQLs, self.treeSQLs)
        event.Skip()

    def OnTreeSQLsTreeBeginDrag(self, event):
        event.Skip()

    # -------- python --------
    def OnTreePythonTreeSelChanged(self, event):
        event.Skip()
        return self.treectrl_selected('python', self.treePython, self.stcPython, event.GetItem())

    def OnTreePythonTreeItemRightClick(self, event):
        self.snippet_delete_item('python', self.treePython, event.GetItem())
        event.Skip()

    def OnBtnPythonReloadButton(self, event):
        self.snippet_refresh_from_table('python', self.treePython)
        event.Skip()

    def OnBtnPythonSaveButton(self, event):
        self.snippet_add_item('python', self.stcPython, self.treePython)
        event.Skip()

    # -------- code snippet --------
    def OnTreeCodeSnippetTreeSelChanged(self, event):
        event.Skip()
        if self.textCodeSnippet.GetStringSelection(): return
        item = event.GetItem()
        if item == self.treeCodeSnippet.GetRootItem(): return
        itemp = self.treeCodeSnippet.GetItemParent(item)
        if itemp == self.treeCodeSnippet.GetRootItem(): return
        typestr = self.treeCodeSnippet.GetItemText(itemp)
        name = self.treeCodeSnippet.GetItemText(item)
        try:
            val = self.cfg.snippet_table_select_1row('code', typestr, name)
            if val:
                self.textCodeSnippet.SetValue(val)
        except Exception as ee:
            self.textCodeSnippet.SetValue(u'%s' % str(ee).decode(self.str_encode))
            pass
        self.time_seteditfocus.Start(100, True)

    def OnTreeCodeSnippetTreeItemRightClick(self, event):
        self.snippet_delete_item('code', self.treeCodeSnippet, event.GetItem())
        event.Skip()

    def OnBtnCodeReloadButton(self, event):
        self.snippet_refresh_from_table('code', self.treeCodeSnippet)
        event.Skip()

    def OnBtnCodeSaveButton(self, event):
        self.snippet_add_item('code', self.textCodeSnippet, self.treeCodeSnippet)
        event.Skip()

    def OnBtnDB2HelpButton(self, event):
        event.Skip()
        dlg = wx.TextEntryDialog(self.last_dlg, _('Input db2 statcode. SQL1234 '), u'db2 ? XXXX', u'SQL', style=wx.OK | wx.CANCEL)
        try:
            if wx.ID_OK == dlg.ShowModal():
                stxt = dlg.GetValue().strip().upper()
                val = self.cfg.snippet_table_select_1row('code', u'DB2', stxt)
                if not val:
                    ss = subprocess.Popen('db2 ? %s ' % stxt.encode(self.str_encode), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                    lls = ss.stdout.read()
                    self.textCodeSnippet.SetValue(lls)
                    self.cfg.snippet_table_insert('code', u'DB2', stxt, lls)
                self.snippet_refresh_from_table('code', self.treeCodeSnippet)
                self.treeCodeSnippet.ExpandAll()
        except Exception as _ee:
            pass
        finally:
            dlg.Destroy()

    # -----------------------------------------------------------
    # -------- menu ----------------------
    def OnMenuFileItems_saveMenu(self, event):
        print ''' OnMenuFileItems_saveMenu'''

    def OnMenuFileItems_reloadMenu(self, event):
        print ''' OnMenuFileItems_reloadMenu'''

    def OnMenuFileItem_exitMenu(self, event):
        if wx.YES == wx.MessageBox(_('Exit program ?'), _('Ask'), wx.YES_NO|wx.ICON_QUESTION, self):
            self.Close()
            
    def OnFind(self, event):
        ctl = self.ctl
        if not ctl: return

        et = event.GetEventType()
        flags = event.GetFlags()
        findTxt = event.GetFindString()
        self.findTxt = findTxt
        if et in [wx.wxEVT_COMMAND_FIND_REPLACE, wx.wxEVT_COMMAND_FIND_REPLACE_ALL]:
            replaceTxt = event.GetReplaceString()
        else:
            replaceTxt = u""

        try:
            if issubclass(ctl.__class__, wx.stc.StyledTextCtrl):
                stcflags= 0
                if flags & 2: stcflags &= wx.stc.STC_FIND_WHOLEWORD
                if flags & 4: stcflags &= wx.stc.STC_FIND_MATCHCASE
                oldpos = ctl.GetCurrentPos()
                b,e = ctl.GetSelectionStart(),ctl.GetSelectionEnd()
                ctl.SearchAnchor()
                if flags & 1:
                    ipos = ctl.SearchNext(stcflags, findTxt)    # bug?
                    if ipos == oldpos:
                        i = ctl.GetCurrentPos() + len(findTxt)
                        ctl.SetSelection(i,i)
                        ctl.SearchAnchor()
                        ipos = ctl.SearchNext(stcflags, findTxt)
                else:
                    ipos = ctl.SearchPrev(stcflags, findTxt)
                    if ipos == oldpos:
                        i = ctl.GetCurrentPos() - len(findTxt)
                        ctl.SetSelection(i,i)
                        ctl.SearchAnchor()
                        ipos = ctl.SearchPrev(stcflags, findTxt)
                if ipos != -1:
                    print ipos
                    ctl.EnsureCaretVisible()
                    return
                else:
                    ctl.SetSelectionStart(b)
                    ctl.SetSelectionEnd(e)
                    wx.MessageBox(u"Cann't find the:\n%s" % findTxt, _('msg'), wx.OK, event.GetDialog())
            elif issubclass(ctl.__class__, wx.TextCtrl):
                pass
            elif issubclass(ctl.__class__, wx.grid.Grid):
                pass
            elif ctl.GetName() =='grid window':
                gridX = self.FindWindowById(ctl.GetId()).GetParent()
                row, col = gridX.GetGridCursorRow(), gridX.GetGridCursorCol()
                if hasattr(gridX.GetTable(),'data'):
                    desc = gridX.description2[col]
                    descstr = '"%s" (%s/%s)' % (desc[0],desc[1],desc[2])
                    descstr = descstr.decode(self.str_encode)
                else:
                    descstr = gridX.GetColLabelValue(col)
                if flags & 2:   s = findTxt.replace('*','.*').replace('?','.')
                else:           s = '.*' + findTxt.replace('*','.*').replace('?','.') + '.*'
                if flags & 4:   f = 0
                else:           f = re.IGNORECASE
                for i in range(row + 1, gridX.GetNumberRows()):
                    if re.match(s, gridX.GetCellValue(i, col), f):   # bug?, no use match
                        gridX.SelectBlock(i, col, i, col)
                        gridX.SetGridCursor(i, col)
                        gridX.MakeCellVisible(i, col)
                        return
                for i in range(0, row + 1):
                    if re.match(s, gridX.GetCellValue(i, col), f):
                        gridX.SelectBlock(i, col, i, col)
                        gridX.SetGridCursor(i, col)
                        gridX.MakeCellVisible(i, col)
                        return
                wx.MessageBox(u"Cann't find the text at  %s:\n%s" % (descstr, findTxt), u'msg', wx.OK, event.GetDialog())
            elif issubclass(ctl.__class__, wx.ListCtrl):
                pass
            elif issubclass(ctl.__class__, wx.ListBox):
                s = '.*' + findTxt.replace('*','.*').replace('?','.') + '.*'
                ss = ctl.GetItems()
                ic = ctl.GetSelection()
                for i in range(ic+1, len(ss)):
                    if re.match(s, ss[i], re.IGNORECASE):
                        ctl.SetSelection(i)
                        wx.lib.pubsub.Publisher().sendMessage(ctl)
                        return
                for i in range(0, ic+1):
                    if re.match(s, ss[i], re.IGNORECASE):
                        ctl.SetSelection(i)
                        wx.lib.pubsub.Publisher().sendMessage(ctl)
                        return
                wx.MessageBox(u"Cann't find the :\n%s" % findTxt, u'msg', wx.OK, event.GetDialog())
            else:
                pass
        except Exception as ee:
            print ' onfind: %s' % str(ee)
        finally:
            pass
            #ctl.SetFocus()
                

    def dis_find(self, status):
        iss = self.menuEdit.GetMenuItems()
        for i in iss:
            if i.GetId() in [wxID_DBMMENUEDITITEMS_FIND, wxID_DBMMENUEDITITEMS_REPLACE]:
                i.Enable(status)

    def OnFindClose(self, event):
        dlg = event.GetDialog()
        if dlg: dlg.Destroy()
        self.dis_find(True)

    def OnMenuEditItems_findMenu(self, event):
        data = wx.FindReplaceData()
        data.SetFlags(wx.FR_DOWN)
        data.SetFindString(self.findTxt)
        dlg = wx.FindReplaceDialog(self, data, _('Find ...'))
        dlg.data = data
        self.ctl = self.FindFocus()
        dlg.Show(True)
        self.dis_find(False)

    def OnMenuEditItems_replaceMenu(self, event):
        data = wx.FindReplaceData()
        data.SetFlags(wx.FR_DOWN)
        data.SetFindString(self.findTxt)
        dlg = wx.FindReplaceDialog(self, data, _('Find & Replace ...'), wx.FR_REPLACEDIALOG)
        dlg.data = data
        self.ctl = self.FindFocus()
        dlg.Show(True)
        self.dis_find(False)

    def OnUpdateMenuExec(self, event):
        event.Enable(self.nbMainFrame.GetSelection() == self.iSQL  and \
            self.stcSQLs.GetSelectionStart() != self.stcSQLs.GetSelectionEnd() or \
            self.nbMainFrame.GetSelection() == self.iPYTHON  and \
            self.stcPython.GetSelectionStart() != self.stcPython.GetSelectionEnd())

    def OnUpdateMenuFormatSql(self, event):
        event.Enable(self.nbMainFrame.GetSelection() == self.iSQL  and \
            self.stcSQLs.GetSelectionStart() != self.stcSQLs.GetSelectionEnd() or \
            self.nbMainFrame.GetSelection() == self.iOBJECTS  and \
            self.ctl in [self.stcM1, self.stcM2 ] )

    def OnMenuExecItems_exec_sqlsMenu(self, event):
        curpos = self.nbMainFrame.GetSelection()
        if curpos == self.iSQL:
            self.execSQLs()
        elif curpos == self.iPYTHON:
            self.execPython()

    def OnMenuExecItems_exec_singleMenu(self, event):
        if self.nbMainFrame.GetSelection() != self.iSQL: return
        self.execSQLs(True)

    def OnMenuExecItems_format_sqlMenu(self, event):
        stcc = self.ctl
        if not stcc in [self.stcSQLs,self.stcM1,self.stcM2]: return
        ss = stcc.GetSelectedText()
        if len(ss) == 0: return
        beee = stcc.GetSelectionStart()
        stcc.ReplaceSelection(u'\n')
        az = sqld.QueryTokenizer()
        spc = self.getsplitchar()
        ss = az.tokenize(ss, self.str_encode, spc)
        for s in ss:
            s = sqlformatter.SQLFormatter(s[0]).format()
            s = s.decode(self.str_encode)
            stcc.AddText(s + u'\n %s\n' % spc)
        eeed = stcc.GetSelectionEnd()
        stcc.SetSelection(beee, eeed)

    def OnMenuHelpItems_help_aboutMenu(self, event):
        info = wx.AboutDialogInfo()
        info.Name = u"db2 tool"
        info.Version = u"0.0.9"
        info.Copyright = _("(C) 2010 Programmers and Coders Everywhere")
        info.Description = wx.lib.wordwrap.wordwrap(
            _('''A "db2 tool" program is a software program that IBM/DB2 utility tool'''),
            500, wx.ClientDC(self))
        #info.WebSite = ("emailto:windwiny.ubt@gmail.com", "emailto:")
        info.Developers = [u"windwiny.ubt@gmail.com", ]

        info.License = wx.lib.wordwrap.wordwrap(
            _('''GPL V2/3'''), 
            500, wx.ClientDC(self))

        wx.AboutBox(info)

    def testmsg(self):
        d1 = _('testmsg')
        d2 = 'testmsg'
        print type(d1),type(d2),d1,d2
        wx.MessageBox(d1,d2,wx.OK)

    def sqlcr(self ,event):
        print '--sqlcr call'
        self.sqlss,be,ed,ti = self.get_sqls_from_stcSQLs()
        self.iXX = -1
        print be,ed,ti,
        print len(self.sqlss)
    
    def sqlse(self ,event):
        print '--sqlse call'
        if not hasattr(self,'sqlss') or len(self.sqlss)==0:
            print '---- no has sqlss -'
            return
        if not hasattr(self,'iXX'):
            self.iXX= -1
        self.iXX  = (self.iXX +1) % len(self.sqlss)
        __1,be,en= self.sqlss[self.iXX]
        print be,en
        self.stcSQLs.SetSelection(be,en)

    def x11(self, event, S=False):
        st = self.stcSQLs.GetSelectedText()
        if S:
            st = st.encode(self.str_encode)
        print "SQL:",type(st),st
        db2db = self.get_db2db_from_connect_string(self.choiceConnectedDbnames.GetStringSelection(),False)
        db2db.cs.execute(st)
        va = db2db.cs.fetchall()
        print "LEN", len(va)
        pass
    def x12(self, event):
        self.x11(event, True)
        pass
    
