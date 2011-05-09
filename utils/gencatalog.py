import os, sys


def main ():
    ls = open('list.txt','r').readlines()
    f2 = open('list2.txt','wb')
    nodes = {}
    dbs = []
    for l in ls:
        if not l :continue
        ll = l.split(',')
        nodes[ll[0]]=ll[1]
        aln,dbn = ll[2].replace('[','').replace(']','').split(' ')
        dbs.append((ll[1],aln,dbn))
    for node in nodes.keys():
        txt = 'db2 catalog tcpip node %s remote %s server %s'
        ip,port = node.split(':')
        txt = txt % (nodes[node], ip, port)
        f2.write(txt + '\n')
    f2.write('\n')

    for db in dbs:
        node,aln,dbn = db
        txt = 'db2 catalog db %s as %s at node %s'
        txt = txt % (dbn, aln, node)
        f2.write(txt + '\n')
    f2.write('\n')
    f2.write('db2 terminate\n')
    f2.write('\n')

if __name__ == '__main__':
    main()
