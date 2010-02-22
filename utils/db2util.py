#-*- coding:utf-8 -*-

"""Utilities for use with DB2 and the Python DB2 interface."""

__author__ = "Patrick K. O'Brien <pobrien@orbtech.com>"
__cvsid__ = "$Id: db2util.py,v 1.2 2002/12/04 00:38:09 pobrien Exp $"
__revision__ = "$Revision: 1.2 $"[11:-2]


import DB2


SQLTYPES = (
    'SQL_BIGINT',
    'SQL_BINARY',
    'SQL_BLOB',
    'SQL_BLOB_LOCATOR',
    'SQL_CHAR',
    'SQL_CLOB',
    'SQL_CLOB_LOCATOR',
    'SQL_TYPE_DATE',
    'SQL_DBCLOB',
    'SQL_DBCLOB_LOCATOR',
    'SQL_DECIMAL',
    'SQL_DOUBLE',
    'SQL_FLOAT',
    'SQL_GRAPHIC',
    'SQL_INTEGER',
    'SQL_LONGVARCHAR',
    'SQL_LONGVARBINARY',
    'SQL_LONGVARGRAPHIC',
    'SQL_NUMERIC',
    'SQL_REAL',
    'SQL_SMALLINT',
    'SQL_TYPE_TIME',
    'SQL_TYPE_TIMESTAMP',
    'SQL_VARCHAR',
    'SQL_VARBINARY',
    'SQL_VARGRAPHIC',
    )

BINARYTYPES = (
    'SQL_BLOB', 
    'SQL_BLOB_LOCATOR', 
    'SQL_CLOB', 
    'SQL_CLOB_LOCATOR', 
    'SQL_DBCLOB', 
    'SQL_DBCLOB_LOCATOR', 
    'SQL_GRAPHIC', 
    'SQL_LONGVARBINARY', 
    'SQL_LONGVARGRAPHIC', 
    'SQL_VARBINARY', 
    'SQL_VARGRAPHIC'
    )


def connect(dsn='sample', uid='db2inst1', pwd='ibmdb2', 
            autocommit=True, connecttype=1):
    """Return connection to DB2."""
    conn = DB2.connect(dsn, uid, pwd, autocommit, connecttype)
    return conn

def fp(cursor, sep=' ', null=''):
    """Fetch and print all rows returned by cursor.

    cursor is a database cursor
    sep is the column separator (default is one space)
    null is the representation for a NULL value (default is an empty string)
    """
    rows = cursor.fetchall()
    cprint(cursor, rows, sep, null)

def cprint(cursor, rows, sep=' ', null=None):
    """Print rows returned by cursor in a columnar format.

    cursor is a database cursor
    rows is a list of tuples returned by cursor.fetch*
    sep is the column separator (default is one space)
    null is the representation for a NULL value (default is None)
    """
    columns = cursor.description2
    if not columns:
        return '*** NO QUERY WAS EXECUTED ***'
    headers = getheaders(columns, sep)
    # Format the rows.
    dataformats = getdataformats(columns)
    textformats = gettextformats(columns)
    rows = [formatrow(row, dataformats, textformats, sep, null) for row in rows]
    # Print the final formatted text.
    print "\n".join(headers + rows)

def getheaders(columns, sep):
    """Return list of headers for columnar display."""
    nameheader = getnameheader(columns, sep)
    # Dashes will separate the names from the values.
    dashheader = getdashheader(columns, sep)
    headers = [nameheader, dashheader]
    return headers

def getnameheader(columns, sep):
    """Return name header."""
    names = getnames(columns)
    textformats = gettextformats(columns)
    textformat = sep.join(textformats)
    header = textformat % tuple(names)
    return header

def getdashheader(columns, sep):
    """Return dash header."""
    dashes = getdashes(columns)
    textformats = gettextformats(columns)
    textformat = sep.join(textformats)
    header = textformat % tuple(dashes)
    return header

def getnames(columns):
    """Return list of names for columns"""
    names = [column[0] for column in columns]
    return names

def getdashes(columns):
    """Return list of dashes for columnar display."""
    sizes = getdisplaysizes(columns)
    dashes = ['-' * size for size in sizes]
    return dashes

def getdisplaysizes(columns):
    """Return list of display sizes required for columns."""
    sizes = [getdisplaysize(column) for column in columns]
    return sizes

def getdisplaysize(column):
    """Return display size required for column."""
    name, type, displaysize, internalsize, precision, scale, nullokay = column
    size = max(len(name), displaysize)
    if type in BINARYTYPES:
        if type in ('SQL_DBCLOB', 'SQL_DBCLOB_LOCATOR'):
            size = max(len(name), len('<DBCLOB>'))
        else:
            size = max(len(name), len('<?LOB>'))
    return size

def gettextformats(columns):
    """Return list of text format strings for columns."""
    sizes = getdisplaysizes(columns)
    textformats = ['%%-%ss' % size for size in sizes]
    return textformats

def getdataformats(columns):
    """Return list of data format strings for columns."""
    dataformats = [getdataformat(column) for column in columns]
    return dataformats

def getdataformat(column):
    """Return data format string for column."""
    name, type, displaysize, internalsize, precision, scale, nullokay = column
    size = getdisplaysize(column)
    if type in ('SQL_DECIMAL', 'SQL_DOUBLE', 'SQL_FLOAT', 'SQL_NUMERIC', 'SQL_REAL'):
        format = '%%%s.%sf' % (size, scale)
    elif type in ('SQL_BIGINT', 'SQL_INTEGER', 'SQL_SMALLINT'):
        format = '%%%si' % (size)
    elif type in BINARYTYPES:
        format = '%%-%sr' % (size)
    else:
        format = '%%-%ss' % (size)
    return format

def formatrow(row, dataformats, textformats, sep, null=None):
    """Return row as formatted string, taking into account NULL values."""
    row = list(row)
    formats = []
    for n in range(len(row)):
        if row[n] is None:
            if null is not None:
                row[n] = null
            formats.append(textformats[n])
        else:
            formats.append(dataformats[n])
    format = sep.join(formats)
    row = format % tuple(row)
    return row
