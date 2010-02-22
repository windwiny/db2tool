
This software release under the GPL




On Windows(XP), the .exe execute file create by py2exe,
if you don't run this program, Please install python 2.6,
wxPython 2.8.10, IBM DB2 Client,  PyDB2 binary or PyDB2 source
and mingw32, and compile it.

On Linux(Ubuntu 9.10 x86), not test




-------------
python f:\ux\python26\Tools\i18n\pygettext.py mods\mainframe.py 
python utils\merge_po.py x messages.pot locale\zh_CN\LC_MESSAGES\db2tool.po locale\zh_CN\LC_MESSAGES\db2tool2
python f:\ux\python26\Tools\i18n\msgfmt.py locale\zh_CN\LC_MESSAGES\db2tool2.po
