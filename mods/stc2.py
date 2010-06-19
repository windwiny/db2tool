#-*- coding:utf-8 -*-
'''
Created on 2010-1-22

@author:   copy from PyCrust
'''
__author__ = ""
__cvsid__ = "$Id:  $"
__revision__ = "$Revision: 2010 $"[11:-2]

import wx
from wx import stc

import os
import sys
import time



kwlist_unknow = []

kwlist_python = [
#--start keywords--
        'and',
        'as',
        'assert',
        'break',
        'class',
        'continue',
        'def',
        'del',
        'elif',
        'else',
        'except',
        'exec',
        'finally',
        'for',
        'from',
        'global',
        'if',
        'import',
        'in',
        'is',
        'lambda',
        'not',
        'or',
        'pass',
        'print',
        'raise',
        'return',
        'try',
        'while',
        'with',
        'yield',
#--end keywords--
        ]

kwlist_sql_db2 = [
        'select','from','where','group','order','by','asc','desc','fetch','row','rows','only',
        'case','on','union','left','right','join','between','as','like','distinct',
        'have','in','default',
        'insert','into','values',
        'update','set',
        'delete',
        'commit','rollback',
        'and','or','not','is','null',
        'create','drop','alter','add','table','primary','key','column','describe',
        'tablespace','bufferpool','index','view','function','trigger',
        'procedure','user','mapping','summary',
        'drda','server','nickname','options','remote_authid','remote_password',
        'wrapper','type','version','authorization','password',
        'db2_fenced','DB2','UDB','dbname',
        'foreach','do','end','for',
        'connect','to','disconnect','using',
        'export','import','load','of','backup','restore',
        ]

kwlist2_sql = [
        'OOO','XXX','GGG'
        ]

if os.name == 'nt':
    FACES = { 'times'     : 'Times New Roman',
              'mono'      : 'Courier New',
              'helv'      : 'Arial',
              'lucida'    : 'Lucida Console',
              'other'     : 'Comic Sans MS',
              'size'      : 10,
              'lnsize'    : 8,
              'backcol'   : '#FFFFFF',
              'calltipbg' : '#FFFFB8',
              'calltipfg' : '#404040',
            }
else:
    FACES = { 'times'     : 'Times',
              'mono'      : 'Courier',
              'helv'      : 'Helvetica',
              'other'     : 'new century schoolbook',
              'size'      : 12,
              'lnsize'    : 10,
              'backcol'   : '#FFFFFF',
              'calltipbg' : '#FFFFB8',
              'calltipfg' : '#404040',
            }

class EditWindow(stc.StyledTextCtrl):
    """EditWindow based on StyledTextCtrl."""

    revision = __revision__

#    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
#                 size=wx.DefaultSize, style=wx.CLIP_CHILDREN | wx.SUNKEN_BORDER, name=''):
    def __init__(self, parent, id, pos, size, style, name, typestr, kwlist=None):
        """Create EditWindow instance."""
        stc.StyledTextCtrl.__init__(self, parent, id, pos, size, style, name)
        self.typestr = str(typestr).upper()
        print ' new stc %s:%s' % (name, self.typestr)
        if kwlist is None:
            if self.typestr == 'SQL':
                self.kwlist = kwlist_sql_db2
            elif self.typestr == 'PYTHON':
                self.kwlist = kwlist_python
            else:
                self.kwlist = kwlist_unknow
        else:
            self.kwlist = kwlist
        self.__config()
        stc.EVT_STC_UPDATEUI(self, id, self.OnUpdateUI)

    def _fontsizer(self, signal):
        """Receiver for Font* signals."""
        size = self.GetZoom()
        if signal == 'FontIncrease':
            size += 1
        elif signal == 'FontDecrease':
            size -= 1
        elif signal == 'FontDefault':
            size = 0
        self.SetZoom(size)


    def __config(self):
        self.setDisplayLineNumbers(True)
        
        if self.typestr == 'SQL':
            self.SetLexer(stc.STC_LEX_SQL)
        elif self.typestr == 'PYTHON':
            self.SetLexer(stc.STC_LEX_PYTHON)
        else:
            pass
        self.SetKeyWords(0, ' '.join(self.kwlist))

        self.setStyles(FACES)
        self.SetViewWhiteSpace(False)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        # Do we want to automatically pop up command completion options?
        self.autoComplete = True
        self.autoCompleteIncludeMagic = True
        self.autoCompleteIncludeSingle = True
        self.autoCompleteIncludeDouble = True
        self.autoCompleteCaseInsensitive = True
        self.AutoCompSetIgnoreCase(self.autoCompleteCaseInsensitive)
        self.autoCompleteAutoHide = False
        self.AutoCompSetAutoHide(self.autoCompleteAutoHide)
        self.AutoCompStops(' .,;:([)]}\'"\\<>%^&+-=*/|`')
        # Do we want to automatically pop up command argument help?
        self.autoCallTip = True
        self.callTipInsert = True
        self.CallTipSetBackground(FACES['calltipbg'])
        self.CallTipSetForeground(FACES['calltipfg'])

        self.SetWrapMode(False)
        try:
            self.SetEndAtLastLine(False)
        except AttributeError:
            pass
        self.SetCaretForeground(wx.Colour(255,0,0))
        self.SetCaretWidth(10)
        self.SetCaretPeriod(200)
        self.SetCaretLineBackground(wx.Colour(0,255,255))
        self.SetCaretLineBackAlpha(20)
        self.SetCaretLineVisible(True)

    def setDisplayLineNumbers(self, state):
        self.lineNumbers = state
        if state:
            self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
            self.SetMarginWidth(1, 38)
        else:
            # Leave a small margin so the feature hidden lines marker can be seen
            self.SetMarginType(1, 0)
            self.SetMarginWidth(1, 6)
        
    def setStyles(self, faces):
        self.setStyles_common(faces)

        if self.typestr == 'SQL':
            self.setStyles_sql(faces)
        elif self.typestr == 'PYTHON':
            self.setStyles_python(faces)
        else:
            pass
        
    def setStyles_common(self, faces):
        """Configure font size, typeface and color for lexer."""

        # Default style
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d,back:%(backcol)s" % faces)

        self.StyleClearAll()
        self.SetSelForeground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
        self.SetSelBackground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        # Built in styles
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(mono)s,size:%(lnsize)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#0000FF,back:#FFFF88")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#FF0000,back:#FFFF88")

    def setStyles_sql(self, faces):
        # sql styles
        self.StyleSetSpec(stc.STC_SQL_DEFAULT, "face:%(mono)s" % faces)     # DEFAULT
        self.StyleSetSpec(stc.STC_SQL_IDENTIFIER, "face:%(mono)s" % faces)  # TABNEME

        self.StyleSetSpec(stc.STC_SQL_STRING, "fore:#FF007F,face:%(mono)s" % faces)     # "..." """..."""
        self.StyleSetSpec(stc.STC_SQL_CHARACTER, "fore:#DD0000,face:%(mono)s" % faces)  # '...' '''...'''
        self.StyleSetSpec(stc.STC_SQL_QUOTEDIDENTIFIER, "fore:#0000FF")
        self.StyleSetSpec(stc.STC_SQL_WORD, "fore:#0000FF,bold")        # setKeyWords
        self.StyleSetSpec(stc.STC_SQL_WORD2, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_SQL_USER1, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_SQL_USER2, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_SQL_USER3, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_SQL_USER4, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_SQL_SQLPLUS, "fore:#ff0000,bold")
        self.StyleSetSpec(stc.STC_SQL_SQLPLUS_COMMENT, "back:#ffff00")
        self.StyleSetSpec(stc.STC_SQL_SQLPLUS_PROMPT, "back:#00ff00")
        
        self.StyleSetSpec(stc.STC_SQL_NUMBER, "fore:#FF00FF")           # 01234567890.+-e
        self.StyleSetSpec(stc.STC_SQL_OPERATOR, "fore:#0000FF")         # + - * / % = ! ^ & . , ; <> () [] {}
        
        self.StyleSetSpec(stc.STC_SQL_COMMENTLINE, "back:#AAFFAA")      # --...
        self.StyleSetSpec(stc.STC_SQL_COMMENTLINEDOC, "back:#FF0000")   # #...
        self.StyleSetSpec(stc.STC_SQL_COMMENT, "back:#AAFFAA")          # /*...*/
        self.StyleSetSpec(stc.STC_SQL_COMMENTDOC, "back:#AAFFAA")
        self.StyleSetSpec(stc.STC_SQL_COMMENTDOCKEYWORD, "back:#AAFFAA")
        self.StyleSetSpec(stc.STC_SQL_COMMENTDOCKEYWORDERROR, "back:#AAFFAA")

    def setStyles_python(self, faces):
        # python styles
        self.StyleSetSpec(stc.STC_P_DEFAULT, "face:%(mono)s" % faces)
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, "back:#AAFFAA")
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "back:#AAFFAA")

        self.StyleSetSpec(stc.STC_P_NUMBER, "")
        self.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,face:%(mono)s" % faces)
        self.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(mono)s" % faces)
        self.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold")
        self.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000")
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#000033,back:#FFFFE8")
        self.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:#0000FF,bold")
        self.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold")
        self.StyleSetSpec(stc.STC_P_OPERATOR, "")
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, "")
        self.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eolfilled" % faces)

    def OnUpdateUI(self, event):
        """Check for matching braces."""
        # If the auto-complete window is up let it do its thing.
        if self.AutoCompActive() or self.CallTipActive():
            return
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # Check before.
        if charBefore and chr(charBefore) in '[]{}()' \
        and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # Check after.
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in '[]{}()' \
            and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def CanCopy(self):
        """Return True if text is selected and can be copied."""
        return self.GetSelectionStart() != self.GetSelectionEnd()

    def CanCut(self):
        """Return True if text is selected and can be cut."""
        return self.CanCopy() and self.CanEdit()

    def CanEdit(self):
        """Return True if editing should succeed."""
        return not self.GetReadOnly()

    def CanPaste(self):
        """Return True if pasting should succeed."""
        return stc.StyledTextCtrl.CanPaste(self) and self.CanEdit()


    def GetLastPosition(self):
        return self.GetLength()

    def GetRange(self, start, end):
        return self.GetTextRange(start, end)

    def GetSelection(self):
        return self.GetAnchor(), self.GetCurrentPos()

    def ShowPosition(self, pos):
        line = self.LineFromPosition(pos)
        #self.EnsureVisible(line)
        self.GotoLine(line)

    def DoFindNext(self, findData, findDlg=None):
        backward = not (findData.GetFlags() & wx.FR_DOWN)
        matchcase = (findData.GetFlags() & wx.FR_MATCHCASE) != 0
        end = self.GetLastPosition()
        textstring = self.GetRange(0, end)
        findstring = findData.GetFindString()
        if not matchcase:
            textstring = textstring.lower()
            findstring = findstring.lower()
        if backward:
            start = self.GetSelection()[0]
            loc = textstring.rfind(findstring, 0, start)
        else:
            start = self.GetSelection()[1]
            loc = textstring.find(findstring, start)

        # if it wasn't found then restart at begining
        if loc == -1 and start != 0:
            if backward:
                start = end
                loc = textstring.rfind(findstring, 0, start)
            else:
                start = 0
                loc = textstring.find(findstring, start)

        # was it still not found?
        if loc == -1:
            dlg = wx.MessageDialog(self, 'Unable to find the search text.',
                          'Not found!',
                          wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        if findDlg:
            if loc == -1:
                wx.CallAfter(findDlg.SetFocus)
                return
            else:
                findDlg.Close()

        # show and select the found text
        self.ShowPosition(loc)
        self.SetSelection(loc, loc + len(findstring))

    # ---- compatible textCtrl method ----
    def GetStringSelection(self):
        return self.GetSelectedText()

    def GetValue(self):
        return self.GetText()

    def SetValue(self, text):
        return self.SetText(text)

    def SetMaxLength(self, max):
        return True

    def SetFont(self, ff):
        return True

    def SetEditable(self, sset):
        return self.SetReadOnly(not sset)

    def SetInsertPosinion(self, pos):
        return self.ShowPosition(pos)

    def ClearAll(self):
        rere = self.GetReadOnly()
        if rere:self.SetReadOnly(False)
        super(EditWindow,self).ClearAll()
        if rere:self.SetReadOnly(True)

    def AppendText(self, text):
        rere = self.GetReadOnly()
        if rere:self.SetReadOnly(False)
        super(EditWindow,self).AppendText(text)
        if rere:self.SetReadOnly(True)
