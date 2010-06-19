#-*- coding:utf-8 -*-
'''
Created on 2010-1-7

@author: windwiny
'''

import os, sys
import sqlite3
import pickle
import locale
import zlib
import base64


class dbConfig():
    '''configure file use sqlite3 database
    '''

    def __init__(self, str_encode, fi=''):
        '''
        Constructor
        '''
        self.str_encode = str_encode
        self.conf_password = None
        if fi == '':
            if sys.path[-1].endswith('configd.sqlite3'):
                fi = sys.path[-1]
            else:
                fi = sys.path[0] + os.path.sep + 'configd.sqlite3' 
        fs = os.path.isfile(fi)
        self.__db1 = sqlite3.connect(fi)
        #self.__db1.row_factory = sqlite3.Row
        #self.__db1.text_factory = str
        self.__cs1 = self.__db1.cursor()
        if not fs:
            self.__init_db()
        pass

    def __decodess(self, msg):
        '''
        @param msg:
        @return: base decode --> decompress
        '''
        if not self.conf_password:
            return msg

        try:
            msg =  zlib.decompress(base64.b64decode(msg))
            return pickle.loads(msg)
        except Exception as _ee:
            return msg

    decodess = __decodess
    
    def __encodess(self, msg, replaceSingleQuote=True, convStr2Uni=True):
        '''
        @param msg: any type data
        @param replaceSingleQuote: default True
        @param convStr2Uni: default True
        @return: compress --> base encode --> and/or replace ' ''
        '''
        if not self.conf_password:
            return msg
        
        try:
            if type(msg) == type('') and convStr2Uni:
                try: msg = msg.decode(self.str_encode)
                except Exception as _ee:
                    pass
            strs = base64.b64encode(zlib.compress(pickle.dumps(msg,1)))
            if replaceSingleQuote:
                return strs.replace("'","''")
            else:
                return strs
        except Exception as _ee:
            return msg
        
    encodess = __encodess

    def snippet_table_select_1row(self, codetype, typestr, name):
        ''' EXEC: select $code from $tablename where type='$typestr' and name='$name'   and   FETCH 1
        @param codetype: value in ['sql', 'python', 'code']
        @param typestr:
        @param name:
        @return: value string or None
        '''
        assert codetype in ['sql', 'python', 'code']
        tablename = codetype + 'snippet'
        self.__execute('''select code from %s where type='%s' and name='%s' ''' % (tablename, 
                        self.__encodess(typestr), self.__encodess(name)))
        f = self.__cs1.fetchone()
        if f and len(f) > 0:
            val = self.__decodess(f[0])
            return val
        else:
            return None

    def snippet_table_delete(self, codetype, typestr, name, autocommit=True):
        ''' EXEC: delete from $table where type='$type' and name='$name'
        @param codetype: value in ['sql', 'python', 'code']
        @param typestr:
        @param name:
        @param autocommit:
        @return: 0 or rowcount
        '''
        assert codetype in ['sql', 'python', 'code']
        tablename = codetype + 'snippet'
        try:
            self.__cs1.execute('''delete from %s where type='%s' and name='%s' ''' % (tablename, 
                        self.__encodess(typestr), self.__encodess(name)))
            if autocommit: self.__db1.commit()
            return self.__cs1.rowcount
        except Exception as ee:
            print ee
            return 0

    def snippet_table_insert(self, codetype, typestr, name, code, autocommit=True):
        ''' EXEC: insert into $tablename (type,name,code) values ('$typestr', '$name', '$code' )
        @param codetype: value in ['sql', 'python', 'code']
        @param typestr:
        @param name:
        @param code:
        @param autocommit:
        @return: boolean
        '''
        assert codetype in ['sql', 'python', 'code']
        tablename = codetype + 'snippet'
        try:
            self.__cs1.execute('''insert into %s (type,name,code) values ('%s','%s','%s') ''' % (tablename, 
                        self.__encodess(typestr), self.__encodess(name), self.__encodess(code) ))
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False

    def snippet_table_select_all(self, codetype):
        '''
        @param codetype: value in ['sql', 'python', 'code']
        @return: types[], names[]
        '''
        assert codetype in ['sql', 'python', 'code']
        tablename = codetype + 'snippet'
        types, names = [], []
        self.__cs1.execute('''select type from %s group by type order by type''' % tablename)
        f = self.__cs1.fetchall()
        if len(f) > 0:
            for i in range(len(f)):
                types.append(self.__decodess(f[i][0]))
        types.sort()
        for i in range(len(types)):
            self.__cs1.execute('''select name from %s where type='%s' order by name''' % (tablename, self.__encodess(types[i])))
            d = self.__cs1.fetchall()
            nn = [self.__decodess(i[0]) for i in d]
            nn.sort()
            names.append(nn)
        return types, names

    def __gettreeitem(self, table, typestr, name):
        self.__cs1.execute('''select code from %s where type='%s' and name='%s'  ''' % (table, typestr.replace("'","''"), name.replace("'","''")))
        f = self.__cs1.fetchall()
        return (True, f[0])
        pass
    
    def nodes_table_reset(self, nodes, timestr, autocommit=True):
        '''
        @param nodes[]:  node, comment, local, procto, ip, port
        @param timestr:
        @param autocommit:
        '''
        assert type(nodes) == type([]) and len(nodes[0]) >= 6
        if len(nodes) > 0:
            self.delete_table('nodes', False)
            for i in nodes:
                self.nodes_table_insert(i[0], i[1], i[2], i[3], i[4], i[5], timestr, False)
            if autocommit: self.__db1.commit()
                
    def nodes_table_insert(self, node, comment, local, procto, ip, port, timestr, autocommit=True):
        ''' EXEC: insert into nodes values ('%s','%s','%s','%s','%s','%s','%s')
        @param node:
        @param comment:
        @param local:
        @param procto:
        @param ip:
        @param port:
        @param timestr:
        @param autocommit:
        @return: boolean
        '''
        try:
            self.__cs1.execute('''insert into nodes values ('%s','%s','%s','%s','%s','%s','%s') ''' % (
                 node, comment, local, procto, ip, port, timestr))
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False
        
    def dbs_table_reset(self, dbs, timestr, autocommit=True):
        '''
        @param dbs:
        @param timestr:
        @param autocommit:
        '''
        assert type(dbs) == type([]) and len(dbs[0]) >= 9
        if len(dbs) > 0:
            self.delete_table('dbs', False)
            for i in dbs:
                self.dbs_table_insert(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], timestr, False)
            if autocommit: self.__db1.commit()

    def dbs_table_insert(self, dsn, dbname1, node, level, comment, typestr, part, bip, bport, timestr, autocommit=True):
        '''
        @param dsn:
        @param dbname1:
        @param node:
        @param level:
        @param comment:
        @param type:
        @param part:
        @param bip:
        @param bport:
        @param timestr:
        @param autocommit:
        @return: boolean
        '''
        try:
            self.__cs1.execute('''insert into dbs values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') ''' % (
                 dsn, dbname1, node, level, comment, typestr, part, bip, bport, timestr))
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False
    
    def dbinfo_select(self):
        ''' COLUMNS: ip,node,dsn,uid,pwd,comment
        @return: dbs[], desc[] 
        '''
        self.__cs1.execute('''select
            'LOCAL'     IP,
            D.node     NODE,
            D.dsn || ' [' || D.dbname1 || ']' DSN,
            '' UID,
            '' PWD,
            '' COMMENT
            from dbs D
            where node not in (select node from nodes)
            order by DSN''')
        db1 = self.__cs1.fetchall()
        desc = self.__cs1.description
        self.__cs1.execute('''select
            N.ip || ':' || N.port    IP,
            D.node    NODE ,
            D.dsn || ' [' || D.dbname1 || ']' DSN,
            '' UID,
            '' PWD,
            '' COMMENT
            from nodes N,dbs D
            where D.node = N.node
            order by IP, D.NODE, DSN ''')
        db2 = self.__cs1.fetchall()
        dbs = []
        for i in range(len(db1)):
            db = [self.__decodess(db1[i][x]) for x in [0,1,2,3,4,5] ]
            dbs.append(db)
        for i in range(len(db2)):
            db = [self.__decodess(db2[i][x]) for x in [0,1,2,3,4,5] ]
            dbs.append(db)

        self.__cs1.execute('''select
            dsn, username, password, comment
            from userpass
            order by time desc''')
        du = self.__cs1.fetchall()
        for i in range(len(dbs)):
            for x in range(len(du)):
                if dbs[i][2] == self.__decodess(du[x][0]):
                    dbs[i][3] = self.__decodess(du[x][1])
                    dbs[i][4] = self.__decodess(du[x][2])
                    dbs[i][5] = self.__decodess(du[x][3])
                    break

        return dbs, desc

    def dbinfo_save(self, dbs, lstChd, timestr, autocommit=True):
        '''
        @param dbs:
        @param lstChd:
        @param timestr:
        @param autocommit:
        '''
        for i in lstChd:
            dsn,usern = dbs[i][2], dbs[i][3]
            passw,comm = dbs[i][4], dbs[i][5]
            if not usern: continue
            self.userpass_delete(dsn)
            self.userpass_insert(dsn, usern, passw, comm, timestr)
        if autocommit: self.__db1.commit()
        
    def userpass_delete(self, dsn, autocommit=True):
        ''' EXEC delete from userpass where dsn='$dsn'
        @param dsn:
        @param autocommit:
        @return: 'Error' or rowcount
        '''
        try:
            self.__cs1.execute('''delete from userpass where dsn='%s' ''' % self.__encodess(dsn))
            if autocommit: self.__db1.commit()
            return self.__cs1.rowcount
        except Exception as ee:
            print ee
            return 'Error'

    def userpass_insert(self, dsn, username, password, comment, timestr, autocommit=True):
        ''' EXEC: insert into userpass (dsn,username,password,comment,time) values 
            ('$dsn', '$username', '$password', '$comment', time.strftime()
        @param dsn:
        @param username:
        @param password:
        @param comment:
        @param timestr:
        @param autocommit:
        @return: boolean
        '''
        try:
            self.__cs1.execute('''insert into userpass (dsn,username,password,comment,time) values ('%s','%s','%s','%s','%s') ''' % \
                        (self.__encodess(dsn), self.__encodess(username), 
                        self.__encodess(password), self.__encodess(comment), timestr) )
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False
        
    def colsize_delete(self, tabname, colname, autocommit=True):
        ''' EXEC: delete from colsize where tabname='$tabname' and colname='$colname'
        @param tabname:
        @param colname:
        @param autocommit:
        @return: 'Error' or rowcount
        '''
        try:
            self.__cs1.execute('''delete from colsize where tabname='%s' and colname='%s' ''' % (
                                    self.__encodess(tabname), self.__encodess(colname)) )
            if autocommit: self.__db1.commit()
            return self.__cs1.rowcount
        except Exception as ee:
            print ee
            return 'Error'
        
    def colsize_insert(self, tabname, colname, size, autocommit=True):
        ''' EXEC: insert into colsize (tabname,colname,size) values ('$tabname','$colname',$size)
        @param tabname:
        @param colname:
        @param autocommit:
        @return: boolean
        '''
        try:
            tbn, cln = self.__encodess(tabname), self.__encodess(colname)
            self.__cs1.execute('''delete from colsize where tabname='%s' and colname='%s' ''' % (
                                    tbn, cln) )
            self.__cs1.execute('''insert into colsize (tabname,colname,size) values ('%s','%s',%d)  ''' % (
                                    tbn, cln, size) )
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False
        
    def colsize_select(self, tabname):
        ''' EXEC: select colname,size from colsize where tabname='$tabname' 
        @param tabname:
        @return: colnames, sizes
        '''
        try:
            self.__cs1.execute('''select colname,size from colsize where tabname='%s' ''' % self.__encodess(tabname))
            f = self.__cs1.fetchall()
            cl = [self.__decodess(i[0]) for i in f]
            sz = [i[1] for i in f]
            return cl, sz
        except Exception as ee:
            print ee
            return [], []
    
    # ------------------------------------------------------------------------
    def delete_table(self, tablename, autocommit=True):
        ''' EXEC: delete from $tablename
        @param tablename:
        @param autocommit:
        @return: 'Error' or rowcount
        '''
        try:
            self.__cs1.execute('''delete from %s ''' % tablename )
            if autocommit: self.__db1.commit()
            return self.__cs1.rowcount
        except Exception as ee:
            print ee
            return 'Error'

    def select(self, sql, fetchAll=None):
        ''' Execute SELECT statement
        @param sql:
        @param fetchAll:
        @return: raise Exception or fetchmany or False
        '''
        if sql.lstrip()[:6].upper() != 'SELECT':
            raise Exception("Error: No select statement")
        dss = []
        try:
            self.__cs1.execute(sql)
            if fetchAll == True or fetchAll is None:
                ds = self.__cs1.fetchall()
            else:
                try:
                    n = int(fetchAll)
                    ds = self.__cs1.fetchmany(n)
                except Exception as _ee:
                    ds = self.__cs1.fetchall()
            for i in range(len(ds)):
                l = []
                for j in range(len(ds[i])):
                    l.append(self.__decodess(ds[i][j]) )
                dss.append(l)
        except Exception as ee:
            print ee
        finally:
            dss.sort()
            return dss

    def get_config(self, keystr, defaultvalue):
        '''
        @param keystr:
        @param defaultvalue:
        @return: unicode or other ( not type('') )
        '''
        try:
            self.__cs1.execute('''select value from config where key='%s' ''' % self.__encodess(keystr))
            f = self.__cs1.fetchone()
            if f:
                val = self.__decodess(f[0])
                ty = type(defaultvalue)
                if type(val) != ty and ty != type(''):
                    return ty(val)
                else:
                    return val
            else:
                return defaultvalue
        except Exception as ee:
            print ee
            return defaultvalue

    def save_config(self, keystr, value, autocommit=True):
        '''
        @param keystr: if type('') conv to unicode
        @param value: if type('') conv to unicode
        @param autocommit: default True
        '''
        try:
            self.__cs1.execute('''delete from config where key='%s' ''' % self.__encodess(keystr))
            self.__cs1.execute('''insert into config (key, value) values ('%s','%s') ''' % 
                    (self.__encodess(keystr), self.__encodess(value)))
            if autocommit: self.__db1.commit()
            return True
        except Exception as ee:
            print ee
            return False
        
    # ------------------------------------------------------------------------
    # -- other --
    def close(self):
#        self.__db1.commit()
        self.__cs1.close()
        self.__db1.close()

    def __execute(self, sql):
        try:
            self.__cs1.execute(sql)
        except sqlite3.Error as ee:
            print str(ee)
        except Exception as ee:
            print str(ee)
        
    def __init_db(self):
        sqls = [
            """create table config (key, value) """,
            """create table nodes(node,comment,local,procto,ip,port,time ) """,
            """create table dbs (dsn,dbname1,node,level,comment,type,part,bip,bport,time) """,
            """create table userpass (dsn,dbname1,username,password,comment,time) """,
            """create table sqlsnippet (type, name, code) """,
            """create table codesnippet (type, name, code) """,
            """create table pythonsnippet (type, name, code) """,
            """create table colsize (tabname, colname, size) """,
        ]
        for sql in sqls:
            self.__cs1.execute(sql)
        self.__db1.commit()
        pass

    def get_last_cs_description(self):
        return self.__cs1.description

    def getcs(self):
        return self.__cs1

    def __fetchall(self):
        return self.__cs1.fetchall()

    def __fetchmany(self, i):
        return self.__cs1.fetchmany(i)

    def __fetchone(self):
        return self.__cs1.fetchone()
        
    def commit(self):
        self.__db1.commit()
        
    def rollback(self):
        self.__db1.rollback()


