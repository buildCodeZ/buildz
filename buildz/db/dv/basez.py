import sys
from .structz import ItDv
from buildz.db import tls
def sp(obj):
    return super(obj.__class__, obj)

pass
class SimpleDv(ItDv):
    # func to impl:
    def to_list(self, query_result):
        return []
    def sql_tables(self):
        return "select TABLE_NAME tableName,TABLE_COMMENT comemnt,TABLE_ROWS dataNums from information_schema.tables where table_schema='"+self.db+"'"
    def new_con(self):
        return None
    def new_cursor(self):
        return None
    def init(self, *argv, **maps):
        pass
    # func already impl
    def check_query(self, s):
        arr = s.split(" ")
        k = arr[0].strip().lower()
        rst = k not in "delete,insert,update,create,drop,commit".split(",")
        return rst
    def __init__(self, host, port, user, pwd, db, *argv, **maps):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.con = None
        self.cursor = None
        self.init(*argv, **maps)
    def begin(self):
        self.con = self.new_con()
        self.cursor = self.new_cursor()
    def close(self):
        self.cursor.close()
        self.con.close()
        self.cursor = None
        self.con = None
    def is_open(self):
        return self.cursor is not None
    def commit(self):
        self.cursor.close()
        self.con.commit()
        self.cursor = self.new_cursor()
    def refresh(self):
        self.cursor.close()
        self.cursor = self.new_cursor()
    def query(self, sql, vals=()):
        # return list, first row is key
        tmp = self.cursor.execute(sql, vals)
        #print("[TESTZ] exe:",tmp)
        rst = self.cursor.fetchall()
        return self.to_list(rst)
    def execute(self, sql, vals=()):
        tmp = self.cursor.execute(sql, vals)
        return tmp
    def insert_or_update(self, maps, table, keys = None):
        if type(maps)!=dict:
            maps = maps.__dict__
        if keys is None:
            keys = []
        if type(keys) not in (list, tuple):
            keys = [keys]
        update = False
        conds = ""
        if len(keys)>0:
            need_query = True
            conds = []
            for k in keys:
                if k not in maps:
                    need_query = False
                    break
                v = maps[k]
                if type(v)==str:
                    v = f"'{v}'"
                if v not is None:
                    cond = f"{k} = {v}"
                else:
                    cond = f"{k} is null"
                conds.append(cond)
            if need_query:
                conds = " and ".join(conds)
                sql_search = f"select count(*) from {table} where {conds}"
                rst = self.query(sql_search)[1][0]
                update = rst>0
        if update:
            keys = set(keys)
            kvs = [[k,tls.py2sql(v)] for k,v in maps.items() if k not in keys]
            sets = [f"{k}={v}"]
            sets = ",".join(sets)
            sql = f"update {table} set {sets} where {conds}"
        else:
            kvs = [k, tls.py2sql(v) for k,v in maps.items()]
            ks = ",".join([kv[0] for kv in kvs])
            vs = ",".join([kv[1] for kv in kvs])
            sql = f"insert into {table}({ks}) values({vs});"
        return self.execute(sql)

pass

# user|pwd@host:port/db
def fetch(args):
    """
        host[:port][/db][ user][ pwd]
        host:port/db user pwd
    """
    if type(args) == str:
        args = args.split(" ")
    url = args[0].strip()
    tmp = url.split("/")
    url = tmp[0]
    db = None
    if len(tmp)>1:
        db = tmp[1]
    tmp = url.split(":")
    if len(tmp)==2:
        host, port = tmp
        port = int(port)
    else:
        host = tmp[0]
        port = None
    user = None
    if len(args)>1:
        user = args[1]
        if user is not None:
            user = user.strip()
    pwd = None
    if len(args)>2:
        pwd = args[2]
        if pwd is not None:
            pwd = pwd.strip()
    return host, port, user, pwd, db

pass