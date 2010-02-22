select  D.node,N.local || ' : ' || N.procto ,  N.ip || ':' || N.port, D.dsn || ' [' || D.dbname1 || ']' 
from nodes N,dbs D
where D.node = N.node
order by D.node, D.dsn




select  D.node NODE ,N.local || ' : ' || N.procto TT ,  N.ip || ':' || N.port IPPORT, D.dsn || ' [' || D.dbname1 || ']' DBINFO
from nodes N,dbs D
where D.node = N.node
order by D.node, D.dsn

select D.node,  '' TT, '' IPPORT,  D.dsn || ' [' || D.dbname1 || ']' DBINFO
from dbs D
where node not in (select node from nodes) 