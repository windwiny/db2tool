#coding=gbk

''' Save current node directory and db directory to recreate batch file
'''

import os,sys

os.system('db2level')
msg = raw_input('\n Run db2 command success ? (Yes/No) : ')
if msg.upper() != 'YES':
    sys.exit(0)

fnode='node'
fdb='dbe'
fbat='refdb2.bat'

bat = open(fbat,'w')
m1 = ' db2 list node directory > %s \n' % fnode
m2 = ' db2 list db   directory > %s \n' % fdb
bat.write('rem # '+m1)
bat.write('rem # '+m2)

if not (os.path.isfile(fnode) and os.path.isfile(fdb) and sys.argv[-1].upper().strip() =='RN'):
    os.system(m1)
    os.system(m2)
else:
    print 'use old file ',fnode,fdb

f=open(fnode,'r').readlines()
for i in range(len(f)):
    s=f[i].split('=')
    if len(s)==2:
        mss = s[0].split()[0]
        if mss.find('节点名') != -1 or mss.upper().find('NODE NAME') != -1:
            nn=f[i].split('=')[1].split()[0]
            ip=f[i+4].split('=')[1].split()[0]
            po=f[i+5].split('=')[1].split()[0]
            msg = 'db2 catalog tcpip node \t%s \tremote \t%s \tserver \t%s \n' % ( nn, ip , po )
            bat.write(msg.expandtabs(16))

f=open(fdb,'r').readlines()
for i in range(len(f)):
    s=f[i].split('=')
    if len(s)==2:
        mss = s[0].split()[0]
        if mss.find('别名') != -1 or mss.upper().find(' ALIAS')  != -1:
            al=f[i].split('=')[1].split()[0]
            db=f[i+1].split('=')[1].split()[0]

            loc = f[i+2].split('=')[1].strip()
            if loc and loc[-1]==':':
                nd=f[i+2].split('=')[1].split()[0]
                msg = 'db2 catalog db \t%s \tas \t%s \ton \t%s \n' % ( db, al , nd[:2] )
                bat.write(msg.expandtabs(12))
            else:
                nd=f[i+2].split('=')[1].split()[0]
                msg = 'db2 catalog db \t%s \tas \t%s \tat node \t%s \n' % ( db, al , nd )
                bat.write(msg.expandtabs(12))


bat.close()
